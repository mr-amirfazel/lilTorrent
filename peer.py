import socket
import threading
import requests
from request import Request, RequestTypes
import utils
import pickle
from PIL import Image
import zlib
import numpy as np

BASE_URL = "http://localhost:8000"
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
PORT_NUMBER = utils.generate_random_port('udp')
TCP_PORT_NUMBER = utils.generate_random_port('tcp')
TCP_RECIEVE_PORT = 4030
LOCK = False
USER_NAME = ''

#  state variables
registered = False
connected = False
connected_to = None


def signUp():
    username = input('enter your username:\n>')
    USER_NAME = username
    data = {
        'username': username,
        'ip': ip_address,
        'port': PORT_NUMBER
    }
    try:
        response = requests.post(BASE_URL + '/signup', json=data)
        print(response.text)
        return True
    except:
        print('oh oh')
        return False


def getAllUsers():
    try:
        response = requests.get(BASE_URL + '/users')

        for idx, user in enumerate(response.json()['users']):
            print('{}) {}'.format(idx + 1, user))
    except:
        print('oh oh')


def getUserInfo():
    user_input = input('enter the username please:\n>')
    try:
        response = requests.get(BASE_URL + '/user?id={}'.format(user_input))
        print(response.json())
    except:
        print('oh oh')


def connection_request_handler(server_socket, client_address):
    req_accept = input('Do you want to accept this request?\n1)Yes\n2)No\n>')
    if req_accept == '1':
        response_message = "Connection accepted"
        server_socket.sendto(response_message.encode(), client_address)
        print(f"Sent connection acceptance to {client_address[0]}:{client_address[1]}")
    elif req_accept == '2':
        response_message = "Connection rejected"
        server_socket.sendto(response_message.encode(), client_address)
        print(f"Sent connection rejection to {client_address[0]}:{client_address[1]}")
    else:
        print('wrong entry!!')
    LOCK = False


def request_quote_handler(server_socket, client_address, data):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ip_address, TCP_RECIEVE_PORT))
    tcp_socket.listen(1)
    quote_accept = input('Do you want to accept the quote request?\n1) Yes\n2) No\n>')
    if quote_accept == '1':
        response_message = utils.get_random_quote()
        connection_socket, _ = tcp_socket.accept()
        connection_socket.sendall(response_message.encode())
        print(f"Sent a Random quote to {client_address[0]}:{client_address[1]}")
    elif quote_accept == '2':
        response_message = "random quote request rejected"
        server_socket.sendto(response_message.encode(), client_address)
        print(f"Sent random quote request rejection to {client_address[0]}:{client_address[1]}")
    else:
        print('oops. wrong entry!!')

    LOCK = False


def split_into_packets(image_data, packet_size):
    packets = []
    num_packets = (len(image_data) + packet_size - 1) // packet_size

    for i in range(num_packets):
        start = i * packet_size
        end = start + packet_size
        packet = image_data[start:end]
        packets.append(packet)

    return packets


def calculate_checksum(data):
    checksum = sum(data) % 65536  # Assuming 16-bit checksum
    return checksum


def request_media_handler(server_socket, client_address, data):
    req_accept = input('Do you want to accept the Media request?\n1)Yes\n2)No\n>')
    if req_accept == '1':
        image_address = utils.get_random_image()
        image = Image.open(image_address)
        image_array = np.asarray(image)
        rows, columns, channels = image_array.shape
        dimensions_message = f"{rows}:{columns}"
        server_socket.sendto(dimensions_message.encode(), client_address)
        image_data = image.tobytes()
        chunk_size = 1024
        total_chunks = (len(image_data) + chunk_size - 1) // chunk_size
        for i in range(total_chunks):
            if i == total_chunks - 1:
                chunk = image_data[i * chunk_size:]
            else:
                chunk = image_data[i * chunk_size: (i + 1) * chunk_size]
            server_socket.sendto(chunk, client_address)
        server_socket.sendto(b'Finished', client_address)
        server_socket.close()

        # packet_size = 1024
        # image_address = utils.get_random_image()
        # image = Image.open(image_address)
        #
        # image_size = image.size
        # image_size_data = f"{image_size[0]},{image_size[1]}"
        # server_socket.sendto(image_size_data.encode(), client_address)
        #
        # # Convert the image to RGB mode
        # image = image.convert('RGB')
        #
        # # Iterate over the image and send packets
        # for y in range(image_size[1]):
        #     for x in range(image_size[0]):
        #         # Get the pixel RGB values
        #         r, g, b = image.getpixel((x, y))
        #
        #         # Create the packet data
        #         packet_data = f"{x},{y},{r},{g},{b}"
        #
        #         # Send the packet
        #         while True:
        #             print('boi')
        #             server_socket.sendto(packet_data.encode(), client_address)
        #             ack, addr = server_socket.recvfrom(1024)
        #             if ack == b'ACK':
        #                 break

        # Close the socket
        # sock.close()
        # image_bytes = image.tobytes()
        #
        # chunk_size = 1024
        # packet_numbers = (len(image_bytes) + chunk_size - 1) // chunk_size
        # server_socket.sendto(str(packet_numbers).encode(), client_address)
        # for i in range(0, len(image_bytes), chunk_size):
        #     chunk = image_bytes[i: i + chunk_size]
        #
        #     # Send the chunk of image bytes
        #     server_socket.sendto(chunk, client_address)

        # packets = split_into_packets(image_data, 1024)
        # total_packets = len(packets)
        #
        # for sequence_number, packet in enumerate(packets):
        #     header = f"{sequence_number}/{total_packets}"
        #     checksum = calculate_checksum(packet)
        #     message = header.encode() + packet + checksum.to_bytes(2, "big")
        #     server_socket.sendto(message, client_address)

        print(f"Sent media request acceptance to {client_address[0]}:{client_address[1]}")
    elif req_accept == '2':
        pass
    else:
        print('wrong entry!!')
    LOCK = False


def listen_for_requests(port=PORT_NUMBER):
    # Create a UDP socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to a specific port
        server_socket.bind((ip_address, port))

        print(f"UDP listener started on port {port}")

        while True:
            # Receive data from clients
            data, client_address = server_socket.recvfrom(1024)
            data = pickle.loads(data)
            LOCK = True
            if data.type == RequestTypes.CONNECTION:
                print(f"Received request from {client_address[0]}:{client_address[1]} for Connection")
                connection_request_handler(server_socket, client_address)
            elif data.type == RequestTypes.QUOTE:
                print(f"Received request from {client_address[0]}:{client_address[1]} for a random quote")
                request_quote_handler(server_socket, client_address, data)
            elif data.type == RequestTypes.MEDIA:
                print(f"Received request from {client_address[0]}:{client_address[1]} for a random media")
                request_media_handler(server_socket, client_address, data)
    except:
        print('we got an error')
        listener_thread = threading.Thread(target=listen_for_requests, args=(PORT_NUMBER,))
        listener_thread.start()


def connect_to_peer():
    port = input("please enter Port number:\n>")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = pickle.dumps(Request(RequestTypes.CONNECTION))
    sock.sendto(message, (ip_address, int(port)))
    print('Connection request was sent succesfully wait for acception...')
    sock.settimeout(15)
    try:
        response, _ = sock.recvfrom(1024)
        print(f"Connection accepted by {ip_address}:{port}")
        return (True, {
            'ip': ip_address,
            'port': port
        })

    except socket.timeout:
        print(f"No response from {ip_address}:{port}. Peer is not online.")
        return False, None

    finally:
        # Close the socket
        sock.close()


def request_quote():
    port = connected_to['port']
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = pickle.dumps(Request(RequestTypes.QUOTE, data={'port': TCP_PORT_NUMBER}))
    sock.sendto(message, (ip_address, int(port)))
    print('Quote request was sent succesfully wait for acception...')
    sock.close()
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        tcp_socket.connect((ip_address, TCP_RECIEVE_PORT))
        print(f"Connected to {ip_address}:{TCP_RECIEVE_PORT} via TCP")

        try:
            response = tcp_socket.recv(1024)
            print(f"Quote received from {ip_address}:{port}  :\n>{response.decode()}")

        finally:
            tcp_socket.close()

    except Exception as e:
        print(f"An error occurred while connecting to the target peer via TCP: {e}")


    except socket.timeout:
        print(f"No response from {ip_address}:{port}. Peer is not online.")


def validate_checksum(data, received_checksum):
    calculated_checksum = calculate_checksum(data)
    return calculated_checksum == received_checksum


def reassemble_packets(received_packets, total_packets):
    sorted_packets = [received_packets[i] for i in range(total_packets)]
    image_data = b"".join(sorted_packets)
    return image_data


def request_media():
    port = connected_to['port']
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = pickle.dumps(Request(RequestTypes.MEDIA))
    sock.sendto(message, (ip_address, int(port)))
    print('Media request was sent succesfully wait for acception...')
    sock.settimeout(70)
    try:
        dimensions_message, addr = sock.recvfrom(1024)
        dimensions = dimensions_message.decode().split(":")
        rows = int(dimensions[0])
        columns = int(dimensions[1])
        print("Image Dimensions: " + str(rows) + " * " + str(columns))
        received_rows = []
        while True:
            input_data, addr = sock.recvfrom(1024)
            if input_data == b'Finished':
                print("Downloading Image Finished.")
                break
            received_rows.append(input_data)
        sock.close()
        image_data = b''.join(received_rows)
        image_array = np.frombuffer(image_data, dtype=np.uint8).reshape((rows, columns, -1))
        image = Image.fromarray(image_array)
        image.save('./dist/img.jpg')

        

    except socket.timeout:
        print(f"No response from {ip_address}:{port}. Peer is not online.")

    finally:
        # Close the socket
        sock.close()


listener_thread = threading.Thread(target=listen_for_requests, args=(PORT_NUMBER,))
listener_thread.start()
if __name__ == "__main__":

    loop_condition = True
    print('welcome to TMGE service \nplease pick a choice:')
    while loop_condition:
        if LOCK:
            pass
        else:
            utils.print_menu(connected=connected, registered=registered)

            user_input = utils.get_input()
            if registered:
                if not connected:
                    if user_input == '1':
                        getAllUsers()
                    elif user_input == '2':
                        getUserInfo()
                    elif user_input == '3':
                        try:
                            connected, connected_to = connect_to_peer()
                        except:
                            pass
                else:
                    if user_input == '1':
                        try:
                            request_quote()
                        except:
                            pass
                    elif user_input == '2':
                        try:
                            request_media()
                        except:
                            pass
                    elif user_input == '3':
                        connected = False
                        connected_to = None
            else:
                if user_input == '1':
                    registered = signUp()
