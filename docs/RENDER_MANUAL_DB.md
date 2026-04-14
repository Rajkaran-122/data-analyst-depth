# Manual Render Database Setup Guide 🗄️

If you prefer to manage your PostgreSQL database manually rather than through a Blueprint, follow these steps.

### ⚠️ Prerequisite: The "One Free DB" Rule
Render allows only **one** free-tier PostgreSQL instance per account. If you already have one (like `finguard-db`), you must either delete it or upgrade your account before creating a new one.

---

## 1. Create the Database
1.  Log in to [Render.com](https://render.com/).
2.  Click **New +** -> **PostgreSQL**.
3.  Fill in the details:
    -   **Name:** `data-analyst-db`
    -   **Database:** `data_analyst`
    -   **User:** `admin`
    -   **Region:** Select the same region as your Web Service (e.g., Oregon).
    -   **Plan:** Select **Free**.
4.  Click **Create Database**.

## 2. Retrieve Connection String
1.  Wait for the status to turn **"Available"**.
2.  Scroll down to the **"Connections"** section.
3.  Copy the **"Internal Database URL"**. 
    -   *Example: `postgres://admin:pwd@dpg-xxx-a:5432/data_analyst`*

## 3. Link to the Backend API
1.  Navigate to your **`data-analyst-prod-api`** Web Service in the Render Dashboard.
2.  Click on the **Environment** tab in the sidebar.
3.  Find the `DATABASE_URL` environment variable.
4.  Click **Edit**, paste your Internal Database URL, and click **Save**.
5.  Render will automatically redeploy your API with the new connection.

## 4. Verification
Once the API is redeployed (turns Green), check the **Logs**. You should see:
`INFO:  Connected to PostgreSQL database at ...`
or no connection errors.

---

## Alternative: Use your existing Database
If you don't want to delete your other database, simply copy its **Internal Database URL** and paste it into the `DATABASE_URL` field of the `data-analyst-prod-api` service. SQLAlchemy will automatically create the tables it needs!
