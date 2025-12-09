#!/usr/bin/env python3
import socket
import argparse
import random
from pathlib import Path
from typing import Tuple


# TODO feel free to use this helper or not
def receive_common_info(f_obj) -> Tuple[int, int]:
    # TODO: Wait for a client message that sends a base number.
    try:
        # Read two lines: base and modulus
        base_line = f_obj.readline()
        mod_line = f_obj.readline()
        
        if not base_line or not mod_line:
            raise ValueError("Connection closed unexpectedly")
            
        base = int(base_line.strip())
        modulus = int(mod_line.strip())
        return base, modulus
    except ValueError as e:
        print(f"Error parsing common info: {e}")
        return 0, 0
    
    # TODO: Return the tuple (base, prime modulus)

# Do NOT modify this function signature, it will be used by the autograder
def dh_exchange_server(server_address: str, server_port: int) -> Tuple[int, int, int, int]:
    # TODO: Create a server socket. can be UDP or TCP.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_address, server_port))
        sock.listen(1)
        print(f"Server listening on {server_address}:{server_port}...")

        conn, addr = sock.accept()
        with conn:
            print(f"Connected by {addr}")
            
            # Use makefile for easier line-by-line reading
            with conn.makefile('r', encoding='utf-8') as f_obj:

                # TODO: Read client's proposal for base and modulus using receive_common_info
                base, modulus = receive_common_info(f_obj)
                print(f"Received base={base}, modulus={modulus}")
    
                # TODO: Generate your own secret key
                # Secret should be in range [2, modulus-2]
                secret_key = random.randint(2, max(2, modulus - 2))
                print(f"Secret is {secret_key}")
                
                # Compute server public value: (base ^ secret_key) % modulus
                public_value = pow(base, secret_key, modulus)
    
                # TODO: Exchange messages with the client
                # Receive client public value first
                line = f_obj.readline()
                if not line:
                    print("Connection closed by client")
                    return (0, 0, 0, 0)
                
                client_public_value = int(line.strip())
                print(f"Int received from peer is {client_public_value}")
                
                # Send server public value
                conn.sendall(f"{public_value}\n".encode())
    
                # TODO: Compute the shared secret.
                # Shared Secret = (client_public_value ^ secret_key) % modulus
                shared_secret = pow(client_public_value, secret_key, modulus)
                print(f"Shared secret is {shared_secret}")
    
                # TODO: Return the base number, prime modulus, the secret integer, and the shared secret
                return base, modulus, secret_key, shared_secret

def main(args):
    dh_exchange_server(args.address, args.port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--address",
        default="127.0.0.1",
        help="The address the server will bind to.",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=8000,
        type=int,
        help="The port the server will listen on.",
    )
    # Parse options and process argv
    arguments = parser.parse_args()
    main(arguments)
