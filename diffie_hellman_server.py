#!/usr/bin/env python3
import socket
import argparse
import random
from pathlib import Path
from typing import Tuple


# TODO feel free to use this helper or not
def receive_common_info(conn: socket.socket) -> Tuple[int, int]:
    # TODO: Wait for a client message that sends a base number.
    data = conn.recv(1024).decode()
    if not data:
        raise ValueError("Connection closed by client before sending common info")
    
    try:
        parts = data.strip().split('\n')
        if len(parts) < 2:
             # Handle case where data might be fragmented (though unlikely for this small amount)
             # Ideally we'd buffer, but for this assignment simple recv is usually okay
             raise ValueError(f"Received incomplete data: {data}")
             
        base = int(parts[0])
        modulus = int(parts[1])
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

            # TODO: Read client's proposal for base and modulus using receive_common_info
            base, modulus = receive_common_info(conn)
            print(f"Received base={base}, modulus={modulus}")

            # TODO: Generate your own secret key

            # TODO: Exchange messages with the client

            # TODO: Compute the shared secret.

            # TODO: Return the base number, prime modulus, the secret integer, and the shared secret
            # Placeholder return for now to allow testing
            return (0, 0, 0, 0)

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
