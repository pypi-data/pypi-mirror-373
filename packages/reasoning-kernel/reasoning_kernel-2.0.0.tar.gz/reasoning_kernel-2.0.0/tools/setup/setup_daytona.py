import os
from daytona import Daytona, DaytonaConfig

# The API key is set as an environment variable
api_key = os.environ.get("DAYTONA_API_KEY")
if not api_key:
    raise RuntimeError("DAYTONA_API_KEY environment variable not set")

# Initialize Daytona with the correct base URL (no /api suffix)
config = DaytonaConfig(api_key=api_key, api_url="https://app.daytona.io")
daytona = Daytona(config)

# Create a new sandbox
sandbox = daytona.create()

print(f"Sandbox created with ID: {sandbox.id}")

# Clone the Git repository inside the sandbox
repo_url = "https://github.com/Qredence/Reasoning-Kernel.git"
response = sandbox.process.code_run(f"git clone {repo_url}")

if response.exit_code != 0:
    print(f"Error cloning repository: {response.exit_code} {response.result}")
else:
    print("Repository cloned successfully.")
