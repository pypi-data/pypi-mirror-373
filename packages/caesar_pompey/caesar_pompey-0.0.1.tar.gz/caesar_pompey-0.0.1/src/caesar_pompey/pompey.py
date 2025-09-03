"""Main script for the Pompey decipher application."""

import sys

from caesar_pompey.utils import cipher

# pragma: no cover


def main():
    """Implement main loop of pompey deciphering application."""
    sentence = sys.argv[1]
    ciphered = ""
    for char in sentence:
        ciphered = ciphered + str(cipher(char, -1))
    print(ciphered)


if __name__ == "__main__":
    main()
