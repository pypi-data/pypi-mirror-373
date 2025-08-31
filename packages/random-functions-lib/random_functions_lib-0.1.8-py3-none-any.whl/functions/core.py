import random
def encode(string,key):
    result = ""
    for i,char in enumerate(string):
        result += format(ord(char) ^ ord(key[i % len(key)]), "02x")
    return result


def decode(encoded_string, key):
    key_len = len(key)
    decoded = ""
    for i in range(0, len(encoded_string), 2):
        byte = int(encoded_string[i:i + 2], 16)
        decoded += chr(byte ^ ord(key[(i // 2) % key_len]))
    return decoded


def invert_caps(string):
    cap_invert = {}
    result = ""
    letters = "abcdefghijklmnopqrstuvwxyz"
    for letter in letters:
        cap_invert[letter]=letter.upper()
    for letter in letters:
        cap_invert[letter.upper()]=letter
    for letter in string:
        result += cap_invert[letter]
    return result


def reverse(string):
    index = len(string)-1
    result = ""
    while index >= 0:
        result += string[index]
        index -= 1
    return result


def scramble(string):
    positions = []
    new_positions = {}
    result = ""
    for position in range(len(string)):
        positions.append(position)
    for letter in string:
        choice = random.choice(positions)
        new_positions[choice]=letter
        positions.remove(choice)
    for number in range(len(string)):
        result+=new_positions[number]
    return result


def flip_a_coin():
    heads_or_tails = random.randint(1,2,)
    if heads_or_tails == 1:
        return "heads"
    else:
        return "tails"


def shout(string):
    result = ""
    for letter in string:
        result += letter.upper()
    result += "!!!"
    return result


def binary(text: str) -> str:
    return " ".join(format(ord(c), "08b") for c in text)

