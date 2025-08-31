from rich.console import Console
console = Console()
from typing import Any, Dict, Optional
import time

from pydantic import PrivateAttr

from jaygoga_orchestra.v1.memory.memory import Memory
from jaygoga_orchestra.v1.memory.short_term.short_term_memory_item import ShortTermMemoryItem
from jaygoga_orchestra.v1.memory.storage.rag_storage import RAGStorage
from jaygoga_orchestra.v1.utilities.events.jaygoga_orchestra.v1_event_bus import jaygoga_orchestra.v1_event_bus
from jaygoga_orchestra.v1.utilities.events.memory_events import (
    MemoryQueryStartedEvent,
    MemoryQueryCompletedEvent,
    MemoryQueryFailedEvent,
    MemorySaveStartedEvent,
    MemorySaveCompletedEvent,
    MemorySaveFailedEvent,
)


class ShortTermMemory(Memory):
    """
    ShortTermMemory class for managing transient data related to immediate tasks
    and interactions.
    Inherits from the Memory class and utilizes an instance of a class that
    adheres to the Storage for data storage, specifically working with
    MemoryItem instances.
    """

    _memory_provider: Optional[str] = PrivateAttr()

    def __init__(self, squad=None, embedder_config=None, storage=None, path=None):
        memory_provider = embedder_config.get("provider") if embedder_config else None
        if memory_provider == "mem0":
            try:
                from jaygoga_orchestra.v1.memory.storage.mem0_storage import Mem0Storage
            except ImportError:
                raise ImportError(
                    "Mem0 is not installed. Please install it with `pip install mem0ai`."
                )
            config = embedder_config.get("config") if embedder_config else None
            storage = Mem0Storage(type="short_term", squad=squad, config=config)
        else:
            storage = (
                storage
                if storage
                else RAGStorage(
                    type="short_term",
                    embedder_config=embedder_config,
                    squad=squad,
                    path=path,
                )
            )
        super().__init__(storage=storage)
        self._memory_provider = memory_provider

    def save(
        self,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        jaygoga_orchestra.v1_event_bus.emit(
            self,
            event=MemorySaveStartedEvent(
                value=value,
                metadata=metadata,
                source_type="short_term_memory",
                from_agent=self.agent,
                from_task=self.task,
            ),
        )

        start_time = time.time()
        try:
            item = ShortTermMemoryItem(
                data=value,
                metadata=metadata,
                agent=self.agent.role if self.agent else None,
            )
            if self._memory_provider == "mem0":
                item.data = (
                    f"Remember the following insights from Agent run: {item.data}"
                )

            super().save(value=item.data, metadata=item.metadata)

            jaygoga_orchestra.v1_event_bus.emit(
                self,
                event=MemorySaveCompletedEvent(
                    value=value,
                    metadata=metadata,
                    # agent_role=agent,
                    save_time_ms=(time.time() - start_time) * 1000,
                    source_type="short_term_memory",
                    from_agent=self.agent,
                    from_task=self.task,
                ),
            )
        except Exception as e:
            jaygoga_orchestra.v1_event_bus.emit(
                self,
                event=MemorySaveFailedEvent(
                    value=value,
                    metadata=metadata,
                    error=str(e),
                    source_type="short_term_memory",
                    from_agent=self.agent,
                    from_task=self.task,
                ),
            )
            raise

    def search(
        self,
        query: str,
        limit: int = 3,
        score_threshold: float = 0.35,
    ):
        jaygoga_orchestra.v1_event_bus.emit(
            self,
            event=MemoryQueryStartedEvent(
                query=query,
                limit=limit,
                score_threshold=score_threshold,
                source_type="short_term_memory",
                from_agent=self.agent,
                from_task=self.task,
            ),
        )

        start_time = time.time()
        try:
            results = self.storage.search(
                query=query, limit=limit, score_threshold=score_threshold
            )  # type: ignore # BUG? The reference is to the parent class, but the parent class does not have this parameters

            jaygoga_orchestra.v1_event_bus.emit(
                self,
                event=MemoryQueryCompletedEvent(
                    query=query,
                    results=results,
                    limit=limit,
                    score_threshold=score_threshold,
                    query_time_ms=(time.time() - start_time) * 1000,
                    source_type="short_term_memory",
                    from_agent=self.agent,
                    from_task=self.task,
                ),
            )

            return results
        except Exception as e:
            jaygoga_orchestra.v1_event_bus.emit(
                self,
                event=MemoryQueryFailedEvent(
                    query=query,
                    limit=limit,
                    score_threshold=score_threshold,
                    error=str(e),
                    source_type="short_term_memory",
                ),
            )
            raise

    def reset(self) -> None:
        try:
            self.storage.reset()
        except Exception as e:
            raise Exception(
                f"An error occurred while resetting the short-term memory: {e}"
            )
