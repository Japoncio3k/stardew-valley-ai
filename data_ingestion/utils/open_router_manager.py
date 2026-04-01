import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from data_ingestion.utils.print_with_timestamp import print_with_timestamp


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class OpenRouterManager:
    index: int = 0
    keys: list[str]
    enrichment_llm: ChatOpenAI
    llm_model: str = "x-ai/grok-4-fast"
    # llm_model: str = "openai/gpt-oss-20b:free"
    base_url: str = "https://openrouter.ai/api/v1"

    def __init__(self):
        load_dotenv()
        self.keys = os.environ.get("OPEN_ROUTER_KEYS").split(",")
        os.environ["OPENAI_API_KEY"] = self.keys[self.index]
        self.index = 0
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0,
            base_url=self.base_url,
        )

    def set_next_key(self):
        self.index += 1
        os.environ["OPENAI_API_KEY"] = self.keys[self.index]
        print_with_timestamp("Switched to next OpenRouter key")
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=0,
            base_url=self.base_url,
        )
