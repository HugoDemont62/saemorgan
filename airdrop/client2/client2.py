import socket
import os

def client_program():
    host_name = "localhost"
    port_number = 9000
    echo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Permet de se connecter au serveur
        echo_socket.connect((host_name, port_number))
        connection_message = echo_socket.recv(1024).decode('utf-8').strip()
        server_message=None
        while server_message!="ok":
            nom = input("enter your name: ").strip()
            # Permet d'envoyer le nom du client au serveur
            echo_socket.sendall(nom.encode('utf-8'))
            server_message = echo_socket.recv(1024).decode('utf-8').strip()
            print(server_message)


        server_message = echo_socket.recv(1024).decode('utf-8').strip()

        while True:
            # Envoie le choix au serveur
            choice = input("do:download up:upload di:disconnect cl:client list fl:file list --> ").strip()
            echo_socket.sendall(choice.encode('utf-8'))
            if choice == "do":
                receive_file(echo_socket)

            elif choice == "up":
                upload_file(echo_socket)

            elif choice == "di":
                print("disconnected")
                echo_socket.close()
                break

            elif choice == "cl":
                server_message = echo_socket.recv(1024).strip()
                print(f"server: {server_message}")

            elif choice == "fl":
                server_message = echo_socket.recv(1024).strip()
                print(f"server: {server_message}")
            else:
                print("invalid choice")

    # Gère les erreurs
    except Exception as e:
        print(f"error: {e}")


# Gère la réception des fichiers
def receive_file(echo_socket):
    filename = input("enter file name: ").strip()
    echo_socket.sendall(filename.encode('utf-8'))
    filename_message = echo_socket.recv(1024).decode('utf-8').strip()
    if filename_message.startswith("send"):
        _, filename, file_size = filename_message.split()
        file_size = int(file_size)
        with open(filename, 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                data = echo_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                bytes_received += len(data)

        print(f"file {filename} received successfully.")
    else:
        print(f"server: {filename_message}")


# Gère l'envoie de fichiers
def upload_file(echo_socket):
    filename = input("Enter the file name to upload: ").strip()
    echo_socket.sendall(filename.encode('utf-8'))
    server_response = echo_socket.recv(1024).decode('utf-8').strip()
    if server_response.startswith("ready to receive"):
        file_size = os.path.getsize(filename)
        echo_socket.sendall(str(file_size).encode('utf-8'))
        with open(filename, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                echo_socket.sendall(data)
        print(f"file {filename} sent successfully.")
    else:
        print(f"server: {server_response}")


if __name__ == "__main__":
    client_program()
