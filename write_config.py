import base64

# Base64 encoded config.py (generated separately)
encoded = ""
# We'll write the encoded content here

with open("config_b64.txt", "r") as f:
    encoded = f.read().strip()

decoded = base64.b64decode(encoded)
with open("src/coding_agent/config.py", "wb") as f:
    f.write(decoded)

print("config.py written from base64")