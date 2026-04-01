from pydantic import BaseModel, ConfigDict
from unstructured.documents.elements import Element as UnstructuredElement


class PageData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    urls: list[str]
    chunks: list[UnstructuredElement]
