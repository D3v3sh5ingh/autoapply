# 🤖 AutoApply + JobAnalytics
**Author**: Devesh Singh

> *A privacy-first, open-source agent that automates the job hunt: Scraping, Matching, Applying, and Analytics.*

## 🚀 Key Features
*   **Multi-Source Scraping**: Instahyre, Naukri, LinkedIn, and **Arbeitnow (Remote)**.
*   **Intelligent Matching**: Uses Semantic AI (Sentence Transformers) + Resume Parsing (Skills specific).
*   **Auto-Apply Bot**: Selenium-based bot that fills applications for you.
*   **Smart Analytics**:
    *   **Skill Gaps**: Tells you which keywords you are missing.
    *   **Resume Health**: Tracks your match % trend over time.
    *   **Top Companies**: Shows who is hiring.
*   **Notifications**: Email alerts for high-match jobs (>75%).
*   **History**: Track applications, sort by score, and mark manual applications.

## 🛠️ Setup & Usage

1.  **Install**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Dashboard**:
    ```bash
    streamlit run src/ui/dashboard.py
    ```
    *Open http://localhost:8501 in your browser.*

3.  **Configure**:
    *   Enter your Name and Skills in the sidebar.
    *   (Optional) Enable Email Alerts with your Gmail/Outlook App Password.
    *   Upload your Resume PDF.

## � Docker Deployment
For easy deployment on a server or locally without installing dependencies manually:

```bash
docker-compose up --build -d
```
The application will be available at `http://your-server-ip:8501`. Your data is persisted in `autoapply.db` on the host machine.

## 🗄️ Data Management
*   **Export**: Download your entire application history as a CSV file.
*   **Selective Delete**: Use the 🗑️ icon on any job card to remove individual entries.
*   **Cleanup**: Remove expired jobs (older than 30 days) automatically.
*   **Reset**: Use the "Danger Zone" in the maintenance tab for a fresh start.

## 🤖 Bot Safety (BETA)
The Auto-Apply bot is a powerful tool. For your protection:
*   **Login Detection**: The bot automatically stops if it detects a Login or Signup page to prevent unintended account actions.
*   **Visual Mode**: By default, the bot runs in a visible window so you can supervise its actions.

---
*Built by Devesh Singh.*
> *Advanced AI development patterns were utilized to accelerate this project's implementation and automation.*
