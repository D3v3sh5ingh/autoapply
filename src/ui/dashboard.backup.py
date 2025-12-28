import os
import sys

# CRITICAL FIX: Force correct SSL Certificate path before any other imports
try:
    # 1. Check for standard Windows path (local dev)
    # 2. Check for standard Linux path (Docker)
    # 3. Check for certifi path via python
    import certifi
    cert_path = certifi.where()
    
    # Override for specific broken environments if necessary
    custom_win_path = r"C:\Python312\Lib\site-packages\certifi\cacert.pem"
    if os.path.exists(custom_win_path):
        cert_path = custom_win_path
        
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    os.environ['SSL_CERT_FILE'] = cert_path
except: 
    pass

import streamlit as st
import pandas as pd
from datetime import datetime
from src.scraper.mock_scraper import MockScraper
from src.scraper.hn_scraper import HNScraper
from src.scraper.instahyre_scraper import InstahyreScraper
from src.scraper.generic_scraper import GenericScraper
from src.scraper.arbeitnow_scraper import ArbeitnowScraper
from src.matcher.simple_matcher import KeywordMatcher
from src.utils.notifier import Notifier
from src.matcher.semantic_matcher import SemanticMatcher
from src.utils.resume_parser import ResumeParser
# ApplicationBot import moved inside function to prevent early import errors if selenium issues exist
from src.scraper.naukri_scraper import NaukriScraper
from src.scraper.linkedin_scraper import LinkedInScraper
from src.database.models import Job, Profile

# STREAMLIT PAGE CONFIG
st.set_page_config(page_title="AutoApply Dashboard", layout="wide")

# ... imports ...
from src.database.db import save_jobs, get_saved_jobs, mark_job_applied, init_db, delete_job, reset_db

# STREAMLIT PAGE CONFIG
st.set_page_config(page_title="AutoApply Dashboard", layout="wide")

def main():
    # Ensure DB tables exist on startup
    try:
        init_db()
    except Exception as e:
        print(f"DB Init Warning: {e}")

    st.title("🤖 JobPulse Agent")
    st.caption("Your Privacy-First AI Job Assistant (Scrape • Match • Track)")
    
    # TABS
    tab_search, tab_history, tab_analytics = st.tabs(["🔍 Search & Apply", "📊 History & Tracking", "📈 Analytics"])
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        with st.expander("👤 Profile & Resume", expanded=True):
            name = st.text_input("Name", "Devesh Singh")
            phone = st.text_input("Mobile Number", "9876543210")
            
            uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
            resume_text = ""
            resume_path = None
            
            if uploaded_file:
                try:
                    os.makedirs("temp", exist_ok=True)
                    resume_path = os.path.abspath(os.path.join("temp", uploaded_file.name))
                    with open(resume_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    parser = ResumeParser()
                    data = parser.parse_file(uploaded_file)
                    resume_text = data.get("text", "")
                    skills_from_resume = data.get("skills", [])
                    st.caption(f"✅ Parsed {len(skills_from_resume)} skills from PDF.")
                except Exception as e:
                    st.error(f"Resume Error: {e}")

            default_skills = "Python, SQL, PySpark, Snowflake, AWS"
            skills_input = st.text_area("Skills (comma separated)", default_skills)
            skills = [s.strip() for s in skills_input.split(",") if s.strip()]

        st.divider()
        
        st.subheader("🔎 Search Criteria")
        query = st.text_input("Job Role", "Data Engineer")
        location = st.text_input("Location", "Remote")
        if not location:
            st.warning("⚠️ Please enter a location (e.g., 'Remote', 'India')")
            
        search_limit = st.slider("Jobs per Source", 5, 30, 10)
        use_smart_search = st.checkbox("Smart Search (AI Query Expansion)", value=True)
        
        st.subheader("Sources")
        use_instahyre = st.checkbox("Instahyre", value=True)
        use_arbeitnow = st.checkbox("Arbeitnow (Remote)", value=True)
        use_naukri = st.checkbox("Naukri (Beta)", value=True)
        use_linkedin = st.checkbox("LinkedIn (Beta - Limited)", value=True)
        use_mock = st.checkbox("Mock Data (Testing)", value=False)
        use_hn = False 
        
        st.divider()
        st.subheader("🧠 Intelligence")
        use_semantic = st.toggle("Semantic Matching (AI)", value=True)
        
        st.divider()
        with st.expander("🔔 Email Alerts", expanded=False):
            email_enabled = st.checkbox("Enable Alerts", value=False)
            email_user = st.text_input("Email (Gmail/Outlook)", placeholder="you@gmail.com")
            email_pass = st.text_input("App Password", type="password")
            if email_enabled and email_user and email_pass:
                if st.button("Test Email Connection"):
                    notifier = Notifier(email_user, email_pass)
                    if notifier.send_alert(email_user, []): # Empty list just checks connection/logic
                         st.success("✅ Connection Successful!")
                    else:
                         st.error("❌ Connection Failed. Check App Password.")

        st.divider()
        if st.button("🚀 Find Jobs", type="primary"):
            run_search(query, location, skills, resume_text, resume_path, phone, use_mock, 
                       use_instahyre, use_hn, use_semantic, use_naukri, 
                       use_linkedin, use_smart_search, use_arbeitnow,
                       email_enabled, email_user, email_pass, search_limit)

    # --- TAB 1: SEARCH ---
    with tab_search:
        st.info("Configure your profile on the left and click 'Find Relevant Jobs'.")
        
        # DEBUG LOG DISPLAY
        if 'search_log' in st.session_state:
            with st.expander("🛠️ System Activity Logs", expanded=False):
                for log in st.session_state['search_log']:
                    if "❌" in log: st.error(log)
                    elif "✅" in log: st.success(log)
                    else: st.write(log)
        
        # RESULTS DISPLAY
        if 'results' in st.session_state:
            results = st.session_state['results']
            st.markdown(f"### Found {len(results)} Matches")
            
            # Batch Actions
            if st.button(f"⚡ Auto-Apply to Top 5 Matches"):
                run_batch_apply(results[:5], name, skills, resume_text)

            for job in results:
                # Card UI
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(f"{job.title} @ {job.company}")
                        tags = f"{job.location} | {job.source.upper()}"
                        if job.date_posted: tags += f" | {job.date_posted.strftime('%Y-%m-%d')}"
                        st.caption(tags)
                        st.write(job.description[:300] + "..." if job.description else "No description available.")
                        
                    with col2:
                        # Show Match Score if available
                        score = int(job.match_score) if job.match_score else 0
                        if score > 0:
                            st.metric("Match %", f"{score}%")
                        
                        st.link_button("View / Apply Manually", job.url)
                        
                        if st.button(f"Auto Apply 🤖", key=f"btn_{job.url}"):
                             run_single_apply(job, name, skills, resume_text)
                    st.divider()
    
    # --- TAB 2: HISTORY ---
    with tab_history:
        st.markdown("### 🗄️ Job Database")
        
        # Controls Row
        col_sort, col_filter, col_refresh = st.columns([2, 2, 1])
        
        saved = get_saved_jobs()
        
        # Extract unique locations for filter
        unique_locs = sorted(list(set([j.location for j in saved if j.location])))
        
        with col_filter:
            filter_loc = st.multiselect("Filter by Location:", unique_locs, default=[])
            
        with col_sort:
            sort_option = st.selectbox(
                "Sort Applications By:",
                ["Date Posted (Newest First)", "Date Posted (Oldest First)", "Match Score (Highest First)", "Match Score (Lowest First)"]
            )
            
            # Export
            if saved:
                export_df = pd.DataFrame([{
                    "Title": j.title, "Company": j.company, "Location": j.location, 
                    "Date Posted": j.date_posted, "Source": j.source, "URL": j.url, 
                    "Match Score": j.match_score, "Applied": "Yes" if j.applications else "No"
                } for j in saved])
                csv = export_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export CSV", csv, "job_history.csv", "text/csv")
            
        with col_refresh:
            st.write("") 
            st.write("")
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # RETENTION CONTROLS
        with st.expander("🧹 Maintenance & Retention", expanded=False):
            st.markdown("Remove jobs older than 30 days (keeping those you applied to).")
            if st.button("Run Cleanup Task"):
                try:
                    from src.database.db import clean_old_jobs
                    deleted = clean_old_jobs(days=30)
                    st.success(f"Cleanup Complete! Removed {deleted} old jobs.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Cleanup Failed: {e}")
            
            st.divider()
            st.markdown("**Danger Zone**")
            if st.button("🚨 RESET DATABASE (Delete All Data)", type="primary"):
                if reset_db():
                    st.success("Database has been reset. History cleared.")
                    st.rerun()
                else:
                    st.error("Failed to reset database.")

        # Apply Filters
        if filter_loc:
            saved = [j for j in saved if j.location in filter_loc]
            
        # Apply Sorting
        if "Date Posted (Newest" in sort_option:
            saved.sort(key=lambda x: x.date_posted or datetime.min, reverse=True)
        elif "Date Posted (Oldest" in sort_option:
            saved.sort(key=lambda x: x.date_posted or datetime.min, reverse=False)
        elif "Match Score (Highest" in sort_option:
            saved.sort(key=lambda x: x.match_score or 0, reverse=True)
        elif "Match Score (Lowest" in sort_option:
            saved.sort(key=lambda x: x.match_score or 0, reverse=False)

        st.write(f"Showing {len(saved)} Jobs")
        
        # Display as cards
        for job in saved:
            is_applied = len(job.applications) > 0
            
            with st.container():
                col1, col2 = st.columns([3.5, 1.5])
                with col1:
                    title_str = f"{job.title} @ {job.company}"
                    if is_applied:
                        title_str = "✅ " + title_str
                    st.subheader(title_str)
                    
                    tags = f"📍 {job.location} | 📅 {job.date_posted.strftime('%Y-%m-%d') if job.date_posted else 'N/A'} | 🔗 {job.source.upper()}"
                    st.caption(tags)
                    
                    if is_applied:
                        app = job.applications[0]
                        st.success(f"Applied on {app.date_applied.strftime('%Y-%m-%d')} ({app.status})")
                    
                with col2:
                    # Match Score
                    score = int(job.match_score) if job.match_score else 0
                    if score > 0:
                        st.metric("Match %", f"{score}%")
                    
                    st.link_button("📄 View Job", job.url)
                    
                    if not is_applied:
                        c1, c2, c3 = st.columns([1, 1, 0.5])
                        with c1:
                            if st.button("🤖 Auto Apply", key=f"auto_{job.id}"):
                                run_single_apply(job, name, skills, resume_text)
                                st.rerun()
                        with c2:
                            if st.button("✅ Mark Done", key=f"manual_{job.id}", help="Mark as applied manually"):
                                mark_job_applied(job.id, status="manual")
                                st.toast(f"Marked {job.company} as Applied!")
                                st.rerun()
                        with c3:
                            if st.button("🗑️", key=f"del_{job.id}", help="Delete this job"):
                                delete_job(job.id)
                                st.rerun()
                    else:
                         # Even if applied, allow delete if user wants to clean history
                         if st.button("🗑️ Delete Record", key=f"del_app_{job.id}"):
                             delete_job(job.id)
                             st.rerun()
                st.divider()

    # --- TAB 3: ACTIONABLE INSIGHTS ---
    with tab_analytics:
        st.markdown("### 🧠 Smart Insights & Gaps")
        
        saved = get_saved_jobs()
        if not saved:
            st.info("No data yet. Run some searches to generate insights!")
        else:
            from src.utils.analytics import analyze_skill_gaps, get_top_companies, get_market_skills
            
            # 1. MARKET DEMAND
            st.subheader("🔥 Market Demand: Top Skills")
            st.caption("What are companies asking for right now based on your search?")
            market_skills = get_market_skills(saved)
            if market_skills:
                skill_df = pd.DataFrame(market_skills, columns=["Skill", "Mentions"])
                skill_df.set_index("Skill", inplace=True)
                st.bar_chart(skill_df, color="#FF4B4B")
            
            st.divider()

            # 2. GAP ANALYSIS
            st.subheader("⚠️ Missing Skills")
            st.caption("Keywords in matched jobs that you might be missing:")
            gaps = analyze_skill_gaps(saved, skills)
            if gaps:
                gap_cols = st.columns(5)
                for i, (word, count) in enumerate(gaps[:5]):
                    with gap_cols[i]:
                        st.metric(label=word.capitalize(), value=f"{count}", delta="Missing", delta_color="inverse")
            else:
                st.success("Your skills match the job descriptions very well!")

            st.divider()

            # 3. PERFORMANCE STATS
            st.subheader("📊 Performance Analytics")
            
            # Data Preparation
            df = pd.DataFrame([{
                "source": j.source.upper(),
                "score": j.match_score if j.match_score else 0,
                "company": j.company
            } for j in saved])
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Source Breakdown")
                if not df.empty:
                    st.bar_chart(df['source'].value_counts())
                else: st.write("No data.")
                
            with c2:
                st.subheader("Match Score Dist.")
                if not df.empty:
                    bins = [0, 20, 40, 60, 80, 100]
                    labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
                    df['score_bin'] = pd.cut(df['score'], bins=bins, labels=labels)
                    bin_counts = df['score_bin'].value_counts().sort_index()
                    st.bar_chart(bin_counts, color="#00aa00")
                else: st.write("No data.")

            st.divider()
            st.subheader("🏢 Top Hiring Companies")
            top_cos = get_top_companies(saved)
            if top_cos:
                st.dataframe(pd.DataFrame(top_cos, columns=["Company", "Jobs Found"]), hide_index=True)


def run_batch_apply(jobs, name, skills, resume_text, resume_path, phone):
    temp_profile = Profile(name=name, skills=skills, resume_text=resume_text, resume_path=resume_path, phone=phone)
    progress = st.progress(0)
    status = st.empty()
    
    try:
        from src.application_bot import ApplicationBot
        # Use simple visual bot for demo/safety
        bot = ApplicationBot(headless=False)
        
        for i, job in enumerate(jobs):
            status.text(f"Applying to {i+1}/{len(jobs)}: {job.title} @ {job.company}...")
            try:
                bot.fill_application(job.url, temp_profile)
                # TRACKING
                mark_job_applied(job.id, status="applied")
                st.toast(f"✅ Applied & Tracked: {job.company}")
            except Exception as e:
                st.toast(f"❌ Failed {job.company}: {e}")
            progress.progress((i + 1) / len(jobs))
            
        bot.close()
        status.success("Batch Application Complete!")
        
    except Exception as e:
        st.error(f"Batch Error: {e}")

def run_single_apply(job, name, skills, resume_text, resume_path, phone):
    temp_profile = Profile(name=name, skills=skills, resume_text=resume_text, resume_path=resume_path, phone=phone)
    st.toast(f"Launching Auto-Apply Bot for {job.company}...", icon="🚀")
    try:
        from src.application_bot import ApplicationBot
        bot = ApplicationBot(headless=False) 
        bot.fill_application(job.url, temp_profile)
        
        # TRACKING
        if job.id:
            mark_job_applied(job.id, status="applied")
        
        st.success(f"Bot finished for {job.title}. Marked as Applied.")
    except Exception as e:
        st.error(f"Bot failed: {e}")

def run_search(query, location, skills, resume_text, resume_path, phone, use_mock, use_instahyre, use_hn, use_semantic, use_naukri, use_linkedin, use_smart_search, use_arbeitnow, email_enabled, email_user, email_pass, limit=10):
    # SMART SEARCH LOGIC
    queries = [query]
    if use_smart_search:
        q_lower = query.lower()
        if "data engineer" in q_lower:
            queries.extend(["Spark Developer", "Big Data Engineer", "Python Data Engineer", "ETL Developer"])
        elif "data scientist" in q_lower:
            queries.extend(["Machine Learning Engineer", "AI Engineer", "Data Analyst"])
        elif "frontend" in q_lower or "react" in q_lower:
            queries.extend(["React Developer", "UI Engineer", "Javascript Developer"])
        elif "backend" in q_lower or "python" in q_lower:
            queries.extend(["Python Developer", "Django Developer", "Backend Engineer"])
        elif "full stack" in q_lower:
             queries.extend(["Full Stack Developer", "Software Engineer"])
            
    # Setup
    profile = Profile(name="User", skills=skills, resume_text=resume_text, resume_path=resume_path, phone=phone)
    
    if use_semantic:
        matcher = SemanticMatcher()
    else:
        matcher = KeywordMatcher()
    
    search_log = []
    search_log.append(f"🧠 Smart Search Active. Queries: {queries}")
    
    all_jobs = []
    
    # Run scrapers
    with st.status("🔍 Searching across platforms...", expanded=True) as status:
        for i, q in enumerate(queries):
            status.update(label=f"Searching for '{q}' ({i+1}/{len(queries)})...")
            q_jobs = []
            
            # --- SCRAPER BLOCK ---
            if use_mock:
                try:
                    status.write(f"Checking Mock Data for {q}...")
                    s = MockScraper()
                    q_jobs.extend(s.scrape(query=q, location=location, limit=limit))
                except: pass
                
            if use_instahyre:
                try:
                    status.write(f"Scraping Instahyre for {q}...")
                    s = InstahyreScraper()
                    q_jobs.extend(s.scrape(query=q, location=location, limit=limit))
                except Exception as e: 
                    status.write(f"⚠️ Instahyre error: {e}")
                    search_log.append(f"Instahyre Error on '{q}': {e}")
            
            if use_arbeitnow:
                try:
                    status.write(f"Fetching Arbeitnow (Remote) for {q}...")
                    s = ArbeitnowScraper()
                    q_jobs.extend(s.scrape(query=q, location=location, limit=limit))
                except Exception as e:
                    status.write(f"⚠️ Arbeitnow error: {e}")
                    search_log.append(f"Arbeitnow Error on '{q}': {e}")

            if use_naukri:
                try:
                    status.write(f"Scraping Naukri for {q}...")
                    s = NaukriScraper()
                    q_jobs.extend(s.scrape(query=q, location=location, limit=limit))
                except Exception as e: 
                    status.write(f"⚠️ Naukri error: {e}")
                    search_log.append(f"Naukri Error on '{q}': {e}")
                
            if use_linkedin:
                try:
                    status.write(f"Scraping LinkedIn for {q}...")
                    s = LinkedInScraper()
                    q_jobs.extend(s.scrape(query=q, location=location, limit=limit))
                except Exception as e: 
                    status.write(f"⚠️ LinkedIn error: {e}")
                    search_log.append(f"LinkedIn Error on '{q}': {e}")
                
            search_log.append(f"Query '{q}' returned {len(q_jobs)} raw jobs.")
            all_jobs.extend(q_jobs)
            
        status.update(label="✅ Search Complete!", state="complete", expanded=False)

    # De-duplicate by URL
    unique_jobs = {j.url: j for j in all_jobs}.values()
    final_jobs = list(unique_jobs)
    
    # Match (Calculate scores BEFORE saving)
    matched_jobs = []
    if final_jobs:
        for job in final_jobs:
            try:
                score, details = matcher.match(job, profile)
                job.match_score = score
                matched_jobs.append(job)
            except Exception as e:
                matched_jobs.append(job)
                continue
        
    # Sort
    matched_jobs.sort(key=lambda x: x.match_score or 0, reverse=True)
    
    # NOTIFICATION LOGIC
    if email_enabled and email_user and email_pass:
        # Find high matches that haven't been alerted yet
        high_matches = [j for j in matched_jobs if (j.match_score or 0) >= 75]
        if high_matches:
            if 'last_alert_count' not in st.session_state: st.session_state['last_alert_count'] = 0
            
            st.toast(f"📧 Sending email alert for {len(high_matches)} top jobs...")
            notifier = Notifier(email_user, email_pass)
            success = notifier.send_alert(email_user, high_matches[:5]) # Top 5 only
            if success:
                st.toast("✅ Email sent!")
                search_log.append("📧 Email Notification sent successfully.")
            else:
                st.toast("❌ Email failed. Check credentials.")
                search_log.append("❌ Email Notification failed.")

    # Save to DB
    saved_count = save_jobs(matched_jobs)
    search_log.append(f"💾 Saved {saved_count} new unique jobs to Database.")
    
    st.session_state['results'] = matched_jobs
    st.session_state['search_log'] = search_log
    st.rerun()




if __name__ == "__main__":
    main()
