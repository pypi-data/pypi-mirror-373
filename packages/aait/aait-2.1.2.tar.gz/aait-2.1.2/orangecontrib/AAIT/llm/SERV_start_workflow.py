import subprocess


workflow_key = "Acuity_RAG"


# Step 1: Start the workflow
start_command = [
    "curl",
    "-X", "GET",
    f"http://localhost:8000/start-workflow/{workflow_key}",
    "-H", "accept: application/json"
]

start_result = subprocess.run(start_command, capture_output=True, text=True)
print("Start Workflow - Status Code:", start_result.returncode)
print("Start Workflow - Output:", start_result.stdout)