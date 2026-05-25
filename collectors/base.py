from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import requests
from config import REQUEST_TIMEOUT


@dataclass
class Article:
    title: str
    url: str
    source: str
    summary: str
    category: str  # paper / project / news / tool


class BaseCollector(ABC):
    name: str = "base"
    category: str = "news"

    @abstractmethod
    def collect(self) -> List[Article]:
        ...

    def _get(self, url: str, headers: dict = None) -> requests.Response:
        default_headers = {"User-Agent": "AI-News-Digest/1.0"}
        if headers:
            default_headers.update(headers)
        return requests.get(url, headers=default_headers, timeout=REQUEST_TIMEOUT)
