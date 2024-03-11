from socket import *
import os

def get_from_cache(filename):
    """Check if the file is in the cache and return its content if available."""
    try:
        print(f"Trying to retrieve {filename} from cache...")
        with open(f"cache/{filename}", "rb") as f:
            print(f"Cache hit for {filename}")
            return f.read()
    except FileNotFoundError:
        print(f"Cache miss for {filename}")
        return None

def save_to_cache(filename, data):
    """Save the fetched data to cache."""
    print(f"Saving {filename} to cache...")
    os.makedirs("cache", exist_ok=True)
    with open(f"cache/{filename}", "wb") as f:
        f.write(data)
    print(f"Saved {filename} to cache successfully.")

def fetch_from_server(hostname, port, resource_path):
    """Fetch content from the actual web server."""
    print(f"Fetching {resource_path} from server {hostname}:{port}...")
    # Create a TCP/IP socket
    tempSocket = socket(AF_INET, SOCK_STREAM)
    
    try:
        # Connect to the web server
        tempSocket.connect((hostname, port))
        getRequest = f"GET /{resource_path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
    
        # Send the GET request
        tempSocket.send(getRequest.encode())
        print(f"Sent GET request for {resource_path} to {hostname}:{port}")
        
        # Receive the response from the web server
        response = b""
        while True:
            recvData = tempSocket.recv(2048)
            if not recvData:
                break
            response += recvData
        response1 = response.split("\r\n\r\n".encode(), 1)[1]
        print(f"Received response from server for {resource_path}")
        return response1
    
    except Exception as e:
        print(f"Error fetching from server: {e}")
        return None
    
    finally:
        # Close the connection
        tempSocket.close()

serverPort = 8888
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print("The proxy server is ready to serve...")

while True:
    connectionSocket, addr = serverSocket.accept()
    print(f"Accepted connection from {addr}")
    try:
        message = connectionSocket.recv(2048).decode()
        print(f"Received request: {message}")
        fieldname = message.split()[1]
        split_name = fieldname.split("/")
        connection_info = split_name[1].split(":")
        host = connection_info[0]
        if len(connection_info) == 1:
            port = '80'
        else:
            port = connection_info[1]
        filename = split_name[2]

        # name to put into cache
        joinedname = host + "+" + port + "+" + filename
        outputdata = get_from_cache(joinedname)
        if outputdata is None:
            # If not in cache, fetch from server and cache it
            outputdata = fetch_from_server(host, int(port), filename)
            if outputdata:
                save_to_cache(joinedname, outputdata)
        if outputdata:
            connectionSocket.send(bytes('HTTP/1.1 200 OK\r\n\r\n', "ascii"))
            connectionSocket.send(outputdata)
            print(f"Served {joinedname} to client")
        else:
            # Send 404 if the file wasn't found in cache and couldn't be fetched
            connectionSocket.send(bytes("HTTP/1.1 404 Not Found\r\n\r\n", "ascii"))
            print(f"Sent 404 Not Found for {joinedname}")
    except IOError as e:
        print(f"IOError occurred: {e}")
        connectionSocket.send(bytes("HTTP/1.1 500 Internal Server Error\r\n\r\n", "ascii"))
    finally:
        connectionSocket.close()
        print(f"Connection closed with {addr}")

serverSocket.close()
