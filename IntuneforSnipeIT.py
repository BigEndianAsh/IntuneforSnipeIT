#!/usr/bin/env python3
"""
Intune -> Snipe-IT Device Sync
- Matches on serial number
- Splits categories: Windows -> Laptops, Android -> Phones
- iOS Logic: Distinguishes iPhones (Phones) from iPads (Tablets) via Model string
- Clickable Intune Links: Converts Device ID to a direct portal link
"""

import requests
import time

# -- Configuration -------------------------------------------------------------

AZURE_TENANT_ID     = "YOUR_TENANT_ID"
AZURE_CLIENT_ID     = "YOUR_CLIENT_ID"
AZURE_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

SNIPEIT_URL         = "https://your-snipeit.example.com"
SNIPEIT_API_TOKEN   = "YOUR_SNIPEIT_API_TOKEN"

# OS Mapping for non-iOS devices[cite: 1]
OS_CATEGORY_MAP = {
    "Windows": "Laptops",
    "Android": "Phones"
}

DEFAULT_CATEGORY_NAME   = "Intune Devices"
DEFAULT_FIELDSET_NAME   = "Intune Devices"
DEFAULT_STATUS_NAME     = "Deployed"

INTUNE_ID_FIELD_NAME = "Intune Device ID"
AUTO_CREATE_USERS    = True

# -- Graph API auth ------------------------------------------------------------

def get_graph_token():
    url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
    r = requests.post(url, data={
        "grant_type":    "client_credentials",
        "client_id":     AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/.default",
    }, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def get_all_intune_devices(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = (
        "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"
        "?$select=id,deviceName,serialNumber,manufacturer,model,"
        "operatingSystem,osVersion,userPrincipalName,userDisplayName,"
        "lastSyncDateTime,enrolledDateTime,complianceState"
        "&$top=999"
    )
    devices = []
    while url:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        body = r.json()
        devices.extend(body.get("value", []))
        url = body.get("@odata.nextLink")
    return devices

# -- Snipe-IT helpers ----------------------------------------------------------

def snipe_headers():
    return {
        "Authorization": f"Bearer {SNIPEIT_API_TOKEN}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }

def snipe_get(path, params=None):
    r = requests.get(f"{SNIPEIT_URL}/api/v1{path}",
                     headers=snipe_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def snipe_post(path, payload):
    r = requests.post(f"{SNIPEIT_URL}/api/v1{path}",
                      headers=snipe_headers(), json=payload, timeout=30)
    return r.json()

def snipe_patch(path, payload):
    r = requests.patch(f"{SNIPEIT_URL}/api/v1{path}",
                       headers=snipe_headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# -- Category & Resource Management --------------------------------------------

def get_or_create_category(name):
    """Strict name matching for categories[cite: 1]."""
    results = snipe_get("/categories", {"search": name})
    for row in (results.get("rows") or []):
        if row["name"].strip().lower() == name.strip().lower():
            return row["id"]
    
    print(f"   Category '{name}' not found -- creating...")
    result = snipe_post("/categories", {"name": name, "category_type": "asset"})
    if result.get("status") == "success":
        return result["payload"]["id"]
    else:
        print(f"   ERROR: Could not create category '{name}': {result.get('messages')}")
        return None

def get_or_create_status(name):
    results = snipe_get("/statuslabels")
    for row in (results.get("rows") or []):
        if row["name"].lower() == name.lower():
            return row["id"]
    result = snipe_post("/statuslabels", {"name": name, "type": "deployable"})
    return result["payload"]["id"]

def get_or_create_custom_field(field_name):
    fields = snipe_get("/fields")
    for field in (fields.get("rows") or []):
        if field["name"].lower() == field_name.lower():
            col = field.get("db_column") or field.get("db_column_name")
            return field["id"], col
    result = snipe_post("/fields", {
        "name": field_name,
        "element": "text",
        "help_text": "Clickable link to Microsoft Intune",
    })
    payload = result["payload"]
    return payload["id"], (payload.get("db_column") or payload.get("db_column_name"))

def get_or_create_fieldset(fieldset_name, field_id):
    fieldsets = snipe_get("/fieldsets")
    for fs in (fieldsets.get("rows") or []):
        if fs["name"].lower() == fieldset_name.lower():
            fieldset_id = fs["id"]
            existing_fields = [f["id"] for f in (fs.get("fields", {}).get("rows") or [])]
            if field_id not in existing_fields:
                snipe_post(f"/fieldsets/{fieldset_id}/fields", {"field_id": field_id})
            return fieldset_id
    result = snipe_post("/fieldsets", {"name": fieldset_name})
    fs_id = result["payload"]["id"]
    snipe_post(f"/fieldsets/{fs_id}/fields", {"field_id": field_id})
    return fs_id

# -- Manufacturer & Model ------------------------------------------------------

def get_or_create_manufacturer(name):
    name = name or "Unknown"
    results = snipe_get("/manufacturers", {"search": name})
    for row in (results.get("rows") or []):
        if row["name"].lower() == name.lower():
            return row["id"]
    result = snipe_post("/manufacturers", {"name": name})
    return result["payload"]["id"]

def get_or_create_model(model_name, manufacturer_id, category_id, fieldset_id):
    model_name = model_name or "Unknown Model"
    results = snipe_get("/models", {"search": model_name})
    for row in (results.get("rows") or []):
        if row["name"].lower() == model_name.lower():
            # If the model exists but is assigned to the wrong category, fix it[cite: 1].
            if row.get("category", {}).get("id") != category_id:
                snipe_patch(f"/models/{row['id']}", {"category_id": category_id})
            return row["id"]
    result = snipe_post("/models", {
        "name":            model_name,
        "manufacturer_id": manufacturer_id,
        "category_id":     category_id,
        "fieldset_id":     fieldset_id,
    })
    return result["payload"]["id"]

# -- Main Sync Logic -----------------------------------------------------------

def sync():
    print("Starting Intune to Snipe-IT Sync...")
    token = get_graph_token()

    # Initial setup[cite: 1]
    status_id = get_or_create_status(DEFAULT_STATUS_NAME)
    field_id, intune_field_col = get_or_create_custom_field(INTUNE_ID_FIELD_NAME)
    fieldset_id = get_or_create_fieldset(DEFAULT_FIELDSET_NAME, field_id)

    devices = get_all_intune_devices(token)
    print(f"Syncing {len(devices)} devices...\n")

    for device in devices:
        name   = device.get("deviceName", "Unknown")
        serial = (device.get("serialNumber") or "").strip()
        os     = device.get("operatingSystem", "")
        model_str = device.get("model", "")
        intune_id = device.get("id", "")

        if not serial:
            continue

        # Determine Category[cite: 1]
        target_category = DEFAULT_CATEGORY_NAME
        
        # iOS Splitting Logic: Distinguish iPhone vs iPad via Model string[cite: 1]
        if "iOS" in os:
            if "iPad" in model_str:
                target_category = "Tablets"
            elif "iPhone" in model_str:
                target_category = "Phones"
        else:
            # Standard OS Mapping for Windows/Android[cite: 1]
            for os_key, cat_name in OS_CATEGORY_MAP.items():
                if os_key.lower() in os.lower():
                    target_category = cat_name
                    break
        
        try:
            category_id = get_or_create_category(target_category)
            if not category_id:
                continue

            mfr_id   = get_or_create_manufacturer(device.get("manufacturer"))
            model_id = get_or_create_model(model_str, mfr_id, category_id, fieldset_id)
            
            # Create Clickable Link for the custom field[cite: 1]
            intune_link = f'<a href="https://intune.microsoft.com/#view/Microsoft_Intune_DeviceSettings/ManagedDeviceDetailsBlade/id/{intune_id}" target="_blank">{intune_id}</a>'

            payload = {
                "name":      name,
                "serial":    serial,
                "model_id":  model_id,
                "status_id": status_id,
                intune_field_col: intune_link
            }

            # Find and Update/Create Asset[cite: 1]
            results = snipe_get(f"/hardware/byserial/{serial}")
            rows = results.get("rows") or []
            
            if rows:
                asset_id = rows[0]["id"]
                snipe_patch(f"/hardware/{asset_id}", payload)
                print(f"  [UPDATED] {name} -> {target_category}")
            else:
                result = snipe_post("/hardware", payload)
                if result.get("status") == "success":
                    print(f"  [CREATED] {name} -> {target_category}")
                else:
                    print(f"  [FAILED]  {name}: {result.get('messages')}")

        except Exception as e:
            print(f"  [ERROR] Processing {name}: {e}")

        time.sleep(0.1)

if __name__ == "__main__":
    sync()
