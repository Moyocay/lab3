import socket

IP, DPORT = 'localhost', 8080

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

    # TODO: Receive data bytes one by one until a newline ('\n') is received
    #       1. Use a loop that keeps going until `data` equals '\n'
    #       2. Receive 1 byte and set it to the `data` variable
    #       3. Add `data` to `full_data`
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


def main():

    # Configure a socket object to use IPv4 and TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:

        # Connect to the server
        conn.connect((IP, int(DPORT)))

        """
        Part 1: Introduction
        """
        # TODO: receive the introduction message by implementing `recv_intro_message` above.
        intro = recv_intro_message(conn)

        # TODO: print the received message to the screen
        print(intro)

        """
        Part 2: Long Message Exchange Protocol
        """
        long_msg = input("Please enter a message to send to the server: ")

        # TODO: Send message to the server by implementing `send_long_message` above.
        send_long_message(conn, long_msg)


    print("Sent:", long_msg)
    return 0

# Run the `main()` function
if __name__ == "__main__":
    main()
