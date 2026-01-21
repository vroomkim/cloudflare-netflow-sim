import socket
import struct
import time
import random
import argparse
import sys

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)

def generate_random_ip():
    """Generates a completely random IP address (The Internet)"""
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def generate_subnet_ip():
    """Generates a random IP from your specific target subnets"""
    # Target Prefixes: 100.1.1.0/24 and 212.10.11.0/24
    prefix = random.choice(["100.1.1", "212.10.11"])
    return f"{prefix}.{random.randint(1, 254)}"

def send_netflow(dest_ip, dest_port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    last_log_time = start_time
    
    # Configuration
    SAMPLING_RATE = 1000 
    SPEED_HIGH = 0.002  # High Volume
    SPEED_HALF = 0.02   # Half Volume
    SPEED_LOW  = 0.2    # Low Volume
    
    current_phase = ""

    print(f"Starting INBOUND Traffic Simulation to {dest_ip}:{dest_port}")
    print(f"Traffic Direction: Random Internet (Src) -> Your Subnets (Dst)")
    print(f"Cycle: 5m High -> 5m Low -> 40m High -> 5m Half -> 5m Low")

    while True:
        now = time.time()
        elapsed_total = now - start_time
        
        if duration > 0 and elapsed_total > (duration * 60):
            print("Total duration reached. Stopping.")
            break
        
        cycle_pos = elapsed_total % 3600 
        
        # --- PATTERN LOGIC (In Seconds) ---
        if cycle_pos < 300:        # 0 - 5 mins
            sleep_time = SPEED_HIGH
            phase_name = "HIGH VOLUME (5m)"
        elif cycle_pos < 600:      # 5 - 10 mins
            sleep_time = SPEED_LOW
            phase_name = "LOW VOLUME (5m)"
        elif cycle_pos < 3000:     # 10 - 50 mins
            sleep_time = SPEED_HIGH
            phase_name = "HIGH VOLUME (40m)"
        elif cycle_pos < 3300:     # 50 - 55 mins
            sleep_time = SPEED_HALF
            phase_name = "HALF VOLUME (5m)"
        else:                      # 55 - 60 mins
            sleep_time = SPEED_LOW
            phase_name = "LOW VOLUME (5m)"

        # Logging
        if phase_name != current_phase:
            m, s = divmod(int(elapsed_total), 60)
            print(f"[{m}m {s}s total] PHASE SWITCH -> {phase_name}")
            current_phase = phase_name
            
        if (now - last_log_time) > 60:
            m, s = divmod(int(elapsed_total), 60)
            print(f"   ... [{m}m {s}s] Still running: {phase_name}")
            last_log_time = now

        # --- NetFlow Header (v5) ---
        version, count = 5, 1
        sys_uptime = int(time.time() * 1000) & 0xFFFFFFFF
        unix_secs = int(time.time())
        unix_nsecs, flow_seq, engine_type, engine_id = 0, random.randint(1, 1000), 0, 0
        sampling = SAMPLING_RATE
        header = struct.pack('!HHIIIIBBH', version, count, sys_uptime, unix_secs, unix_nsecs, flow_seq, engine_type, engine_id, sampling)

        # --- CHANGED: IP Direction Logic ---
        # Source is now RANDOM (Simulating the Internet/Attackers)
        src_ip_str = generate_random_ip()
        
        # Destination is now YOUR SUBNET (Simulating your infrastructure)
        dst_ip_str = generate_subnet_ip()
        
        rand_proto = random.random()
        if rand_proto < 0.5: prot, s_port, d_port = 6, random.randint(1024, 65535), random.choice([80, 443, 8080])
        elif rand_proto < 0.7: prot, s_port, d_port = 17, random.randint(1024, 65535), 53
        elif rand_proto < 0.85: prot, s_port, d_port = 6, random.randint(1024, 65535), 22
        else: prot, s_port, d_port = 1, 0, 0

        # Packing the record
        src_ip = socket.inet_aton(src_ip_str)
        dst_ip = socket.inet_aton(dst_ip_str)
        nexthop = socket.inet_aton("0.0.0.0")
        input_if, output_if = 1, 2
        packets = random.randint(1, 50) 
        octets = packets * random.randint(64, 1500)
        first, last = sys_uptime - 1000, sys_uptime
        tcp_flags, tos, src_as, dst_as, src_mask, dst_mask = 0, 0, 0, 0, 24, 24
        pad1, pad2 = 0, 0

        record = struct.pack('!4s4s4sHHIIIIHHBBBBHHBBH', 
            src_ip, dst_ip, nexthop, input_if, output_if, 
            packets, octets, first, last, s_port, d_port, 
            pad1, tcp_flags, prot, tos, src_as, dst_as, src_mask, dst_mask, pad2)

        sock.sendto(header + record, (dest_ip, dest_port))
        time.sleep(sleep_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="162.159.65.1")
    parser.add_argument("--port", type=int, default=2055)
    parser.add_argument("--duration", type=int, default=0)
    args = parser.parse_args()
    send_netflow(args.ip, args.port, args.duration)
