# py.server
import socket
import sys
import os

FILES_DIR = "files"


def main():
    if len(sys.argv) != 2:
        print("Usage: py.server <port>") #thus how to run server
        return

    port = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port)) #bind to port
    s.listen(1) #wait for one connection

    while True:
        conn, _ = s.accept()
        conn.settimeout(1) #if not get answer in one minute bye bye bye

        while True:  # loop for keep-alive requests
            try:
                data = b""
                client_closed = False #assume client want to talk
                while b"\r\n\r\n" not in data:
                    input_client = conn.recv(1024)#get input line by line
                    if not input_client: #if not got input then we close connection
                        conn.close()
                        client_closed = True
                        break #get out of here
                    data += input_client
            except socket.timeout:
                conn.close()
                break

            if client_closed:  #if client closed bye bye
                break

            request = data.decode(errors="ignore")
            print(request, end="")  # Print

            lines = request.splitlines()
            if not lines:
                conn.close()
                break

            try:
                _, path, _ = lines[0].split()
            except ValueError:
                conn.close()
                break

            connection_header = "close"
            for line in lines:
                if line.lower().startswith("connection:"):
                    connection_header = line.split(":")[1].strip()

            # redirect
            if path == "/redirect":
                response = ( #if the redirect we told him it move and where it moved to
                    "HTTP/1.1 301 Moved Permanently\r\n"
                    "Connection: close\r\n"
                    "Location: /result.html\r\n"
                    "\r\n"
                )
                conn.sendall(response.encode())
                conn.close()
                break

            # now handle request
            if path == "/":
                path = "/index.html"
            elif path.endswith("/"):
                path = path + "index.html"

            file_path = os.path.join(FILES_DIR, path.lstrip("/"))

            if not os.path.isfile(file_path): #if the path no yo a file we have 
                response = (
                    "HTTP/1.1 404 Not Found\r\n" #tell him we dont have that
                    "Connection: close\r\n"
                    "\r\n"
                )
                conn.sendall(response.encode())
                conn.close()
                break

            # check if file special type or regular
            is_binary = file_path.endswith(".jpg") or file_path.endswith(".ico")
            mode = "rb" if is_binary else "r"
            #if special we nee dread as binary else read as text
            with open(file_path, mode) as f:
                content = f.read()
            #if text, encode to bytes so it can be sent over the socket
            if not is_binary:
                content = content.encode()

            response_headers = (
                "HTTP/1.1 200 OK\r\n" #ockie dockie
                f"Connection: {connection_header}\r\n"
                f"Content-Length: {len(content)}\r\n"
                "\r\n"
            )

            conn.sendall(response_headers.encode() + content)

            if connection_header.lower() == "close":
                conn.close()
                break  # wait for next client
            # else keep-alive we keep the connection

if __name__ == "__main__":  
    main()  # part 2:
