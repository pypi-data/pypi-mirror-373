from typing import Any, Generator
from cobweb.base import (
    Seed,
    BaseItem,
    Request,
    Response,
    CSVItem,
)


class Crawler:

    @staticmethod
    def request(seed: Seed) -> Generator[Request, Response, None]:
        yield Request(seed.url, seed, timeout=5)

    @staticmethod
    def download(item: Request) -> Generator[Response, Any, None]:
        response = item.download()
        yield Response(item.seed, response, **item.to_dict)

    @staticmethod
    def parse(item: Response) -> Generator[BaseItem, Any, None]:
        upload_item = item.to_dict
        upload_item["content"] = getattr(item.response, "text", item.response)
        yield CSVItem(item.seed, data=upload_item)

