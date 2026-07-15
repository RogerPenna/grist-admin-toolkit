# Grist Admin & Data Toolkit v1.3 - Release Notes

## 🚀 New Features & Enhancements

### 🤖 AI Assistant Refactoring & Multi-Table Export
- **Always-Visible Paste Area:** The AI input field to paste generated data is now always visible as soon as you select a document, removing the need to generate a template first.
- **Relational Export (Multi-Table):** You can now select **multiple tables** at once when exporting data for AI analysis. The tool generates a unified JSON object (one key per table), allowing Large Language Models to analyze relationships (e.g., mapping Strategies to Objectives).
- **Internal IDs Included:** The AI JSON export now explicitly includes the Grist internal `id` for each record, which is crucial for the AI to understand and recreate referential links between tables.
- **UX Improvements:** Updated labels in the AI Assistant tab to be more intuitive. The main selector is now simply "Document" (serving as both source and target depending on the tool section).

### 🌍 Localization & Translation Fixes
- Fixed hardcoded Portuguese table headers in the **Access Rules (ACL)**, **Document Mapping**, **Global View**, and **Limits** tabs. All tables now correctly display headers in English when the UI language is switched.

### 🔌 Server Connection Improvements
- **Auto-Correction for Custom URLs:** When connecting to a self-hosted Grist instance, if the user provides the base URL without the required `/api` suffix (e.g., `https://mygristserver.org`), the toolkit will automatically append it to prevent connection failures.

## 🛠️ Technical Fixes
- Restored the version tracker in the sidebar for English users (previously out of sync with the Portuguese interface).
- Kept the cleanup of `gristHelper` columns in the AI export to maintain token efficiency, while restoring the necessary `id` context.
