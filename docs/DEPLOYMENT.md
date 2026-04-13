# Data Analyst Depth - Backend Deployment Guide 🚀

Follow these steps to deploy your backend to **Render** completely for free.

## 1. Prepare your GitHub Repository
Ensure your latest local changes are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure backend for cloud deployment"
git push origin main
```

## 2. Deploy to Render
1.  **Sign Up:** Go to [Render.com](https://render.com/) and connect your GitHub account.
2.  **New Blueprint:** Click **"New +"** and select **"Blueprint"**.
3.  **Connect Repo:** Select your `data-analyst-depth` repository.
4.  **Confirm Blueprint:** Render will detect the `backend/render.yaml` file.
    -   It will automatically create a **Web Service** and a **PostgreSQL Database**.
5.  **Deploy:** Click **"Apply"**.

## 3. Configure Environment Variables
Once the service is created, go to the **Dashboard -> data-analyst-backend -> Environment**:
-   **GOOGLE_API_KEY:** Add your Gemini API key here.
-   **CORS_ORIGINS:** Ensure this matches your Vercel URL (e.g., `https://data-analyst-depth.vercel.app`).

## 4. Update the Frontend
Once Render provides you with a backend URL (e.g., `https://data-analyst-backend.onrender.com`):
1.  Go to your **Vercel Dashboard**.
2.  Select your frontend project -> **Settings -> Environment Variables**.
3.  Update (or add) `REACT_APP_BACKEND_URL` with your new Render URL.
4.  Redeploy your Vercel project to pick up the change.

---

### ⚠️ Note on File Storage (Free Tier)
Render's free tier uses ephemeral storage for files. While your **metadata** (queries, reports, settings) is persistent in the PostgreSQL database, physical files uploaded to the workspace will be cleared upon server restart. 

To keep files permanently, consider upgrading to a Render **Persistent Disk** or integrating cloud storage like AWS S3 or Cloudinary.
