

from flask import current_app

def split_flatten_and_join(arr, k=3, separator=","):
    current_app.logger.info("About to split format and join arrays")
    """
    Splits each sub-array of arr into chunks of size k if its length is greater than k,
    and then joins all elements of each chunk into a single string.

    Args:
    - arr (list of list): A 2D array.
    - k (int): The maximum size of each chunk.
    - separator (str): The separator used when joining elements of each chunk into a string.

    Returns:
    - list: A list of strings, each representing a chunk of elements.
    """
    chunked_strings = []
    for sub_arr in arr:
        for i in range(0, len(sub_arr), k):
            chunk = sub_arr[i:i + k]
            chunk_string = separator.join(map(str, chunk))
            chunked_strings.append(chunk_string)

    return chunked_strings