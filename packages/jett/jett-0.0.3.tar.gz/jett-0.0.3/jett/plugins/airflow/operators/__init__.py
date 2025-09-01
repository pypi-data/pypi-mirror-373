import json
import logging
from collections.abc import Sequence
from typing import Any

from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context
from yaml import safe_load

from jett.tools import Tool

logger = logging.getLogger("jett")


class JettOperator(BaseOperator):
    """Jett Airflow Operator object."""

    template_fields: Sequence[str] = ("tool",)
    template_ext: Sequence[str] = (".tool",)

    ui_color: str = "#eb52b3"

    def __init__(self, tool: str, **kwargs) -> None:
        """Main initialize method."""
        super().__init__(**kwargs)
        self.tool: str = tool

    def execute(self, context: Context) -> Any:
        """Execute Jett tool."""
        logger.info("Debug context:")
        logger.info(f"{json.dumps(dict(context), default=str, indent=2)}")
        logger.info(f"Start run jett: {self.tool}")
        tool_data: dict[str, Any] = safe_load(self.tool)
        tool = Tool(config=tool_data)
        tool.execute()
