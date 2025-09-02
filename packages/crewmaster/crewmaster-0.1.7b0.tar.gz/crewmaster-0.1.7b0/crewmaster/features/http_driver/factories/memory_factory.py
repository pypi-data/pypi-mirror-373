from langgraph.checkpoint.memory import (
    MemorySaver,
    BaseCheckpointSaver,
)
from ...json_serializar_from_custom_models import (
    JsonSerializarFromCustomModels
)


def memory_factory() -> BaseCheckpointSaver:
    serde = JsonSerializarFromCustomModels(
        valid_namespaces=['crew_builder']
    )
    checkpointer = MemorySaver(
        serde=serde
    )
    return checkpointer
