from multiprocessing import Pool

from tqdm import tqdm


def process_bulk(params, function, multiplier):
    with Pool(multiplier) as p:
        list(tqdm(p.imap_unordered(function, params), total=len(params)))


def process_single(params, function):
    list(map(function, tqdm(params)))
