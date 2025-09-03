from typing import List, Optional

import orjson
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RunCommandResponse(BaseModel):
    """
    Pydantic schema for storing command execution results.
    """

    command: List[str] = Field(
        ..., description="The executed command with its arguments."
    )
    stdout: Optional[str] = Field(
        None, description="Standard output of the command."
    )
    stderr: Optional[str] = Field(
        None, description="Standard error output of the command."
    )
    returncode: int = Field(..., description="Exit code of the command.")
    user: str = Field(
        ..., description="The system user who executed the command."
    )
    execution_time: float = Field(
        ..., description="Time taken to execute the command (in seconds)."
    )

    # Auto-clean data with field validators
    @field_validator("stdout", "stderr")
    @classmethod
    def strip_whitespace(cls, value: str) -> Optional[str]:
        """Ensure stdout and stderr are stripped of excess whitespace or set to None if empty."""
        return value.strip() if value and value.strip() else None

    @field_validator("execution_time")
    @classmethod
    def round_execution_time(cls, value: float) -> float:
        """Round execution time to 4 decimal places for consistency."""
        return round(value, 4)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "command": ["ls", "-l"],
                "stdout": "file1.txt  file2.txt",
                "stderr": "",
                "returncode": 0,
                "user": "john_doe",
                "execution_time": 0.123,
            }
        }
    )

    def as_form_payload(self) -> dict:
        """Serialise the response into a dict suitable for multipart/form-data."""
        return {
            "command": orjson.dumps(self.command).decode("utf-8"),
            "stdout": self.stdout or "",
            "stderr": self.stderr or "",
            "returncode": str(self.returncode),
            "user": self.user,
            "execution_time": str(self.execution_time),
        }
