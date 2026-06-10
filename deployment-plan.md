# Deployment Plan: "The Closer" Cold Email Operator

This guide outlines the steps to deploy the Streamlit Web Application for **"The Closer"** cold email sender bot.

---

## Can we use Streamlit to deploy this project?

**Yes, absolutely.** Streamlit provides **Streamlit Community Cloud** (share.streamlit.io), which is a free, secure, and production-ready hosting service for Streamlit projects. It connects directly to a GitHub repository, pulls the code, installs dependencies from `requirements.txt`, and runs the application in the cloud. It also includes built-in secure **Secrets Management** for passwords and API keys, ensuring safety-by-default.

---

## 1. Prerequisites for Deployment
Before deploying, make sure you have:
1. A **GitHub Account** with the repository pushed to a public or private repo.
2. A **Streamlit Community Cloud Account** (sign up for free at [share.streamlit.io](https://share.streamlit.io/) using your GitHub account).
3. Access to your configuration variables (SMTP host credentials, Groq API key).

---

## 2. Step-by-Step Deployment on Streamlit Community Cloud

### Step 1: Push Code to GitHub
Ensure your repository contains the following core files at the root level:
* `app.py` (Streamlit entrypoint)
* `requirements.txt` (Declares `streamlit`, `python-dotenv`, `groq`)
* `contacts.json` (Seed targets)
* `logger.py`, `email_generator.py`, `email_sender.py` (Core modules)

> [!WARNING]
> **Never commit your `.env` file containing real passwords or keys to GitHub.** 
> Ensure `.env` is listed in your `.gitignore` file before pushing.

### Step 2: Deploy on Streamlit Cloud
1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click the **"New App"** button in the dashboard.
3. Select your repository, branch (e.g. `main`), and set the main file path to:
   ```text
   app.py
   ```
4. Click **"Deploy!"**

### Step 3: Configure Cloud Secrets (Credentials)
Streamlit Cloud manages environment variables securely via its **Secrets Manager** instead of `.env` files.
1. In your app dashboard on Streamlit Cloud, click **Settings** (gear icon) in the bottom-right corner.
2. Select **Secrets** on the left menu.
3. Paste the variables in TOML format:
   ```toml
   SMTP_HOST = "smtp.gmail.com"
   SMTP_PORT = "587"
   SMTP_USER = "your_email@gmail.com"
   SMTP_PASSWORD = "your_gmail_app_password"
   SENDER_NAME = "Your Name"
   DRY_RUN = "true"
   USE_LLM = "true"
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   ```
4. Click **Save**. The app will automatically restart and inject these variables as secure environment keys.

---

## 3. Alternative Deployment Platforms
If you want to host the app outside Streamlit Cloud, here are standard alternatives:

### Option A: Hugging Face Spaces (Free)
Excellent free alternative that runs Streamlit apps in Docker-like sandboxes.
1. Create a Hugging Face account and choose **"New Space"**.
2. Select **Streamlit** as the SDK.
3. Add your repository files.
4. Add environment variables under **Settings > Variables and Secrets**.

### Option B: Render or Fly.io (Dockerized)
For complete control using a custom domain.
1. Create a `Dockerfile` in the root:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install --no-cache-dir -r requirements.txt
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```
2. Connect Render to your GitHub repository and deploy as a **Web Service**.
3. Add environment configurations inside Render's dashboard.
