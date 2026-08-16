# Web App & Hosting Guide

This guide explains how to run the UGC NET Answer Key Checker as a sleek Web Application, and how to expose it to the internet using Docker and Ngrok.

## Prerequisites
- **Docker** and **Docker Compose** installed on your computer.
- A free account on [Ngrok](https://ngrok.com/) (to get an Authtoken).

---

## 1. Local System Only (No Docker)
If you just want to run the web app on your own computer without Docker:
```bash
pip install -r requirements.txt
streamlit run web_app.py
```
*Access the app at: `http://localhost:8501`*

---

## 2. Local Network (via Docker)
To run the app using Docker, ensuring zero python dependencies on your host machine, and allowing anyone on your Wi-Fi (Local Area Network) to access it:

```bash
docker-compose --profile local up -d
```
*Access the app on your PC at: `http://localhost:8501`*
*Access the app on your phone at: `http://<YOUR_PC_IP_ADDRESS>:8501`*

---

## 3. Expose to the Internet via Ngrok (Local Host)
If you want to send a link to a friend over the internet, but run the server from your own computer:

1. Copy your Ngrok Authtoken from your Ngrok dashboard.
2. Set it as an environment variable in your terminal:
   - **Linux/Mac**: `export NGROK_AUTHTOKEN="your_token_here"`
   - **Windows (CMD)**: `set NGROK_AUTHTOKEN=your_token_here`
   - **Windows (PowerShell)**: `$env:NGROK_AUTHTOKEN="your_token_here"`
3. Run Docker Compose with the `ngrok` profile:
   ```bash
   docker-compose --profile ngrok up -d
   ```
4. View your public URL by checking the Ngrok container logs:
   ```bash
   docker logs ugc_net_answerkey_checker-ngrok-1 | grep "started tunnel"
   ```
   *Look for the `url=https://abc-123.ngrok-free.app` string.*

---

## 4. Expose to the Internet via GitHub Actions (Free Cloud Server)
If you don't want to keep your computer turned on, you can use GitHub's servers to host your Docker container and Ngrok tunnel for up to 6 hours at a time!

### Setup:
1. Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**.
3. Name: `NGROK_AUTHTOKEN`
4. Secret: Paste your Ngrok token here and click **Add secret**.

### How to Start the Server:
1. Go to the **Actions** tab in your GitHub repository.
2. Click on **"Host Web App via Ngrok"** on the left sidebar.
3. Click the **Run workflow** dropdown on the right.
4. Select how many hours you want the server to stay alive (e.g., `2`) and click Run.
5. Click on the running job and open the **"Display Public URL"** step in the logs.
6. Copy the `https://...ngrok-free.app` URL and share it with your students!

*(Note: GitHub limits Actions to 6 hours max. When it expires, simply click Run workflow again to get a new link!)*
