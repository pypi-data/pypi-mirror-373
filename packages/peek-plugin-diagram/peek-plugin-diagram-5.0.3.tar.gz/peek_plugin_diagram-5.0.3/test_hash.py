from datetime import datetime

import pytz
import json

x = {
    "_tt": "DGP",
    "bi": 1145,
    "bs": 1,
    "g": [0.3205018616, 0.1532438682],
    "hs": 1.0,
    # "id": 21078830,
    "la": 1,
    "le": 735,
    "r": 0,
    "s": True,
    "tn": "update me",
    "vs": 1.0,
}

startTime = datetime.now(pytz.utc)
unique = set()

import string

ALPHABET = (
    string.ascii_uppercase + string.ascii_lowercase + string.digits + "-_"
)
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)
SIGN_CHARACTER = "$"


def num_encode(n):
    if n < 0:
        return SIGN_CHARACTER + num_encode(-n)
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0:
            break
    return "".join(reversed(s))


def num_decode(s):
    if s[0] == SIGN_CHARACTER:
        return -num_decode(s[1:])
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n


for num in range(100):
    x["g"][0] += num
    x["g"][1] += num
    p = hash(json.dumps(x))
    # print(str(p))
    unique.add(p)

    print(str(p))
    print(num_encode(p))

print("Values = %s" % len(unique))
print("Taken %s", (datetime.now(pytz.utc) - startTime))
