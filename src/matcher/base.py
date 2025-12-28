from abc import ABC, abstractmethod
from typing import Tuple, Dict
from ..database.models import Job, Profile

class BaseMatcher(ABC):
    @abstractmethod
    def match(self, job: Job, profile: Profile) -> Tuple[float, Dict]:
        """
        Calculates a match score between a job and a profile.
        Returns:
            - score (float): 0.0 to 100.0
            - details (dict): Metadata about the match (e.g., matched keywords)
        """
        pass
