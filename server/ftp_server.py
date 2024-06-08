import socket
import threading
import os
import socket
import threading

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100
PASSWORD = "mypassword"  # Set your desired password here
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MYFILES_DIR = os.path.join(SCRIPT_DIR, 'myfiles')
# os.chdir('myfiles')


def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)

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

def send_long_message(conn, message):
    
    # TODO: Remove the line below when you start implementing this function!
    # raise NotImplementedError("Not implemented yet!")

    # TODO: Send the length of the message: this should be 8 total hexadecimal digits
    #       This means that ffffffff hex -> 4294967295 dec
    #       is the maximum message length that we can send with this method!
    #       hint: you may use the helper function `to_hex`. Don't forget to encode before sending!

    message_lenght = len(message.encode())

    assert message_lenght <= 0xffffffff, "Message too large for this protocol..."

    message_lenght_hex = to_hex(message_lenght)

    # Send lenght
    conn.sendall(message_lenght_hex.encode())

    # TODO: Send the message itself to the server. Don't forget to encode before sending!
    
    # Send encoded message
    conn.sendall(message.encode())


def list_files(conn):
    try:
        files = os.listdir(MYFILES_DIR)
        files_list = "\n".join(files)
        send_long_message(conn, "ACK\n" + files_list)
    except Exception as e:
        send_long_message(conn, f"NAK {str(e)}")

def put_file(conn, filename):
    try:
        filepath = os.path.join(MYFILES_DIR, filename)
        file_content = receive_long_message(conn)
        with open(filepath, 'wb') as file:
            file.write(file_content.encode())
        send_long_message(conn, "ACK File uploaded successfully")
    except Exception as e:
        send_long_message(conn, f"NAK {str(e)}")

def get_file(conn, filename):
    try:
        filepath = os.path.join(MYFILES_DIR, filename)
        if not os.path.exists(filepath):
            send_long_message(conn, "NAK File not found")
            return

        with open(filepath, 'rb') as file:
            file_content = file.read().decode()
        send_long_message(conn, "ACK")
        send_long_message(conn, file_content)
    except Exception as e:
        send_long_message(conn, f"NAK {str(e)}")

def remove_file(conn, filename):
    try:
        filepath = os.path.join(MYFILES_DIR, filename)
        if not os.path.exists(filepath):
            send_long_message(conn, "NAK File not found")
            return

        os.remove(filepath)
        send_long_message(conn, "ACK File removed successfully")
    except Exception as e:
        send_long_message(conn, f"NAK {str(e)}")


def handle_client(conn):
    conn.sendall("Password required...".encode())
    incorrect_attempts = 0

    while incorrect_attempts < 3:
        password = receive_long_message(conn)
        if password == PASSWORD:
            send_long_message(conn, "ACK Password is correct")
            confirm_ack = receive_long_message(conn)
            if confirm_ack == "ACK":
                send_intro_message(conn)  # Call the send_intro_message function
            break
        else:
            incorrect_attempts += 1
            if incorrect_attempts == 3:
                print("Too many incorrect password attempts. Closing connection.")
                send_long_message(conn, "NACK Too many incorrect password attempts. Connection closed.")
                conn.close()
                return
            else:
                send_long_message(conn, "NAK Incorrect password. Please try again...")

    while True:
        command = receive_long_message(conn)
        if command == "close":
            send_long_message(conn, "ACK")
            conn.close()
            break
        elif command == "list":
            list_files(conn)
        elif command.startswith("put "):
            filename = command[4:]
            put_file(conn, filename) 
        elif command.startswith("get "):
            filename = command[4:]
            get_file(conn, filename)
        elif command.startswith("remove "):
            filename = command[7:]
            remove_file(conn, filename)
        else:
            send_long_message(conn, "NAK Unknown command")

    # Close the connection
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
