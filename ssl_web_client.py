#!/usr/bin/env python3
import ssl
import pprint
import socket
import argparse
from typing import Dict, Any
from pathlib import Path

'''
Simple script that creates a TCP client (optionally secured by SSL). This
client connects to a host and then simply fires off a single HTTP GET request.
If using SSL/HTTPS, it should also print the certificate.
'''

def craft_http_request(host: str, path: str) -> str:
    return f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

def create_socket(host: str, port: int, use_ssl: bool) -> socket.socket | ssl.SSLSocket:
    base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if use_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_socket = ssl_context.wrap_socket(base_socket, server_hostname=host)
        ssl_socket.connect((host, port))
        return ssl_socket
    else:
        base_socket.connect((host, port))
        return base_socket


def get_peer_certificate(ssl_socket: ssl.SSLSocket) -> Dict[str, Any]:
    return ssl_socket.getpeercert()

def send_http_request(s: socket.socket | ssl.SSLSocket, request_string: str) -> str:
    s.sendall(request_string.encode())
    response = s.recv(1024)
    return response.decode()


def main(args):
    s = create_socket(args.host, args.port, args.ssl)

    if (args.ssl):
        cert = get_peer_certificate(s)
        pprint.pprint(cert)

    request = craft_http_request(args.host, args.document)
    response = send_http_request(s, request)

    print("========================= HTTP Response =========================")
    print(response)
    s.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "host",
        default="www.example.com",
        type=str,
        help="The url/host we connect to",
    )

    parser.add_argument(
        "-d",
        "--document",
        default="/",
        type=str,
        help="The path to the document/webpage we want to retrieve"
    )

    parser.add_argument(
        "--ssl",
        action="store_true",
    )

    parser.add_argument(
        "-p",
        "--port",
        default=80,
        type=int,
        help="The port we connect to",
    )

    # Parse options and process argv
    arguments = parser.parse_args()
    main(arguments)
