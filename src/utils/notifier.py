import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .logger import setup_logger

class Notifier:
    """
    Handles sending email notifications for high-match jobs.
    Uses SMTP (works with Gmail App Passwords, Outlook, etc.)
    """
    def __init__(self, email_user, email_pass, header="AutoApply Agent"):
        self.user = email_user
        self.password = email_pass
        self.header = header
        self.logger = setup_logger("Notifier")

    def send_alert(self, to_email, job_matches):
        """
        Sends an HTML email.
        If job_matches is empty, sends a Test Email.
        """
        if not self.user or not self.password:
            self.logger.warning("Email credentials missing.")
            return False

        if not job_matches:
             # Test Mode
             subject = "✅ AutoApply Email Test"
             body = "<h2>Connection Successful!</h2><p>Your email alerts are correctly configured.</p>"
        else:
             subject = f"🎯 {len(job_matches)} New High-Match Jobs Found!"
             # Build HTML Body
             body = f"<h2>🚀 {self.header} found new matches for you:</h2><hr>"
        for job in job_matches:
            score = int(job.match_score) if job.match_score else 0
            body += f"""
            <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <h3 style="margin: 0; color: #2E86C1;">{job.title}</h3>
                <p style="margin: 5px 0;"><strong>Company:</strong> {job.company} | <strong>Location:</strong> {job.location}</p>
                <p style="margin: 5px 0;"><strong>Match Score:</strong> <span style="color: green; font-weight: bold;">{score}%</span></p>
                <a href="{job.url}" style="background-color: #28B463; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; display: inline-block;">Apply Now</a>
            </div>
            """
        
        body += "<p><em>Sent by your AutoApply Agent 🤖</em></p>"

        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            # Auto-detect SMTP server based on email (simple heuristic)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            if "outlook" in self.user or "hotmail" in self.user:
                smtp_server = "smtp-mail.outlook.com"
            elif "yahoo" in self.user:
                smtp_server = "smtp.mail.yahoo.com"
                
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to_email, msg.as_string())
            server.quit()
            
            self.logger.info(f"Email alert sent to {to_email}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
