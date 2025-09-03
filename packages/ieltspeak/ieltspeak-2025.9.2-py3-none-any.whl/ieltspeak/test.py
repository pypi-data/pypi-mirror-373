from .data_loader import TopicDataLoader

data_loader = TopicDataLoader()

print(data_loader.get_topic('1','event'))
