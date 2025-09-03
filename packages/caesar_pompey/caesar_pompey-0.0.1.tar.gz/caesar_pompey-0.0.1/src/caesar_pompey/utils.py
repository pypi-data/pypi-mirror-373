"""Example."""

uppercasesentence = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lowercasesentence = "abcdefghijklmnopqrstuvwxyz"
integerssentence = "0123456789"


def CreateDictAndInvert(sentence):
    """Create a dictionary mapping each character to its index and the inverse.

    param sentence: string of characters to create the dictionary from
    return: a list containing the dictionary and its inverse
    """
    ret = dict()
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
    [upper, inv_upper] = CreateDictAndInvert(uppercasesentence)
    [lower, inv_lower] = CreateDictAndInvert(lowercasesentence)
    [integers, inv_integers] = CreateDictAndInvert(integerssentence)

    if char in upper:
        newindex = (upper[char] + move) % 26
        return inv_upper[newindex]
    elif char in lower:
        newindex = (lower[char] + move) % 26
        return inv_lower[newindex]
    elif char in integers:
        newindex = (integers[char] + move) % 10
        return inv_integers[newindex]
    return char
