import os

import google.auth
from google.auth.transport.requests import Request
from google.auth import impersonated_credentials

TARGET_SA = os.getenv("TARGET_SA", "a2a-service-account@gen-lang-client-0903142317.iam.gserviceaccount.com")
AUDIENCE = os.getenv("AUDIENCE", "travel-agent")

def get_oidc_token():

    # 1. Get your local user identity (Source)
    source_creds, _ = google.auth.default()

    # 2. STEP ONE: Create an impersonated ACCESS TOKEN credential
    # This acts as the service account itself
    target_creds = impersonated_credentials.Credentials(
        source_credentials=source_creds,
        target_principal=TARGET_SA,
        target_scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # 3. STEP TWO: Create the ID Token (OIDC) from the impersonated credential
    # The first argument must be the 'target_creds' we just made
    id_creds = impersonated_credentials.IDTokenCredentials(
        target_creds,
        target_audience=AUDIENCE,
        include_email=True
    )

    # 4. Refresh to fetch the token
    id_creds.refresh(Request())
    return id_creds.token
    

if __name__ == "__main__":
    try:
        print("Fetching impersonated token...")
        token = get_oidc_token()
        print(f"\nSUCCESS!\nToken: {token}")
    except Exception as e:
        print(f"\nERROR: {e}")