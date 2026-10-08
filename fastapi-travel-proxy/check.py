import google.auth
from google.auth.transport.requests import Request

creds, project = google.auth.default()

creds.refresh(Request())

print("Project:", project)
print("Credential Type:", type(creds))

if hasattr(creds, "service_account_email"):
    print("Service Account:", creds.service_account_email)

if hasattr(creds, "quota_project_id"):
    print("Quota Project:", creds.quota_project_id)

print("Token exists:", creds.token is not None)