import importlib
from typing import Any, List, Optional
from langchain_core.load.load import Reviver
from langgraph.checkpoint.serde.jsonplus import (
    JsonPlusSerializer
)
import structlog

log = structlog.get_logger()
"Loger para el módulo"


LC_REVIVER = Reviver(
    valid_namespaces=['crew_builder']
)


class JsonSerializarFromCustomModels(JsonPlusSerializer):
    reviver: Reviver

    def __init__(
        self,
        *args,
        valid_namespaces: Optional[List[str]] = None,
        **kwargs
    ):
        self.reviver = Reviver(valid_namespaces=valid_namespaces)

    def _reviver(self, value: dict[str, Any]) -> Any:
        if (
            value.get("lc", None) == 2
            and value.get("type", None) == "constructor"
            and value.get("id", None) is not None
        ):
            # Get module and class name
            [*module, name] = value["id"]
            # Import module
            mod = importlib.import_module(".".join(module))
            # Import class
            cls = getattr(mod, name)
            # Instantiate class
            if value["method"] is not None:
                method = getattr(cls, value["method"])
                return method(*value["args"], **value["kwargs"])
            else:
                return cls(*value["args"], **value["kwargs"])

        return self.reviver(value)
