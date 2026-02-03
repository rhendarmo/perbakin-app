from datetime import date
from pydantic import BaseModel


class EligibilityResult(BaseModel):
    eligible: bool
    reasons: list[str]
    checked_at: date
    membership_valid: bool
    has_valid_license: bool
