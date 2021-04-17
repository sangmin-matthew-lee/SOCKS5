import socket
import struct
import serializeme

def resolve():

    print("hello")
    
    PORT = 1080
    HOST = 'localhost'
    sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sd.bind((HOST, PORT))
    print("Server IP {} Listening on Port {}".format(HOST, PORT))
    sd.listen(1)

    client_greeting = serializeme.Serialize({
        "VER":("1B", 5),
        "NAUTH":("1B", 2),
        "AUTH":("1B", 2)
    })
    #same =

    server_choice = {
        "VER": ("1B"),
        "CAUTH":("1B")
    }

    client_auth_request = {
        "VER":("1B"),
        "IDLEN":("1B"),
        "ID":("255B"),
        "PWLEN":("1B"),
        "PW":("255B")
    }

    server_response = {
        "VER":("1B"),
        "STATUS":("1B")
    }

    sockst_add = {
        "TYPE":("1B"),
        "ADDR": ("4B")
    }

    client_connection_req = {
        "VER":("1B"),
        "CMD":("1B"),
        "RSV":("1B"),
        "DEST_ADDR":("4B"),
        "DEST_PORT":("2B")
    }
"""  
    PORT = 1080
    HOST = 'localhost'
    sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sd.bind((HOST, PORT))
    print("Server IP {} Listening on Port {}".format(HOST, PORT))
    sd.listen(1)

    while True:
        # Wait for a connection
        print('Waiting for a client connection')
        # connection established
        connection, client_address = sd.accept()
"""


if __name__ == '__main__':
    resolve()
