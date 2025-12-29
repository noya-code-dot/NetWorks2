import socket
import sys
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: py.client <server_ip> <server_port>")
        return

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    while True:
        path = input().strip()
        if not path:
            continue

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, server_port))
        #FORMAT THE REQUEST
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        s.sendall(request.encode())

        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data

        s.close()

        header_end = response.find(b"\r\n\r\n")
        headers = response[:header_end].decode(errors="ignore")
        body = response[header_end + 4:]

        status_line = headers.splitlines()[0]
        print(status_line) #ONLY FIRST LINE AS REQUESTED

        if status_line == "HTTP/1.1 200 OK":
            ext = os.path.splitext(path)[1].lower()
            if ext in [".jpg", ".ico"]:
                filename = os.path.basename(path)
                with open(filename, "wb") as f:
                    f.write(body)

if __name__ == "__main__":
    main()
