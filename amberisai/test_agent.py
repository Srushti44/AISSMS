import requests
import json

response = requests.post(
    "http://localhost:5000/agent",
    json={
        "query": "my baby is crying what do i do",
        "baby_id": 1
    },
    stream=True
)

print("Status:", response.status_code)
for line in response.iter_lines():
    if line:
        decoded = line.decode('utf-8')
        if decoded.startswith("data:"):
            raw = decoded[5:].strip()
            if raw == "[DONE]":
                break
            try:
                parsed = json.loads(raw)
                if "text" in parsed:
                    print(parsed["text"], end="", flush=True)
                elif "error" in parsed:
                    print("ERROR:", parsed["error"])
            except:
                pass

print("\n\nDone!")