from typing import Optional


class BuildPhase:
    def __init__(
        self,
        phase_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.phase_id = phase_id
        self.name = name
        self.description = description
        if not self.name:
            self.name = phase_id.replace("_", " ").capitalize()
        if not self.description:
            self.description = phase_id.replace("_", " ").capitalize()

    def __eq__(self, other):
        return (
            self.phase_id == other.phase_id
            and self.name == other.name
            and self.description == other.description
        )
