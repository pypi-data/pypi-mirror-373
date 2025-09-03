"""
Custom BaseNN encoder implementation.

The encoder works the similar way as a Base64 or similar encoders but it can use non-standard
input alphabet for encoding input integer values. The main usage is to shorten long numeric IDs.
"""
__all__ = [
    "encode",
]


def encode(number, alphabet, length):
    """
    :param number: an input integer number to encode
    :param alphabet: an input encoding alphabet
    :param length: the output length of the encoded string
    :return:
    """
    result = ""
    alphabet_length = len(alphabet)
    for _ in range(length):
        reminder = number % alphabet_length
        result += alphabet[reminder]
        number //= alphabet_length

    return result
