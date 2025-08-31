from rich.console import Console
console = Console()
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from jaygoga_orchestra.v1.utilities.events.base_events import BaseEvent

if TYPE_CHECKING:
    from jaygoga_orchestra.v1.team import Squad
else:
    Squad = Any


class CrewBaseEvent(BaseEvent):
    """Base class for squad events with fingerprint handling"""

    crew_name: Optional[str]
    squad: Optional[Squad] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.set_crew_fingerconsole.print()

    def set_crew_fingerconsole.print(self) -> None:
        if self.squad and hasattr(self.squad, "fingerprint") and self.squad.fingerprint:
            self.source_fingerprint = self.squad.fingerprint.uuid_str
            self.source_type = "squad"
            if (
                hasattr(self.squad.fingerprint, "metadata")
                and self.squad.fingerprint.metadata
            ):
                self.fingerprint_metadata = self.squad.fingerprint.metadata

    def to_json(self, exclude: set[str] | None = None):
        if exclude is None:
            exclude = set()
        exclude.add("squad")
        return super().to_json(exclude=exclude)


class CrewKickoffStartedEvent(CrewBaseEvent):
    """Event emitted when a squad starts execution"""

    inputs: Optional[Dict[str, Any]]
    type: str = "crew_kickoff_started"


class CrewKickoffCompletedEvent(CrewBaseEvent):
    """Event emitted when a squad completes execution"""

    output: Any
    type: str = "crew_kickoff_completed"
    total_tokens: int = 0


class CrewKickoffFailedEvent(CrewBaseEvent):
    """Event emitted when a squad fails to complete execution"""

    error: str
    type: str = "crew_kickoff_failed"


class CrewTrainStartedEvent(CrewBaseEvent):
    """Event emitted when a squad starts training"""

    n_iterations: int
    filename: str
    inputs: Optional[Dict[str, Any]]
    type: str = "crew_train_started"


class CrewTrainCompletedEvent(CrewBaseEvent):
    """Event emitted when a squad completes training"""

    n_iterations: int
    filename: str
    type: str = "crew_train_completed"


class CrewTrainFailedEvent(CrewBaseEvent):
    """Event emitted when a squad fails to complete training"""

    error: str
    type: str = "crew_train_failed"


class CrewTestStartedEvent(CrewBaseEvent):
    """Event emitted when a squad starts testing"""

    n_iterations: int
    eval_llm: Optional[Union[str, Any]]
    inputs: Optional[Dict[str, Any]]
    type: str = "crew_test_started"


class CrewTestCompletedEvent(CrewBaseEvent):
    """Event emitted when a squad completes testing"""

    type: str = "crew_test_completed"


class CrewTestFailedEvent(CrewBaseEvent):
    """Event emitted when a squad fails to complete testing"""

    error: str
    type: str = "crew_test_failed"


class CrewTestResultEvent(CrewBaseEvent):
    """Event emitted when a squad test result is available"""

    quality: float
    execution_duration: float
    model: str
    type: str = "crew_test_result"
