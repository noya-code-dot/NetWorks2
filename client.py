import socket
import sys
import os

def main():
    if len(sys.argv) != 3: #need in good format
        print("Usage: py.client <server_ip> <server_port>")
        return

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    s = None #start no socket

    while True:
        path = input().strip()
        if not path: #not answer no need
            continue

        #we want to check if the socket still active,probloms accour if is not
        if s is not None:
            try:
                request = "."
                s.sendall(request.encode())
                response = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
            except (socket.error, ConnectionResetError, ConnectionAbortedError):
                s.close() #tha means that the sever shut down its side so we need to close our too
                s = None

        if s is None: #if no socket make new connection
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, server_port))


        request = ( #format request
            f"GET {path} HTTP/1.1\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n"
        )
        s.sendall(request.encode()) #send

        response = b"" #read answer
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        #pick the answer apart
        header_end = response.find(b"\r\n\r\n")
        headers = response[:header_end].decode(errors="ignore")
        body = response[header_end + 4:]

        #check if server want to close our connection
        connection_close = False
        for line in headers.splitlines():
            if line.lower().startswith("connection:") and "close" in line.lower():
                connection_close = True

        status_line = headers.splitlines()[0]
        print(status_line)  # ONLY FIRST LINE AS REQUESTED

        #is server chose to close the connection we need to respect that consent is importment
        if connection_close:
            if s:
                s.close()
            s = None
        #if the queires yeald good result and was a picture we save it
        if status_line == "HTTP/1.1 200 OK":
            ext = os.path.splitext(path)[1].lower()
            if ext in [".jpg", ".ico"]:
                filename = os.path.basename(path)
                with open(filename, "wb") as f:
                    f.write(body)

if __name__ == "__main__":
    main()
