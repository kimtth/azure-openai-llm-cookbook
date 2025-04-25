# This model defines the clinical trial data schema which is used both for persisting trial details
# and for correlating with the output from the multi-agent analysis system.
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TrialPhase(str, Enum):
    PHASE_1 = "Phase 1"
    PHASE_2 = "Phase 2"
    PHASE_3 = "Phase 3"
    PHASE_4 = "Phase 4"

class TrialStatus(str, Enum):
    PLANNED = "Planned"
    RECRUITING = "Recruiting"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    TERMINATED = "Terminated"

class ClinicalTrial(BaseModel):
    id: str
    drug_id: str
    phase: TrialPhase
    status: TrialStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    participants: int
    description: str
    results: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "CT001",
                "drug_id": "DRUG001",
                "phase": "Phase 1",
                "status": "Active",
                "start_date": "2024-01-01T00:00:00",
                "participants": 100,
                "description": "Safety study of new drug candidate"
            }
        }
