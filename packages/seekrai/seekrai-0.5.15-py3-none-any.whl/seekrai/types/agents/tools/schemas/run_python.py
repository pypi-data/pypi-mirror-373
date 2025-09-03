from typing import Literal

from seekrai.types.agents.tools.schemas.run_python_env import RunPythonEnv
from seekrai.types.agents.tools.tool import ToolBase, ToolType


class RunPython(ToolBase[RunPythonEnv]):
    name: Literal[ToolType.RUN_PYTHON] = ToolType.RUN_PYTHON
    tool_env: RunPythonEnv
