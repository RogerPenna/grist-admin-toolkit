# Release Notes - v1.2

## 🚀 New Features

### 🏢 Organization User Management
- **Invite to Organization:** New section in the **Global View** tab allows batch-inviting users directly to the Grist Organization.
- **Granular Roles:** Support for all Grist Organization levels:
  - **Owner** (Proprietário)
  - **Editor** (Editor)
  - **Viewer** (Observador)
  - **Member / No Default Access** (Membro / Sem Acesso Padrão)

### 🛡️ Safety & Compliance Checks
- **External User Detection:** The **Quick Actions** tool now automatically detects if an email being added to a document is not a member of the organization.
- **Guest Limit Warnings:** Alerts users about adding Guests (especially useful for Free Plan compliance).
- **One-Click Onboarding:** If an external user is detected, you can now choose to "Add to Organization First" with a single click before granting document access.

## 🛠️ Improvements & Fixes
- **i18n Enhancements:** Full English and Portuguese localization for all new management features.
- **API Robustness:** New `update_org_access` function utilizing the Grist Organization Access API.
- **UI/UX:** Improved selectboxes with localized role labels for better clarity.

---
*Prepared for release on 2026-06-10.*
