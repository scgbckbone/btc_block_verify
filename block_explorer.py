import requests
from exceptions import IncorrectDataProvidedError
from json import JSONDecodeError


class BlockExpolerQuery(object):
    BE_url_base = "https://blockexplorer.com"
    by_height_uri = "/api/block-index/{}"  # format block height
    by_hash_uri = "/api/block/{}"  # format block hash

    @staticmethod
    def _query_(url: str) -> dict:
        try:
            return requests.get(url=url).json()
        except JSONDecodeError as e:
            print(e.msg)

    @classmethod
    def retrieve_block(cls, data):
        if isinstance(data, int):
            return cls.retrieve_block_by_block_height(block_height=data)
        elif isinstance(data, str):
            return cls.retrieve_block_by_block_hash(block_hash=data)
        else:
            raise IncorrectDataProvidedError(
                "Parameter data has to be string (block hash) or integer "
                f"(block height) - not {type(data)}"
            )

    @classmethod
    def retrieve_block_by_block_hash(cls, block_hash):
        return requests.get(
            f"{cls.BE_url_base}{cls.by_hash_uri.format(block_hash)}"
        ).json()

    @classmethod
    def retrieve_block_by_block_height(cls, block_height):
        block_hash = requests.get(
            f"{cls.BE_url_base}{cls.by_height_uri.format(block_height)}"
        ).json()["blockHash"]

        return cls.retrieve_block_by_block_hash(block_hash=block_hash)
