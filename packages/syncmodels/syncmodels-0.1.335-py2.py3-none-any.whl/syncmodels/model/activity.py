# kraken/model/activity.py
from datetime import datetime, timezone
from typing import Optional, Literal, Dict, Any
from uuid import UUID, uuid4
import hashlib
import pickle

from pydantic import BaseModel, Field, model_validator, validator, root_validator

from agptools.helpers import new_uid
from syncmodels.definitions import UID, KIND_KEY, PATH_KEY, ORG_URL
from syncmodels.model.model import Datetime

ActivityType = Literal["task", "particle", "orion_sync", "other"]
ActivityStatusValue = Literal[
    "pending", "running", "flushing", "completed", "failed", "cancelled"
]


BLUEPRINT_KEYS = [
    "activity_type",
]
BLUEPRINT_ARGUMENTS = [
    KIND_KEY,
    # ORG_URL,
    # PATH_KEY,
]


class ActivityStatus(BaseModel):
    """
    Represents the status and metadata of a running or completed activity
    within the Kraken system.
    """

    id: UID = Field(
        default_factory=new_uid,
        description="Unique identifier for this activity instance.",
    )
    # wave_timestamp: datetime = Field(
    #     ..., description="Timestamp of the 'wave' this activity belongs to."
    # )
    name: Optional[str] = Field(
        None,
        description="Descriptive name of the activity (e.g., expanded source identifier).",
    )
    activity_type: ActivityType = Field(..., description="Type of the activity.")
    arguments: Optional[Dict[str, Any]] = Field(
        ..., description="argument used for this activity"
    )
    status: ActivityStatusValue = Field(
        default="pending", description="Current status of the activity."
    )
    start_time: Optional[Datetime] = Field(
        None, description="Timestamp when the activity started."
    )
    update_time: Optional[Datetime] = Field(
        None, description="Timestamp when the activity finished (successfully or not)."
    )
    eta_time: Optional[Datetime] = Field(
        None, description="Timestamp when the activity is expected to finish."
    )
    duration_seconds: Optional[float] = Field(
        None, description="Calculated duration of the activity in seconds."
    )
    progress_percentage: Optional[float] = Field(
        None, description="Progress percentage (0-100), if applicable."
    )
    # details: Optional[Dict[str, Any]] = Field(
    #     None, description="Dictionary for additional details or error messages."
    # )
    details: Optional[str] = Field(
        "", description="Dictionary for additional details or error messages."
    )

    @model_validator(mode="before")
    @classmethod
    def compute_id_name(cls, data: Dict[str, Any]) -> Dict[str, Any]:

        # data["arguments"] = str({k: data[k] for k in set(BLUEPRINT_ARGUMENTS).intersection(data)})
        data["arguments"] = {
            k: data[k] for k in set(BLUEPRINT_ARGUMENTS).intersection(data)
        }
        blueprint = {
            k: data[k]
            for k in set(BLUEPRINT_KEYS + BLUEPRINT_ARGUMENTS).intersection(data)
        }
        blueprint = pickle.dumps(blueprint)
        blueprint = hashlib.md5(blueprint).hexdigest()
        data["id"] = blueprint

        data.setdefault("start_time", datetime.now(tz=timezone.utc))
        data.setdefault("progress_percentage", 0)
        # data.setdefault("details", {})
        return data

    # @validator("progress_percentage")
    # def check_progress_range(cls, v):
    #     if v is not None and not (0 <= v <= 100):
    #         raise ValueError("progress_percentage must be between 0 and 100")
    #     return v

    # @validator("end_time", always=True)
    # def calculate_duration(cls, v, values):
    #     start = values.get("start_time")
    #     if start and v:
    #         duration = (v - start).total_seconds()
    #         values["duration_seconds"] = round(duration, 3)
    #     else:
    #         values["duration_seconds"] = (
    #             None  # Ensure duration is None if start or end is missing
    #         )
    #     return v

    # class Config:
    #     # Example for generating schema
    #     json_schema_extra = {
    #         "example": {
    #             "activity_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    #             "wave_timestamp": "2025-04-11T10:00:00Z",
    #             "activity_type": "particle",
    #             "name": "aemet_fetch_obs_malaga",
    #             "status": "running",
    #             "start_time": "2025-04-11T10:05:15Z",
    #             "end_time": None,
    #             "duration_seconds": None,
    #             "progress_percentage": 25.5,
    #             "details": {"station_id": "6055B"},
    #         }
    #     }
