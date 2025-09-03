"""Main script for the Caesar cipher application."""

import sys

from caesar_pompey.utils import cipher

# pragma: no cover


def main():
    """Implement main loop of caesar ciphering application."""
    sentence = sys.argv[1]
    ciphered = ""
    for char in sentence:
        ciphered = ciphered + str(cipher(char, 1))
    print(ciphered)


if __name__ == "__main__":
    main()
