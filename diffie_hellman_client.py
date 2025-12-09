#!/usr/bin/env python3
import socket
import argparse
import random
from pathlib import Path
from typing import Tuple


# TODO feel free to use this helper or not
def send_common_info(sock: socket.socket, server_address: str, server_port: int) -> Tuple[int, int]:
    # TODO: Connect to the server and propose a base number and prime
    # TODO: You can generate these randomly, or just use a fixed set
    
    # Primes under 100 for random selection
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    modulus = random.choice(primes)
    # Base should theoretically be a primitive root, but for this assignment any small int > 1 is fine
    # Ensuring base < modulus is standard
    base = random.randint(2, modulus - 1)
    
    message = f"{base}\n{modulus}\n"
    sock.sendall(message.encode())
    
    # TODO: Return the tuple (base, prime modulus)
    return base, modulus

# Do NOT modify this function signature, it will be used by the autograder
def dh_exchange_client(server_address: str, server_port: int) -> Tuple[int, int, int, int]:
    # TODO: Create a socket 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((server_address, server_port))
            print(f"Connected to server at {server_address}:{server_port}")
            
            # TODO: Send the proposed base and modulus number to the server using send_common_info
            base, modulus = send_common_info(sock, server_address, server_port)
            print(f"Sent base={base}, modulus={modulus}")

            # TODO: Come up with a random secret key

            # TODO: Calculate the message the client sends using the secret integer.

            # TODO: Exhange messages with the server

            # TODO: Calculate the secret using your own secret key and server message
            
            # TODO: Return the base number, the modulus, the private key, and the shared secret
        except ConnectionRefusedError:
            print(f"Connection refused by {server_address}:{server_port}")
            return (0, 0, 0, 0)

    # Placeholder return for now
    return (0, 0, 0, 0)


def main(args):
    if args.seed:
        random.seed(args.seed)
    
    dh_exchange_client(args.address, args.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a",
        "--address",
        default="127.0.0.1",
        help="The address the client will connect to.",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=8000,
        type=int,
        help="The port the client will connect to.",
    )
    parser.add_argument(
        "--seed",
        dest="seed",
        type=int,
        help="Random seed to make the exchange deterministic.",
    )
    # Parse options and process argv
    arguments = parser.parse_args()
    main(arguments)
