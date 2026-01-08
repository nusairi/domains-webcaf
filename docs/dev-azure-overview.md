# Dev Environment Overview (WebCAF)

## Azure Resources (Dev)
- **Resource Group**: `MHCLGPoc` groups all Dev assets.
- **Container App**: runs the WebCAF web service.
- **Container Registry (ACR)**: stores the application image.
- **PostgreSQL Flexible Server**: stores all business data (users, profiles, assessments).
- **Key Vault**: stores secrets (DB password, Django secret, OIDC keys).
- **Log Analytics**: collects application and platform logs.

## Data Flow (Dev)
1) User opens the WebCAF URL in a browser.
2) Request hits the **Container App**.
3) App reads/writes to **PostgreSQL** for users, organisations, systems, assessments.
4) App reads secrets from **Key Vault** at runtime.
5) Logs are sent to **Log Analytics** for monitoring.

## Dev Login Journey (Simple Auth)
1) User visits the Dev URL.
2) If not authenticated, they are redirected to **Django login** (`/admin/login/`).
3) After login, the app checks for a **UserProfile**:
   - If present, user lands in **My Account**.
   - If missing, user sees: “You do not have a profile set up.”
4) Admins create UserProfiles and assign roles (Organisation Lead/User).

## Diagram (Dev)
```
Browser
  |
  v
Azure Container App (webcaf)
  |  \
  |   \--> Log Analytics
  v
PostgreSQL (Assessments, Users, Profiles)
  ^
  |
Key Vault (Secrets, Keys)
  ^
  |
ACR (Container Image)
```
