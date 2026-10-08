import os

from fastapi import FastAPI, Depends
import requests
import google.auth
from google.auth.transport.requests import Request
from google.auth import impersonated_credentials
from generate_token import get_oidc_token
from fastapi import FastAPI, Request
import requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app = FastAPI()
security = HTTPBearer()

# Environment variables
AGENT_API_URL = os.getenv("AGENT_API_URL", "https://travel-agent-75594044717.us-central1.run.app")

@app.post("/generate-token")
def generate_token(payload: dict):
    """
    Generates an impersonated identity token
    """
    if(payload.get("client_id") == None or payload.get("client_id") != os.getenv("AUDIENCE", "travel-agent")):
        return {"error": "Invalid or missing client_id in payload"}

    token = get_oidc_token()
    return {"token": token}


@app.get("/get-agent-sessions")
def get_agent_sessions(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Forwards incoming request headers + payload to Cloud Run
    """

    # Copy incoming headers
    incoming_headers = dict(request.headers)

    # Remove problematic browser headers
    incoming_headers.pop("host", None)
    incoming_headers.pop("content-length", None)
    incoming_headers.pop("origin", None)
    incoming_headers.pop("referer", None)

    # Forward auth properly
    incoming_headers["Authorization"] = (
        f"Bearer {credentials.credentials}"
    )

    response = requests.get(
        AGENT_API_URL + "/apps/app/users/user/sessions",
        headers=incoming_headers
    )

    return {
        "status_code": response.status_code,
        "response": (
            response.json()
            if "application/json" in response.headers.get("content-type", "")
            else response.text
        )
    }

@app.post("/create-agent-session")
def create_agent_session(payload: dict, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Forwards incoming request headers + payload to Cloud Run
    """

    # Copy incoming headers
    incoming_headers = dict(request.headers)

    # Remove problematic browser headers
    incoming_headers.pop("host", None)
    incoming_headers.pop("content-length", None)
    incoming_headers.pop("origin", None)
    incoming_headers.pop("referer", None)

    # Forward auth properly
    incoming_headers["Authorization"] = (
        f"Bearer {credentials.credentials}"
    )

    response = requests.post(
        AGENT_API_URL + "/apps/app/users/user/sessions",
        json=payload,
        headers=incoming_headers
    )

    return {
        "status_code": response.status_code,
        "response": (
            response.json()
            if "application/json" in response.headers.get("content-type", "")
            else response.text
        )
    }

def extract_response(response_json):

    final_text = None
    function_name = None

    for item in response_json:

        content = item.get("content", {})
        parts = content.get("parts", [])

        for part in parts:

            # Extract tool/function name
            if "functionCall" in part:
                function_name = part["functionCall"].get("name")

            # Extract final model text
            if "text" in part:
                final_text = part["text"]

    return {
        "tool_name": function_name,
        "message": final_text
    }

@app.post("/run-agent")
def run_agent(payload: dict, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Forwards incoming request headers + payload to Cloud Run
    """

    # Copy incoming headers
    incoming_headers = dict(request.headers)

    # Remove problematic browser headers
    incoming_headers.pop("host", None)
    incoming_headers.pop("content-length", None)
    incoming_headers.pop("origin", None)
    incoming_headers.pop("referer", None)

    # Forward auth properly
    incoming_headers["Authorization"] = (
        f"Bearer {credentials.credentials}"
    )

    response = requests.post(
        AGENT_API_URL + "/run",
        json=payload,
        headers=incoming_headers
    )

    return {
        "status_code": response.status_code,
        "response": (
            extract_response(response.json())
            if "application/json" in response.headers.get("content-type", "")
            else response.text
        )
    }
