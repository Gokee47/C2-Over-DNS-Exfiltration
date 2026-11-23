python
import math

def calculate_entropy(data):
    if not data: return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(chr(x)))/len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

print("[*] Scanning Zeek dns.log for C2 Commands and Data...")
found = False

with open('dns.log', 'r') as f:
    for line in f:
        if "evil.com" in line and not line.startswith("#"):
            parts = line.strip().split('\t')
            if len(parts) > 9:
                query = parts[9]
                if "poll.evil.com" in query or "data.evil.com" in query:
                    print(f"[ALERT] Suspicious DNS Query Detected: {query}")
                    found = True

if not found:
    print("[-] No suspicious queries found.")
