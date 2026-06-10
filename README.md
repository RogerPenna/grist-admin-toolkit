# Grist Admin & Data Toolkit

A comprehensive Streamlit application designed for Grist power users and administrators to manage organizations, audit security, and perform advanced data engineering.

## Key Features

### 🔐 Access Management
- **Global View:** List all Team Site users and their organizational access levels.
- **Document Mapping:** Recursive scan of all workspaces and documents to identify individual permissions.
- **Bulk Operations:** Copy, update, or revoke access for multiple users across multiple documents at once.
- **Quick Actions:** Rapidly invite or remove batches of users via email lists.
- **Access Rules (ACL):** Human-readable denormalization of complex Grist ACL tables with JSON backup/restore and **AI-assisted editing** (Generate JSON for AI).

### 🏗️ Data Engineering
- **Table Cloner:** Copy table schemas (structure) between documents without moving data.
- **Data Transporter:** Move entire datasets between documents while maintaining relationship integrity and formulas (3-phase strategy).
- **Integrity Audit:** Sync Grist permissions with a "Control Table" to identify and fix missing or orphan accesses.
- **Blueprint (JSON):** Infrastructure as Code for Grist—create or completely rebuild documents from JSON schemas. Supports **AI-assisted structural extraction**.
- **Populate with AI:** Integration with LLMs to generate realistic test data based on your table structures. Now includes **real sample records** for better context.

### ⚙️ System
- **Limits & Usage:** Monitor document health, row counts, and SQLite file sizes against Grist performance limits.
- **Contextual Help:** Integrated documentation with deep links for every feature.

## Setup & Execution

1. **Prerequisites:**
   - Python 3.8+
   - Grist API Key (Owner permissions recommended)

2. **Environment:**
   - Create a `.env` file or provide your API Key directly in the app sidebar.
   ```env
   GRIST_API_KEY=your_api_key_here
   ```

3. **Installation:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App:**
   - Use the provided batch script (Windows):
     ```bash
     run_toolkit.bat
     ```
   - Or run directly via Streamlit:
     ```bash
     streamlit run grist_admin_toolkit.py
     ```

## Security Note
This application communicates directly with your Grist server via the official REST API. It does not store your data on external servers. Local caching is used for mapping results to improve performance.
