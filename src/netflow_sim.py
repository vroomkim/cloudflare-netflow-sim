import socket
import struct
import time
import random
import argparse
import sys

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)

def send_netflow(dest_ip, dest_port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    src_prefixes = ["100.1.1.", "212.10.11."]
    start_time = time.time()
    
    print(f"Sending NetFlow v5 to {dest_ip}:{dest_port}...")
    
    while True:
        if duration > 0 and (time.time() - start_time) > (duration * 60):
            break
        
        # NetFlow v5 Header
        version, count = 5, 1
        sys_uptime = int(time.time() * 1000) & 0xFFFFFFFF
        unix_secs = int(time.time())
        unix_nsecs, flow_seq, engine_type, engine_id, sampling = 0, random.randint(1, 1000), 0, 0, 0
        header = struct.pack('!HHIIIIBBH', version, count, sys_uptime, unix_secs, unix_nsecs, flow_seq, engine_type, engine_id, sampling)

        # Traffic Randomization
        src_ip_str = random.choice(src_prefixes) + str(random.randint(1, 254))
        dst_ip_str = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
        rand_proto = random.random()
        if rand_proto < 0.5: prot, s_port, d_port = 6, random.randint(1024, 65535), random.choice([80, 443, 8080])
        elif rand_proto < 0.7: prot, s_port, d_port = 17, random.randint(1024, 65535), 53
        elif rand_proto < 0.85: prot, s_port, d_port = 6, random.randint(1024, 65535), 22
        else: prot, s_port, d_port = 1, 0, 0

        # Flow Record
        src_ip = socket.inet_aton(src_ip_str)
        dst_ip = socket.inet_aton(dst_ip_str)
        nexthop = socket.inet_aton("0.0.0.0")
        input_if, output_if = 1, 2
        packets = random.randint(1, 500)
        octets = packets * random.randint(40, 1500)
        first, last = sys_uptime - 1000, sys_uptime
        tcp_flags, tos, src_as, dst_as, src_mask, dst_mask = 0, 0, 0, 0, 24, 24

        record = struct.pack('!4s4s4sHHIIIIHHBBHBBHH', 
            src_ip, dst_ip, nexthop, input_if, output_if, 
            packets, octets, first, last, s_port, d_port, 
            0, tcp_flags, prot, tos, src_as, dst_as, src_mask, dst_mask)

        sock.sendto(header + record, (dest_ip, dest_port))
        time.sleep(0.05)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="162.159.65.1")
    parser.add_argument("--port", type=int, default=2055)
    parser.add_argument("--duration", type=int, default=0)
    args = parser.parse_args()
    send_netflow(args.ip, args.port, args.duration)
