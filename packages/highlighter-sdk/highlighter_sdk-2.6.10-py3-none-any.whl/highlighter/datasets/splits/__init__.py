from .random_split import RandomSplitter

SUPPORTED_SPLIT_FNS = {RandomSplitter.__name__: RandomSplitter}


def get_split_fn(name):
    return SUPPORTED_SPLIT_FNS[name]
