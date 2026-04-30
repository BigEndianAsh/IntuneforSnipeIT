# Intune to Snipe-IT Device Sync

This Python script automates the synchronization of hardware assets from **Microsoft Intune** to **Snipe-IT**. It ensures your asset management database stays current with your MDM-managed devices.

## 🚀 Features

*   **Intelligent Categorization**: 
    *   Windows devices map to `Laptops`.
    *   Android devices map to `Phones`.
    *   iOS devices are split by model: `iPads` to `Tablets` and `iPhones` to `Phones`[cite: 1].
*   **Deep Linking**: The Intune Device ID is stored as a clickable HTML link in Snipe-IT for one-click access to the Intune portal[cite: 1].
*   **Automated Matching**: Matches devices based on Serial Number to prevent duplicate records[cite: 1].
*   **Asset Management**: Automatically creates/updates Categories, Manufacturers, and Models as needed[cite: 1].
*   **Model Correction**: If a device model is in the wrong category, the script "patches" it to the correct one[cite: 1].

## 🛠️ Setup

### Prerequisites
* Python 3.x
* `requests` library (`pip install requests`)

### Azure Configuration
1. Register an App in the **Azure Portal** (App Registrations).
2. Grant `DeviceManagementManagedDevices.Read.All` Graph API permissions.
3. Generate a **Client Secret**.

### Snipe-IT Configuration
1. Generate a **Personal Access Token** in your Snipe-IT user settings.

## ⚙️ Configuration

Edit the script variables at the top of the file:
```python
AZURE_TENANT_ID     = "your-tenant-id"
AZURE_CLIENT_ID     = "your-client-id"
AZURE_CLIENT_SECRET = "your-client-secret"
SNIPEIT_URL         = "[https://your-snipeit.example.com](https://your-snipeit.example.com)"
SNIPEIT_API_TOKEN   = "your-token"
