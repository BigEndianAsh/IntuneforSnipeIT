# Installation & Configuration Guide

Follow these steps to deploy the Intune sync script in your environment.

## 1. Prerequisites
*   **Python 3.8+**
*   **Snipe-IT Instance**: You must have admin access to generate API tokens.
*   **Azure AD (Entra ID)**: You must have permissions to create an App Registration.

## 2. Azure App Registration
The script requires access to the Microsoft Graph API to read device data.

1.  Log in to the [Azure Portal](https://portal.azure.com).
2.  Navigate to **App Registrations** > **New Registration**.
3.  Under **API Permissions**, add the following **Application Permission**:
    *   `DeviceManagementManagedDevices.Read.All`
4.  Click **Grant admin consent for [Your Org]**.
5.  Navigate to **Certificates & secrets** and create a new **Client Secret**. Save the Value immediately.

## 3. Snipe-IT API Token
1.  Log in to Snipe-IT.
2.  Go to your **User Settings** (top right) > **Manage API Tokens**.
3.  Click **Create New Token** and save the provided string.

## 4. Script Setup
1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/BigEndianAsh/IntuneforSnipeIT/intune-snipeit-sync.git](https://github.com/BigEndianAsh/IntuneforSnipeIT/intune-snipeit-sync.git)
    cd intune-snipeit-sync
    ```
2.  **Install dependencies**:
    ```bash
    pip install requests
    ```
3.  **Configure the script**:
    Open `intune_snipeit_sync.py` and fill in your credentials:
    ```python
    AZURE_TENANT_ID     = "your-tenant-id"
    AZURE_CLIENT_ID     = "your-client-id"
    AZURE_CLIENT_SECRET = "your-client-secret"
    SNIPEIT_URL         = "[https://your-snipeit.example.com](https://your-snipeit.example.com)"
    SNIPEIT_API_TOKEN   = "your-api-token"
    ```

## 5. Running the Sync
Run the script manually to test the connection:
```bash
python3 intune_snipeit_sync.py
