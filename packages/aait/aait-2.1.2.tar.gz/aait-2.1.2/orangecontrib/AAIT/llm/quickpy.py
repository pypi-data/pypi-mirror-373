import subprocess
import json
import time

# # Step 1: Start the workflow
# start_command = [
#     "curl",
#     "-X", "GET",
#     "http://localhost:8000/start-workflow/Acuity_RAG",
#     "-H", "accept: application/json"
# ]
#
# start_result = subprocess.run(start_command, capture_output=True, text=True)
# print("Start Workflow - Status Code:", start_result.returncode)
# print("Start Workflow - Output:", start_result.stdout)
#
# time.sleep(30)


#########################
#########################


# Step 2: Send input data
question = "Qu'est-ce qu'un millésime ?"
workflow_id = "Acuity.ows"
input_id = "chatbotInput1"

payload = {
    "workflow_id": workflow_id,
    "data": [
        {
            "num_input": input_id,
            "values": [
                ["content"],
                ["str"],
                [[question]]
            ]
        }
    ]
}

json_data = json.dumps(payload)
escaped_json = json_data.replace('"', '\\"')  # Escape quotes for shell

input_command = f"""curl --location "http://127.0.0.1:8000/input-workflow" \
--header "Content-Type: application/json" \
--data "{escaped_json}" """

input_result = subprocess.run(input_command, shell=True, capture_output=True, text=True)
print("\nSend Input - STDOUT:\n", input_result.stdout)
print("Send Input - STDERR:\n", input_result.stderr)
print("Send Input - Return Code:", input_result.returncode)





# Step 3: Poke the workflow to get the progress / results
print("\nWaiting for workflow to complete...")
output_command = ["curl", "--location", f"http://127.0.0.1:8000/output-workflow/{workflow_id}"]
timeout = 600
k = 0
while k < timeout:
    output_result = subprocess.run(output_command, capture_output=True)
    stdout_utf8 = output_result.stdout.decode("utf-8")
    parsed_response = json.loads(stdout_utf8)
    print(parsed_response)
    if parsed_response["_result"] is None:
        print("Progress:", parsed_response["_statut"])
    else:
        break
    time.sleep(1)
    k += 1
print("\nRaw Output:\n", stdout_utf8)





# Step 4: Parse and get the results
try:
    parsed_response = json.loads(stdout_utf8)
    print("\nParsed Response:\n", parsed_response)
    question = parsed_response["_result"][0]["content"]
    answer = parsed_response["_result"][0]["Answer"]
    print("\nQuestion:", question)
    print("\nAnswer:", answer)
except json.JSONDecodeError as e:
    print("Failed to parse JSON:", e)
except (KeyError, IndexError) as e:
    print("Unexpected response structure:", e)



# .bat pour lancer server
# .py pour lancer workflow sans GUI
# faire fichier dans Parameters
# rajouter while pour voir le progress