from typing import Annotated, Union

from pydantic import Field

from seekrai.types.agents.tools.schemas.file_search import FileSearch
from seekrai.types.agents.tools.schemas.run_python import RunPython
from seekrai.types.agents.tools.schemas.web_search import WebSearch


Tool = Annotated[Union[FileSearch, WebSearch, RunPython], Field(discriminator="name")]
