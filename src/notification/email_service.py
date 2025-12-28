import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import os
from ..database.models import Job

class EmailService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv("EMAIL_SENDER")
        self.password = password or os.getenv("EMAIL_PASSWORD")
        self.enabled = bool(self.sender_email and self.password)

    def send_matches_alert(self, recipient_email: str, matched_jobs: List[Job]):
        if not matched_jobs:
            print("No jobs to notify.")
            return

        subject = f"AutoApply Found {len(matched_jobs)} New Job Matches!"
        
        # Build HTML Body
        body_html = "<h2>Great news! We found jobs matching your profile:</h2><ul>"
        
        for job in matched_jobs:
            score = job.match_score if job.match_score else 0
            body_html += f"""
            <li style="margin-bottom: 20px;">
                <strong>{job.title}</strong> at {job.company} <br>
                <span style="color: green;">Match Score: {score}%</span> <br>
                <a href="{job.url}">Apply Now</a> <br>
                <small>{job.location} | {job.source}</small>
            </li>
            """
        body_html += "</ul>"

        if self.enabled:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body_html, 'html'))

                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(msg)
                server.quit()
                print(f"Email sent to {recipient_email}")
            except Exception as e:
                print(f"Failed to send email: {e}")
        else:
            print("=== MOCK EMAIL NOTIFICATION ===")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print("Body Preview:")
            print(body_html.replace("<br>", "\n").replace("<li>", "- ").replace("</li>", ""))
            print("================================")
            print("Note: Configure EMAIL_SENDER and EMAIL_PASSWORD env vars to send real emails.")
