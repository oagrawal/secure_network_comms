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
    # TODO: Return the tuple (base, prime modulus)
    pass

# Do NOT modify this function signature, it will be used by the autograder
def dh_exchange_client(server_address: str, server_port: int) -> Tuple[int, int, int, int]:
    # TODO: Create a socket 
    
    # TODO: Send the proposed base and modulus number to the server using send_common_info

    # TODO: Come up with a random secret key

    # TODO: Calculate the message the client sends using the secret integer.

    # TODO: Exhange messages with the server

    # TODO: Calculate the secret using your own secret key and server message
    
    # TODO: Return the base number, the modulus, the private key, and the shared secret

    pass


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
