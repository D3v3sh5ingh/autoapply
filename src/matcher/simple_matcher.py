from typing import Tuple, Dict, Set
from .base import BaseMatcher
from ..database.models import Job, Profile

class KeywordMatcher(BaseMatcher):
    def match(self, job: Job, profile: Profile) -> Tuple[float, Dict]:
        if not profile.skills or not isinstance(profile.skills, list):
            return 0.0, {"error": "No skills in profile"}

        text_to_search = (job.title + " " + (job.description or "")).lower()
        
        matched_skills = []
        total_skills = len(profile.skills)
        
        if total_skills == 0:
            return 0.0, {}

        for skill in profile.skills:
            if skill.lower() in text_to_search:
                matched_skills.append(skill)
        
        # Simple score: percentage of profile skills found in job
        score = (len(matched_skills) / total_skills) * 100.0
        
        # Boost score if title matches a skill (heuristic)
        title_skills = [s for s in matched_skills if s.lower() in job.title.lower()]
        if title_skills:
            score = min(100.0, score * 1.2)

        return round(score, 2), {
            "matched_keywords": matched_skills,
            "missing_keywords": [s for s in profile.skills if s not in matched_skills]
        }
