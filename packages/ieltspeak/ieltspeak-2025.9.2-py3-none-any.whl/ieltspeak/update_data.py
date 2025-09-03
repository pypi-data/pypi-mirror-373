import httpx
import asyncio
import time
import itertools
import json
import re
from pathlib import Path

# 配置参数
CONFIG = {
    "base_url": "https://ielts-bro-proxy.duzhuo.icu/ielts-bro",
    "catalogs": ["人物", "事物", "事件", "地点"],
    "parts": ["0", "1"],
    "max_retries": 3,  # 最大重试次数
    "output_dir": "./data/",  # 输出目录
    "concurrency": 4,  # 并发请求数
}


class IELTSSpider:
    def __init__(self):
        # 创建输出目录 - 使用 pathlib
        output_path = Path(CONFIG["output_dir"])
        output_path.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_path

        # 初始化数据结构
        self.part1_data = {
            "part": 0,
            "part_name": "Part 1",
            "categories": ["event", "thing", "person", "location"],
            "data": {"event": [], "thing": [], "person": [], "location": []},
        }

        self.part2_3_data = {
            "part": 1,
            "part_name": "Part 2 & 3",
            "categories": ["event", "thing", "person", "location"],
            "data": {"event": [], "thing": [], "person": [], "location": []},
        }

        # Configure httpx client with connection limits
        limits = httpx.Limits(
            max_connections=CONFIG["concurrency"],
            max_keepalive_connections=CONFIG["concurrency"],
        )
        self.session = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30.0,
            limits=limits,
            proxy=None,
        )

    def is_valid_time_tag(self, time_tag):
        """检查timeTag是否为非大陆"""
        if not time_tag:
            return False

        # 匹配非大陆开头的字符串
        pattern = r"^非大陆.*"
        match = re.search(pattern, time_tag)
        return match is not None

    async def make_request(self, url, params=None, retry=0):
        """带重试机制的异步请求函数"""
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if retry < CONFIG["max_retries"]:
                print(f"请求失败，第 {retry+1} 次重试... (URL: {url})")
                await asyncio.sleep(2 * (retry + 1))  # 指数退避
                return await self.make_request(url, params, retry + 1)
            print(f"请求最终失败: {e} (URL: {url})")
            return None

    async def fetch_topic_list(self, catalog, part):
        """获取主题列表"""
        url = f"{CONFIG['base_url']}/topic-list"
        params = {"catalog": catalog, "part": part}
        print(f"正在获取主题列表: catalog={catalog}, part={part}")
        return await self.make_request(url, params)

    async def fetch_topic_detail(self, topic_id, part):
        """获取主题详情"""
        url = f"{CONFIG['base_url']}/topic-detail"
        params = {"topicID": topic_id, "part": part}
        return await self.make_request(url, params)

    def process_topic_list(self, catalog, part, topic_data):
        """处理主题列表数据"""
        if not topic_data or topic_data.get("status") != 0:
            print(f"获取主题列表失败或数据为空: catalog={catalog}, part={part}")
            return []

        if "content" not in topic_data or "list" not in topic_data["content"]:
            print(f"主题列表数据结构异常: catalog={catalog}, part={part}")
            return []

        category_map = {
            "人物": "person",
            "事物": "thing",
            "事件": "event",
            "地点": "location",
        }
        category_name = category_map.get(catalog)

        processed_topics = []
        for topic in topic_data["content"]["list"]:
            # 只处理非“非大陆”开头的timeTag
            if self.is_valid_time_tag(topic.get("timeTag")):
                print(
                    f"跳过非大陆主题: {topic.get('oralTopicName')} - {topic.get('timeTag')}"
                )
                continue

            processed_topic = {
                "topic_part": int(part),
                "topic_id": topic["oralTopicId"],
                "topic_name": topic["oralTopicName"],
                "preview_question": topic["oralQuestion"],
                "timeTag": topic["timeTag"],
            }
            processed_topics.append(processed_topic)
            print(f"添加主题: {topic['oralTopicName']} - {topic['timeTag']}")

        print(f"已处理 {len(processed_topics)} 个主题 (catalog={catalog}, part={part})")
        return processed_topics

    def process_topic_detail(self, detail_data, topic_part):
        """处理主题详情数据，提取问题列表"""
        if not detail_data or detail_data.get("status") != 0:
            print("获取主题详情失败或数据为空")
            return []

        if (
            "content" not in detail_data
            or "oralQuestionDetailVOList" not in detail_data["content"]
        ):
            print("主题详情数据结构异常")
            return []

        questions = []
        for detail in detail_data["content"]["oralQuestionDetailVOList"]:
            if "oralQuestion" in detail:
                # Part 1主题：包含所有Part 1问题
                if topic_part == 0 and detail.get("oralPart") == 1:
                    questions.append(detail["oralQuestion"])
                # Part 2&3主题：只包含Part 3问题，不包含Part 2描述题
                elif topic_part == 1 and detail.get("oralPart") == 3:
                    questions.append(detail["oralQuestion"])

        print(f"提取到 {len(questions)} 个问题")
        return questions

    def save_to_json(self):
        """保存数据到JSON文件"""
        # 使用 pathlib 构建文件路径
        part1_file = self.output_dir / "ielts_part0.json"
        part2_3_file = self.output_dir / "ielts_part1.json"

        with open(part1_file, "w", encoding="utf-8") as f:
            json.dump(self.part1_data, f, ensure_ascii=False, indent=2)
        print(f"已保存Part1数据到 {part1_file}")

        with open(part2_3_file, "w", encoding="utf-8") as f:
            json.dump(self.part2_3_data, f, ensure_ascii=False, indent=2)
        print(f"已保存Part2&3数据到 {part2_3_file}")

    async def run(self):
        """运行爬虫"""
        print("=" * 50)
        print("开始爬取雅思口语题目数据 (JSON输出版)")
        print(f"参数组合: catalogs={CONFIG['catalogs']}, parts={CONFIG['parts']}")
        print(f"并发数: {CONFIG['concurrency']}")
        print(f"输出目录: {CONFIG['output_dir']}")
        print("=" * 50)

        start_time = time.monotonic()

        # 1. Fetch all topic lists concurrently
        param_combinations = list(
            itertools.product(CONFIG["catalogs"], CONFIG["parts"])
        )
        list_tasks = [self.fetch_topic_list(c, p) for c, p in param_combinations]
        topic_lists_results = await asyncio.gather(*list_tasks)

        all_topics_to_fetch_details = []

        # 2. Process topic lists and collect all topics for detail fetching
        for (catalog, part), topic_list_data in zip(
            param_combinations, topic_lists_results
        ):
            processed_topics = self.process_topic_list(catalog, part, topic_list_data)

            # 按part分类存储
            category_map = {
                "人物": "person",
                "事物": "thing",
                "事件": "event",
                "地点": "location",
            }
            category_name = category_map.get(catalog)

            if part == "0":  # Part 1
                self.part1_data["data"][category_name].extend(processed_topics)
            else:  # Part 2 & 3
                self.part2_3_data["data"][category_name].extend(processed_topics)

            # 收集需要获取详情的主题
            for topic in processed_topics:
                all_topics_to_fetch_details.append((topic, part))

        print(
            f"\n共找到 {len(all_topics_to_fetch_details)} 个符合条件的主题, 开始获取详情..."
        )

        if not all_topics_to_fetch_details:
            print("没有找到符合条件的主题，程序结束")
            await self.session.aclose()
            return

        # 3. Fetch all topic details concurrently with semaphore
        semaphore = asyncio.Semaphore(CONFIG["concurrency"])
        detail_tasks = []

        async def fetch_with_semaphore(topic, part):
            async with semaphore:
                print(f"获取主题详情: {topic['topic_name']} (ID: {topic['topic_id']})")
                return await self.fetch_topic_detail(topic["topic_id"], part)

        for topic, part in all_topics_to_fetch_details:
            detail_tasks.append(fetch_with_semaphore(topic, part))

        detail_results = await asyncio.gather(*detail_tasks)

        print(f"\n获取详情完成, 开始处理详情数据...")

        # 4. Process all topic details and add questions to topics
        for (topic, part), detail_data in zip(
            all_topics_to_fetch_details, detail_results
        ):
            questions = self.process_topic_detail(detail_data, int(part))

            # 将问题添加到对应的主题中
            if part == "0":  # Part 1
                for category in self.part1_data["data"].values():
                    for t in category:
                        if t["topic_id"] == topic["topic_id"]:
                            t["questions"] = questions
                            break
            else:  # Part 2 & 3
                for category in self.part2_3_data["data"].values():
                    for t in category:
                        if t["topic_id"] == topic["topic_id"]:
                            t["questions"] = questions
                            break

        # 5. 清理不需要的字段
        self.clean_data()

        # 6. Save data to JSON files
        self.save_to_json()

        # Close resources
        await self.session.aclose()

        duration = time.monotonic() - start_time
        print("\n" + "=" * 50)
        print(f"爬取完成! 总耗时: {duration:.2f} 秒")
        print(
            f"Part1 主题数量: {sum(len(topics) for topics in self.part1_data['data'].values())}"
        )
        print(
            f"Part2&3 主题数量: {sum(len(topics) for topics in self.part2_3_data['data'].values())}"
        )
        print("=" * 50)

    def clean_data(self):
        """清理数据，移除不需要的字段"""
        for part_data in [self.part1_data, self.part2_3_data]:
            for category in part_data["data"].values():
                for topic in category:
                    # 移除timeTag字段
                    if "timeTag" in topic:
                        del topic["timeTag"]


if __name__ == "__main__":
    print("提示: 此脚本使用 httpx, 请确保已安装 (pip install 'httpx' 'httpx[http2]')")
    spider = IELTSSpider()
    asyncio.run(spider.run())
