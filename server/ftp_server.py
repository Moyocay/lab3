import socket
import threading
import os

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100

# os.chdir('myfiles')


##################################
# TODO: Implement me for Part 1! #
##################################
def send_intro_message(conn):
    # TODO: Replace {ONID} with your ONID (mine is lyakhovs)
    #       and {MAJOR} with your major (i.e. CS, ECE, any others?)
    intro_message = "Hello! Welcome to my (villarmo) server! I'm majoring in CS\n"

    # TODO: Send this intro message to the client. Don't forget to encode() it!
    #       hint: use the `conn` handle and `sendall`!
    conn.sendall(str.encode(intro_message))


##################################
# TODO: Implement me for Part 2! #
##################################
def receive_long_message(conn):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = conn.recv(8, socket.MSG_WAITALL)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    data = b""
    full_data = b""
    bytes_received = 0

    # TODO: Receive all data
    #      1. Keep going until `bytes_received` is less than `data_length` (hint: use a loop)
    #      2. Receive a `CHUNK` of data (see `CHUNK` variable above)
    #      3. Update `bytes_received` and `full_data` variables

    while bytes_received < data_length:
        # Receive a CHUNK of data
        data = conn.recv(CHUNK)
        bytes_received += len(data)
        full_data += data

    
    return full_data.decode()

PASSWORD = "mypassword"  # Set your desired password here

def handle_client(conn):
    password = conn.recv(1024).decode().strip()

    incorrect_attempts = 0

    while incorrect_attempts < 3:
        if password == PASSWORD:
            send_intro_message(conn)  # Call the send_intro_message function
            message = receive_long_message(conn)
            print("Message from client:", message)
            conn.sendall(str.encode("Password is correct."))
            break
        else:
            incorrect_attempts += 1
            conn.sendall(str.encode("Incorrect password. Please try again: "))
            password = conn.recv(1024).decode().strip()

    if incorrect_attempts == 3:
        print("Too many incorrect password attempts. Closing connection.")
        conn.sendall(str.encode("Too many incorrect password attempts. Connection closed."))
    
    conn.close()

def main():
    # Configure a socket object to use IPv4 and TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Set interface and port
        server_socket.bind((INTERFACE, int(SPORT)))

        # Start listening for client connections (allow up to 5 connections to queue up)
        server_socket.listen(5)
        while True:
            # Accept a connection from a client
            conn, (client_host, client_port) = server_socket.accept()
            print("Connection received from:", client_host, "on port", client_port)

            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.start()

if __name__ == "__main__":
    main()
