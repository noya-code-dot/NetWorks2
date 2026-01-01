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

        request = ( #format request
            f"GET {path} HTTP/1.1\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n"
        )
        success  = False
        #the problom when the sever close because timeout but the client disnt know so it doesnt close its connection and try to send but the server closed it side
        while not success :
            if s is None: #if no socket make new connection
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((server_ip, server_port))
            try:
                s.sendall(request.encode())
                response = b""
                while b"\r\n\r\n" not in response:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
                if b"\r\n\r\n" not in response:
                    continue  #while not success
                success = True #else that was successful trasction
            except (socket.error, ConnectionResetError, ConnectionAbortedError):
                s.close() #tha means that the sever shut down its side so we need to close our too
                s = None


        #pick the answer apart
        header_end = response.find(b"\r\n\r\n")
        headers = response[:header_end].decode(errors="ignore")
        body = response[header_end + 4:]

        #check if server want to close our connection
        connection_close = False
        for line in headers.splitlines():
            if line.lower().startswith("connection:") and "close" in line.lower():
                connection_close = True
        content_length = None
        for line in headers.splitlines():
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())

        # קרא את כל ה-body!
        if content_length is not None:
            while len(body) < content_length:
                data = s.recv(4096)
                if not data:
                    break
                body += data
        status_line = headers.splitlines()[0]
        print(status_line)  # ONLY FIRST LINE AS REQUESTED

        #is server chose to close the connection we need to respect that consent is importment
        if connection_close:
            if s:
                s.close()
            s = None
        #if the queires yeald good result
        # Save ALL files with status 200
        if status_line == "HTTP/1.1 200 OK":
            filename = os.path.basename(path)
            if not filename or filename == "":
                filename = "index.html"  # If path is "/", save as index.html
            
            with open(filename, "wb") as f:
                f.write(body)

if __name__ == "__main__":
    main()
