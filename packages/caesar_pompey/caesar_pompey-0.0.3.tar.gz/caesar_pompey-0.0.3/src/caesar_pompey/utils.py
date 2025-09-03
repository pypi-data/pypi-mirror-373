"""Example."""

UPPERCASE_SENTENCE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWERCASE_SENTENCE = "abcdefghijklmnopqrstuvwxyz"
INTEGER_SENTENCE = "0123456789"


def create_dict_and_invert(sentence):
    """Create a dictionary mapping each character to its index and the inverse.

    param sentence: string of characters to create the dictionary from
    return: a list containing the dictionary and its inverse
    """
    ret = {}
    for char in sentence:
        ret[char] = len(ret)
    inv_ret = {v: k for k, v in ret.items()}
    return [ret, inv_ret]


def cipher(char, move):
    """Cipher a character by moving it.

    param char: character to cipher
    param move: number of positions to move the character
    return: the ciphered character
    """
    [upper, inv_upper] = create_dict_and_invert(UPPERCASE_SENTENCE)
    [lower, inv_lower] = create_dict_and_invert(LOWERCASE_SENTENCE)
    [integers, inv_integers] = create_dict_and_invert(INTEGER_SENTENCE)

    if char in upper:
        newindex = (upper[char] + move) % 26
        return inv_upper[newindex]
    if char in lower:
        newindex = (lower[char] + move) % 26
        return inv_lower[newindex]
    if char in integers:
        newindex = (integers[char] + move) % 10
        return inv_integers[newindex]
    return char
