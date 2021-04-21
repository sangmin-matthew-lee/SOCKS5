import socket
import serializeme
import struct


def resolve():
    print("Hello")

    PORT = 1080
    HOST = 'localhost'
    sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sd.bind((HOST, PORT))
    sd.listen(1)

    #print(sd)

    while True:
        print('Waiting for a client connection')

        connection, client_address = sd.accept()
        with connection:
            print("Connected by", client_address)
            rsp = connection.recv(1024)

            #section 3
            decode_client_greeting = serializeme.Deserialize(
                rsp, {
                    "VER": ("1B"),
                    "NAUTH": ("1B", "", "AUTH"),
                    "AUTH": {
                        "Name": "1B"
                    }
                })

            server_choice = serializeme.Serialize({
                "VER": ("1B", 5),
                "METHOD": ("1B", 2)
            })
            connection.sendall(server_choice.packetize())

            #subsequent authentication
            rsp = connection.recv(1024)
            decode_request = serializeme.Deserialize(rsp, {
                "VER": "1B",
                "IDLEN": "1B",
                "ID": "1B",
                "PWLEN": "1B",
                "PW": "1B"
            })

            #if success => status is 0 and return True, if not =>status is 0xFF and return False
            server_response = serializeme.Serialize({
                "VER": ("1B", 1),
                "STATUS": ("1B", 0)
            })
            connection.sendall(server_response.packetize())

            #Section 4
            #Client request
            rsp = connection.recv(1024)

            #Decode first 4 bytes
            decode_client_connection = serializeme.Deserialize(
                rsp[0:4], {
                    "VER": ("1B"),
                    "CMD": ("1B"),
                    "RSV": ("1B"),
                    "ATYP": ("1B")
                })
            atyp = decode_client_connection.get_value("ATYP")

            #Decode rest of bytes
            if atyp == 1:
                decode = serializeme.Deserialize(rsp[4:], {
                    "DEST_ADDR": serializeme.IPv4,
                    "DEST_PORT": "4B"
                })
            elif atyp == 3:
                decode = serializeme.Deserialize(rsp[4:], {
                    "DEST_ADDR": serializeme.PREFIX_LENGTH,
                    "DEST_PORT": "2B"
                })
            dest_addr = decode.get_value("DEST_ADDR")
            dest_port = decode.get_value("DEST_PORT")

            #connection to dest_port (google.com in here)
            new_sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sd.connect((dest_addr, dest_port))

            #section 6
            response_packet = serializeme.Serialize({
                "VER": ("1B", 5),
                "STATUS": ("1B", 0),
                "RSV": ("1B", 0),
                "ATYP": ("1B", atyp),
                "BND_ADDR": (serializeme.PREFIX_LENGTH, dest_addr),
                "BND_PORT": ("2B", dest_port)
            })

            #connection.sendall(response_packet.packetize())
            connection.sendall(response_packet.packetize())

            #listen from client
            rsp = connection.recv(1024)

            #Send packet to server
            new_sd.sendall(rsp)

            #listen from destination address
            rsp = new_sd.recv(4096)
            """
            message = b''
            i = 1
            #print(message)
            while (True):
                rsp = new_sd.recv(4096)
                print(i, rsp)
                if not rsp:
                    break
                #print(i, rsp)
                i = i + 1
                #message += rsp
                message.append(rsp)
            print(message)
            """
            connection.sendall(rsp)
            print("Done")


if __name__ == '__main__':
    resolve()