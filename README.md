# Intune to Snipe-IT Asset Sync

An automated synchronization tool that fetches managed devices from **Microsoft Intune** and populates them into **Snipe-IT** via the Graph API and Snipe-IT API.

## 🚀 Key Features

*   **Smart Categorization**:
    *   **Windows**: Automatically assigned to `Laptops`[cite: 1].
    *   **Android**: Automatically assigned to `Phones`[cite: 1].
    *   **iOS/iPadOS**: Dynamically splits based on hardware model; `iPad` models go to `Tablets`, while `iPhone` models go to `Phones`[cite: 1].
*   **Direct Portal Linking**: The Intune Device ID is stored as a clickable HTML link in Snipe-IT, allowing you to jump directly to the device management blade in the Intune portal[cite: 1].
*   **Duplicate Prevention**: Matches assets strictly by Serial Number to ensure clean data[cite: 1].
*   **Auto-Provisioning**: Automatically creates Categories, Manufacturers, and Models in Snipe-IT if they do not already exist[cite: 1].
*   **Model Correction**: If a hardware model’s category is updated (e.g., a generic device is identified as a Laptop), the script "patches" the existing model record in Snipe-IT[cite: 1].

## 📊 Logic Overview

The script follows a specific hierarchy to ensure data integrity:
1.  **Auth**: Authenticates with Microsoft Graph and Snipe-IT[cite: 1].
2.  **Resource Check**: Verifies Status Labels, Fieldsets, and Custom Fields[cite: 1].
3.  **Process Devices**: Iterates through Intune devices, calculates the target category, and performs a search-or-create for the Model[cite: 1].
4.  **Sync**: Updates existing assets or creates new ones with the deep link attached[cite: 1].

## 📄 License
This project is licensed under the MIT License.
