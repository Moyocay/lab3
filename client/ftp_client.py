import socket
import os


IP, DPORT = 'localhost', 8080
CHUNK = 100
PWD_CORRECT = "Password is correct."
PWD_INCORRECT = "Incorrect password. Please try again: "
PWD_TOO_MANY_ATTEMPTS = "Too many incorrect password attempts. Connection closed."
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MYFILES_DIR = os.path.join(SCRIPT_DIR, 'myfiles')


# Helper function that converts an integer into a string of 8 hexadecimal digits
# Assumption: integer fits in 8 hexadecimal digits
def to_hex(number):
    # Verify our assumption: error is printed and program exists if assumption is violated
    assert number <= 0xffffffff, "Number too large"
    return "{:08x}".format(number)

##################################
# TODO: Implement me for Part 1! #
##################################
def recv_intro_message(conn):
    
    full_data = b""
    data = b""

    while data != b"\n":
        data = conn.recv(1)
        full_data += data

    return full_data.decode()
    


##################################
# TODO: Implement me for Part 2! #
##################################
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

def receive_long_message(conn):
    data_length_hex = conn.recv(8, socket.MSG_WAITALL)
    data_length = int(data_length_hex, 16)

    data = b""
    full_data = b""
    bytes_received = 0

    while bytes_received < data_length:
        data = conn.recv(CHUNK)
        bytes_received += len(data)
        full_data += data

    return full_data.decode()

# Command implementations

def list_files(conn):
    send_long_message(conn, "list")
    response = receive_long_message(conn)
    if response.startswith("ACK"):
        print(response[4:])
    else:
        print(response)

def put_file(conn, filename):
    filepath = os.path.join(MYFILES_DIR, filename)
    if not os.path.exists(filepath):
        print("File does not exist")
        return

    send_long_message(conn, f"put {filename}")
    with open(filepath, 'rb') as file:
        file_content = file.read().decode()
    send_long_message(conn, file_content)
    response = receive_long_message(conn)
    print(response)

def get_file(conn, filename):
    send_long_message(conn, f"get {filename}")
    response = receive_long_message(conn)
    if response.startswith("NAK"):
        print(response)
        return

    file_content = receive_long_message(conn)
    filepath = os.path.join('myfiles', filename)
    with open(filepath, 'wb') as file:
        file.write(file_content.encode())
    print("File downloaded successfully")

def remove_file(conn, filename):
    send_long_message(conn, f"remove {filename}")
    response = receive_long_message(conn)
    print(response)

def close_connection(conn):
    send_long_message(conn, "close")
    response = receive_long_message(conn)
    if response.startswith("ACK"):
        conn.close()


def main():

    # Configure a socket object to use IPv4 and TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:

        isAuth = False
        # Connect to the server
        conn.connect((IP, int(DPORT)))

        password_prompt = conn.recv(1024).decode()
        print(password_prompt)

        while True:
            password = input("Enter the password: ")
            send_long_message(conn, password)

            password_response = receive_long_message(conn)

            print(password_response[4:])

            if password_response.startswith("ACK"):
                isAuth = True
                send_long_message(conn, "ACK")
                break
            elif password_response.startswith("NACK"):
                return 0

        if isAuth:

            # TODO: receive the introduction message by implementing `recv_intro_message` above.
            intro = recv_intro_message(conn)
            # TODO: print the received message to the screen
            print(intro)

            while True:
                command = input("Enter command (list, put, get, remove, close): ")
                if command == "close":
                    close_connection(conn)
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
                    print("Unknown command")
            
  
    return 0

# Run the `main()` function
if __name__ == "__main__":
    main()

