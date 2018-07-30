import hashlib
import binascii
from typing import AnyStr


class BTCBlock(dict):

    block_dt_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, block_dct: dict):
        super().__init__(block_dct)

    def __repr__(self):
        return f"hash={self.hash}; height={self.height}"

    def __getattr__(self, item):
        return super().__getitem__(item)

    def __setattr__(self, key, value):
        super().__setitem__(key, value)

    @classmethod
    def int2hex(cls, num: int, padding: int=8) -> str:
        """
        Converts integer to its string hexadecimal representation.
        """
        return f"{num:#0{padding}x}"

    @classmethod
    def swap_endianess(cls, h: str) -> str:
        """
        Byte order swap.

        Check this great article if curious:
        https://betterexplained.com/articles/understanding-big-and-little-endian-byte-order/
        """
        if h[:2] == "0x":
            h = h[2:]  # If the hash starts with "0x", remove it
        return "".join([h[i:i + 2] for i in range(len(h), -1, -2)])

    @classmethod
    def ascii_encode(cls, string: str) -> bytes:
        return string.encode("ascii")

    @classmethod
    def unhexlify(cls, x: AnyStr) -> bytes:
        return binascii.unhexlify(x)

    def prepare_and_concat_header(self):
        a = self.ascii_encode(self.swap_endianess(self.int2hex(self.version)))
        b = self.ascii_encode(self.swap_endianess(self.previousblockhash))
        c = self.ascii_encode(self.swap_endianess(self.merkleroot))
        d = self.ascii_encode(self.swap_endianess(self.int2hex(self.time)))
        e = self.ascii_encode(self.swap_endianess(self.bits))
        f = self.ascii_encode(self.swap_endianess(self.int2hex(self.nonce)))
        return a + b + c + d + e + f

    @classmethod
    def get_merkle_root(cls, hash_list, n=2):
        """
        Recursively calculates Merkle root of all transaction hashes
        in parameter 'hash_list'. Returns Merkle root hash.
        """
        if len(hash_list) == 1:
            return hash_list[0]
        new_hash_list = []
        for i in range(0, len(hash_list), n):
            pair = hash_list[i:i + n]
            if len(pair) == 1:
                pair = [pair[0], pair[0]]

            new_hash_list.append(
                cls.merkle_swap_concat_hash(
                    *pair
                )
            )
        return cls.get_merkle_root(new_hash_list)

    @classmethod
    def double_sha256(cls, x: bytes) -> str:
        """
         Hash parameter 'x' twice with sha256 and return in hex.
        """
        first = hashlib.sha256(x).digest()
        second = hashlib.sha256(first).hexdigest()
        return second

    @classmethod
    def merkle_swap_concat_hash(cls, a: str, b: str) -> str:
        """
        1. swap endianes for both hashes
        2. unhexlify both hashes
        3. concatenate unhexlifued a and b
        4. hash with sha256
        5. hash with sha256
        6. swap endianes for obtained hexdigest

        :param a: transaction hash a
        :param b: transaction hash b
        :return: result hash
        """
        return cls.swap_endianess(
            cls.double_sha256(
                    cls.unhexlify(cls.swap_endianess(a))
                    +
                    cls.unhexlify(cls.swap_endianess(b))
            )
        )

    def verify_block_header(self):
        prepared = self.prepare_and_concat_header()
        double_hashed = self.double_sha256(self.unhexlify(prepared))
        return self.swap_endianess(double_hashed) == self.hash

    def verify_merkleroot(self):
        return self.get_merkle_root(self.tx) == self.merkleroot

    def verify(self):
        return {
            "merkleroot": self.verify_merkleroot(),
            "block_hash (block header)": self.verify_block_header()
        }
