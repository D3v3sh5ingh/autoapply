from typing import Tuple, Dict
from sentence_transformers import SentenceTransformer, util
from .base import BaseMatcher
from ..database.models import Job, Profile

import os
import certifi

class SemanticMatcher(BaseMatcher):
    def __init__(self):
        super().__init__()
        self.model = None
        # SSL Certificate path is handled globally in dashboard.py
        # but we print it here for confirmation
        cert_path = os.environ.get('REQUESTS_CA_BUNDLE', certifi.where())
        print(f"Loading Semantic Model with certs at: {cert_path}")
        
        # Load a efficient, small model suitable for local CPU
        print(f"Loading Semantic Model (all-MiniLM-L6-v2) with certs at: {cert_path}")
        try:
            # multiple fallback options for model loading could go here
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"FAILED TO LOAD AI MODEL: {e}")
            # We will handle self.model being None in the match method
            pass

    def match(self, job: Job, profile: Profile) -> Tuple[float, Dict]:
        if not self.model:
            return 0.0, {"error": "AI Model not loaded (SSL/Network issue)"}

        # Prepare texts
        # For profile, we use resume text if available, else concatenated skills
        profile_text = profile.resume_text or " ".join(profile.skills or [])
        
        # For job, title is matching weight x2, description x1
        job_text = f"{job.title}. {job.description or ''}"
        
        # Compute embeddings
        # In production, cache profile embedding!
        embeddings1 = self.model.encode(profile_text, convert_to_tensor=True)
        embeddings2 = self.model.encode(job_text, convert_to_tensor=True)
        
        # Cosine similarity
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        score_float = float(cosine_scores[0][0]) * 100.0
        
        # Heuristic boost for title exact match
        if any(s.lower() in job.title.lower() for s in (profile.skills or [])):
            score_float += 10.0
            
        return min(round(score_float, 2), 100.0), {"type": "semantic", "raw_score": score_float}
