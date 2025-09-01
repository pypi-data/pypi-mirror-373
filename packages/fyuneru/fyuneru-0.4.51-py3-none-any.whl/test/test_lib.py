import pytest

from fyuneru.lib import hash


def test_hash():
    print("lib.hash")
    print(hash(b"", "blake3"))
    print(hash(b"123", "blake3"))
    print(hash(b"abc", "blake3"))
    print(len(hash(b"abc", "blake3")))
    print(len(hash(b"abcd", "blake3")))

    print(hash(b"abc", "md5"))
    # print(hash(b"abc", "sha1"))


test_hash()
