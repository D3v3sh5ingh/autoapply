from src.database.models import Job, Profile
from src.matcher.simple_matcher import KeywordMatcher

def test_matching():
    # Setup dummy data
    profile = Profile(
        name="Dev User",
        skills=["Python", "SQL", "Selenium", "FastAPI", "React"]
    )
    
    job_good = Job(
        title="Senior Python Backend Engineer",
        description="We are looking for a Python expert with SQL and Selenium experience. FastAPI is a plus.",
        company="TechCorp"
    )
    
    job_bad = Job(
        title="Marketing Manager",
        description="Looking for SEO and Content Writing expert.",
        company="BizInc"
    )

    matcher = KeywordMatcher()
    
    print("MATCHING TEST")
    print("-" * 20)
    
    # Test Good Match
    score1, details1 = matcher.match(job_good, profile)
    print(f"Job: {job_good.title}")
    print(f"Score: {score1}")
    print(f"Details: {details1}")
    print("-" * 20)

    # Test Bad Match
    score2, details2 = matcher.match(job_bad, profile)
    print(f"Job: {job_bad.title}")
    print(f"Score: {score2}")
    print(f"Details: {details2}")

if __name__ == "__main__":
    test_matching()
