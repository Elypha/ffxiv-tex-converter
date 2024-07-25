import gc
import os
from multiprocessing import Pool

from tqdm import tqdm
# from tqdm.contrib.concurrent import process_map


def _chunks(arr, size):
    """
    split an array into chunks
    :param arr: the array
    :param size: size of each chunk
    :return: yields one chunk of size `size` of `arr`
    """
    for i in range(0, len(arr), size):
        yield arr[i : i + size]


def process_bulk(params, function, multiplier):
    # core_count = os.cpu_count()
    core_count = 2
    with tqdm(total=len(params)) as pb:
        for chunk in _chunks(params, round(core_count * multiplier)):
            with Pool(core_count) as p:
                p.map(function, chunk)
                # gc.collect()
            pb.update(len(chunk))


def process_single(params, function):
    list(map(function, tqdm(params)))
