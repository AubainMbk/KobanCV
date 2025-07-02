import requests
from config import KOBAN_GENERAL_API_KEY, KOBAN_USER_API_KEY, KOBAN_ENDPOINT

def send_to_koban(data):
    headers = {
        "X-ncApi": KOBAN_GENERAL_API_KEY,
        "X-ncUser": KOBAN_USER_API_KEY,
        "Content-Type": "application/json"
    }

    # Extraction du prénom et du nom à partir du nom complet fourni
    full_name = data.get("full_name", "") or ""
    name_parts = full_name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else full_name

    # Construction du payload SANS niveau "Third"
    third_payload = {
        "Label": last_name or "CV inconnu",     # Nom de famille seulement
        "FirstName": first_name,                # Prénom seulement
        "Email": data.get("email"),
        "Cell": data.get("mobile"),               
        "Type": {"Code": "PART"},           # code du type "Particulier"
        "Status": {"Code": "MANVAL"},      # code du statut "Manager à valider"
        "AssignedTo": {"Extcode": "Olivier"}  # code utilisateur Olivier
    }

    print("Payload envoyé :", third_payload)
    resp = requests.post(
        KOBAN_ENDPOINT,
        headers=headers,
        json=third_payload,
        timeout=10
    )
    print("Réponse création Compte:", resp.status_code, resp.text)
    if not resp.ok:
        return False, f"Erreur création Compte: {resp.status_code} {resp.text}"

    return True, "Compte créé !"
