# StockWise — AI-Powered Inventory Management

A beginner-friendly Flask inventory application using OOP, JSON storage and optional Groq generative AI.

## Features
- Product CRUD: add, view, edit and delete.
- Search by product ID, name or category.
- `Product` and inherited `PerishableProduct` classes.
- Dashboard totals: products, units, inventory value, low stock and out of stock.
- Optional Groq AI: inventory analysis, reorder-review suggestions, natural-language assistant and product descriptions.
- Works for normal inventory tasks without a Groq API key.
- Responsive green-and-white interface.

## Project structure
```text
AI_Powered_Inventory_Management/
├── api/index.py              # Vercel entry point
├── app.py                    # Flask routes
├── models.py                 # Product OOP classes
├── inventory.py              # InventoryManager and JSON persistence
├── ai_helper.py              # Groq integration
├── data/products.json        # Sample data (local development)
├── templates/index.html
├── static/style.css
├── static/app.js
├── requirements.txt
├── .env.example
├── .gitignore
├── vercel.json
└── README.md
```

## Run locally (Windows PowerShell)

1. Open PowerShell in this project folder.
2. Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this in the same terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

4. Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace `your_groq_api_key_here` with your own Groq API key. Keep the key private. If you leave the placeholder, the inventory features still work; AI actions will show a helpful message.

5. Start Flask:

```powershell
py app.py
```

6. Open `http://127.0.0.1:5000` in your browser. Keep the terminal running while using the app; press `Ctrl+C` to stop it.

## Groq configuration
- `GROQ_API_KEY`: API key from your Groq account.
- `GROQ_MODEL`: model identifier enabled for your account. The example uses `openai/gpt-oss-120b`; change it if Groq's model availability changes.
- Never paste your API key into Python, JavaScript, GitHub, screenshots or public messages.

## GitHub upload

Create an empty repository on GitHub, then run these commands from the project folder (replace the URL with your own repository URL):

```powershell
git init
git add .
git status
git commit -m "Build AI-powered inventory management system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Check `git status` before committing. `.env` is excluded by `.gitignore`; do not force-add it. If a real key was ever committed, revoke/rotate it in Groq and remove it from repository history.

## Deploy to Vercel

1. Push the project to GitHub.
2. Sign in to Vercel and choose **Add New → Project**.
3. Import the GitHub repository.
4. In project settings, add environment variables:
   - `GROQ_API_KEY` = your key (optional)
   - `GROQ_MODEL` = a model available to your Groq account
5. Deploy. The included `vercel.json` and `api/index.py` route requests to Flask.

### Important storage limitation
The JSON file is suitable for learning and local testing. Vercel serverless deployments do not provide reliable persistent writable project storage; changes written to local files or `/tmp` are not a durable shared database and may disappear between invocations. For real production use, replace `InventoryManager` JSON persistence with Supabase/PostgreSQL (or another managed database), add authentication/authorization, and use database transactions. Do not treat this starter JSON version as a production multi-user system.

## Notes
- Product price, quantity and reorder level are validated on the server.
- Reorder quantities from AI are estimates only. The app does not know sales velocity, supplier lead time or minimum order quantities.
- This starter does not include login, roles, audit logs or automated backups.
