import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SERVICENOW_INSTANCE_URL")
user = os.getenv("SERVICENOW_USERNAME")
pw = os.getenv("SERVICENOW_PASSWORD")

print("URL:", repr(url))
print("Username:", repr(user))
print("Password length:", len(pw) if pw else None)
print("Password repr (shows hidden chars):", repr(pw))

resp = requests.get(
    f"{url}/api/now/table/incident?sysparm_limit=1",
    auth=(user, pw),
    headers={"Accept": "application/json"},
    timeout=15,
)
print("Status code:", resp.status_code)
print("Response snippet:", resp.text[:300])