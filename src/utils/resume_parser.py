import pdfplumber
import re
from typing import List, Dict

class ResumeParser:
    def __init__(self):
        pass

    def parse_file(self, file_obj) -> Dict:
        """
        Parses a file-like object (PDF) and extracts text and basic skills.
        """
        text = ""
        try:
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            return {"error": f"Failed to read PDF: {e}", "text": ""}

        # Basic cleanup
        text = text.replace("\x00", "") 
        
        return {
            "text": text,
            "skills": self._extract_skills(text), # Heuristic
            "email": self._extract_email(text)
        }

    def _extract_email(self, text: str) -> str:
        email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        return email.group(0) if email else ""

    def _extract_skills(self, text: str) -> List[str]:
        # A simple list of common tech skills to look for. 
        # In a real app, this would be a large database or NLP model.
        common_skills = {
            "DATA": ["python", "sql", "spark", "pyspark", "pandas", "numpy", "aws", "snowflake", "kafka", "airflow", "etl", "big data"],
            "WEB": ["javascript", "react", "node", "html", "css", "django", "flask", "fastapi"],
            "TOOLS": ["git", "docker", "kubernetes", "jenkins", "jira", "linux"],
            "LANGUAGES": ["java", "c++", "scala", "go", "rust"]
        }
        
        found = set()
        text_lower = text.lower()
        
        for category, skills in common_skills.items():
            for skill in skills:
                # Regex for whole word match to avoid substring false positives (e.g. 'go' in 'google')
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found.add(skill) # Add the base skill name
                    
        return list(found)
