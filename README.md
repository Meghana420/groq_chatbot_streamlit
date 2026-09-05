# Groq Chatbot Streamlit App

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository. Keep `.env` out of the repository; it is already ignored by `.gitignore`.
2. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Select **Create app**, choose the repository and branch, and set the main file to `main.py`.
4. Open **Advanced settings** before deploying. Add these secrets in TOML format:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   GROQ_MODEL = "qwen/qwen3.6-27b"
   ```

5. Click **Deploy**. The app will install the packages from `requirements.txt` and provide a public URL.

To update the app, push changes to the selected GitHub branch. Streamlit Cloud redeploys automatically.

## Run locally

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=qwen/qwen3.6-27b
```

Then run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run main.py
```

Never commit the `.env` file or publish the Groq API key.