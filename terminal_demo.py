import requests
import json

print("===== CLOUD COMMAND PARSER =====")

while True:
    command = input("\nEnter your command: ")

    if command.lower() == "exit":
        break

    try:
        response = requests.post(
            "http://127.0.0.1:8000/parse",
            json={"command": command}
        )

        print("\nModel Output:")
        print(json.dumps(response.json(), indent=4))

    except Exception as e:
        print("Error:", e)
