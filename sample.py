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
    #print("Server IP {} Listening on Port {}".format(HOST, PORT))
    sd.listen(1)

    #print(sd)

    while True:
        # Wait for a connection
        print('Waiting for a client connection')
        # connection established
        connection, client_address = sd.accept()
        with connection:
            print("Connected by", client_address)
            rsp = connection.recv(1024)
            #print("clinet_greeting data: ", rsp)

            #section 3
            decode_client_greeting = serializeme.Deserialize(
                rsp, {
                    "VER": ("1B"),
                    "NAUTH": ("1B", "", "AUTH"),
                    "AUTH": {
                        "Name": "1B"
                    }
                })
            #print("VER is: ", decode_client_greeting.get_value("VER"))
            #print("NAUTH is: ", decode_client_greeting.get_value("NAUTH"))
            #print("AUTH is: ", decode_client_greeting.get_value("AUTH"))

            server_choice = serializeme.Serialize({
                "VER": ("1B", 5),
                "METHOD": ("1B", 2)
            })
            #print("server choice: ", server_choice.packetize())
            connection.sendall(server_choice.packetize())

            #subsequent authentication
            rsp = connection.recv(1024)
            #print("Client quthentication request): ", rsp)
            decode_request = serializeme.Deserialize(rsp, {
                "VER": "1B",
                "IDLEN": "1B",
                "ID": "1B",
                "PWLEN": "1B",
                "PW": "1B"
            })
            #print("VER is: ", decode_request.get_value("VER"))
            #print("IDLEN is: ", decode_request.get_value("IDLEN"))
            #print("ID is: ", decode_request.get_value("ID"))
            #print("PWLEN is: ", decode_request.get_value("PWLEN"))
            #print("PW is: ", decode_request.get_value("PW"))

            #if success => status is 0 and return True, if not =>status is 0xFF and return False
            server_response = serializeme.Serialize({
                "VER": ("1B", 1),
                "STATUS": ("1B", 0)
            })
            #print("server response: ", server_response.packetize())
            connection.sendall(server_response.packetize())
            print("server response is sent")

            #Section 4
            rsp = connection.recv(1024)
            #print("Client request message: ", rsp)
            #print("First 4 bytes: ", rsp[0:4])

            decode_client_connection = serializeme.Deserialize(
                rsp[0:4], {
                    "VER": ("1B"),
                    "CMD": ("1B"),
                    "RSV": ("1B"),
                    "ATYP": ("1B")
                })
            #print("ATYP is: ", decode_client_connection.get_value("ATYP"))
            #print("Rest of bytes: ", rsp[4:])
            atyp = decode_client_connection.get_value("ATYP")

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
            #print(dest_addr)
            dest_port = decode.get_value("DEST_PORT")
            #print(dest_port)

            #print("VER is: ", decode_client_connection.get_value("VER"))
            #print("CMD is: ", decode_client_connection.get_value("CMD"))
            #print("RSV is: ", decode_client_connection.get_value("RSV"))
            #print("ATYP is: ", decode_client_connection.get_value("ATYP"))
            #print("DEST_ADDR is: ", decode.get_value("DEST_ADDR"))
            #print("DEST_PORT is: ", decode.get_value("DEST_PORT"))

            #connection to dest_port (google.com in here)
            new_sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sd.connect((dest_addr, dest_port))
            #res = new_sd.recv(1024)
            #print(res)

            #section 6
            response_packet = serializeme.Serialize({
                "VER": ("1B", 5),
                "STATUS": ("1B", 0),
                "RSV": ("1B", 0),
                "ATYP": ("1B", atyp),
                "BND_ADDR": (serializeme.PREFIX_LENGTH, dest_addr),
                "BND_PORT": ("2B", dest_port)
            })
            #print("response packet from server", response_packet.packetize())
            #connection.sendall(response_packet.packetize())
            connection.sendall(response_packet.packetize())
            print("response packet is sent to client!")

            #listen from client
            rsp = connection.recv(1024)
            #print(rsp)

            new_sd.sendall(rsp)
            print("User request is sent to desination address!")

            #listen from destination address
            #rsp = new_sd.recv(4096)

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

            connection.sendall(rsp)
            print("Sent reply back from google to clinet")


if __name__ == '__main__':
    resolve()