import socket
import os

def client_program():
    host_name = "localhost"
    port_number = 9000
    echo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #  recuperer le nom du client
        nom = input("Indiquez votre nom: ").strip()
        # se connecter au serveur
        echo_socket.connect((host_name, port_number))
        connection_message = echo_socket.recv(1024).decode('utf-8').strip()
        # envoyer le nom du client
        echo_socket.sendall(nom.encode('utf-8'))
        server_message = echo_socket.recv(1024).decode('utf-8').strip()

        while True:
            # envoyer le choix au serveur
            choice = input("0 télécharger 1 uploader 2 deconnecter 3 liste personnes connectées: ").strip()
            echo_socket.sendall(choice.encode('utf-8'))
            if choice == "0":
                receive_file(echo_socket)

            elif choice == "1":
                upload_file(echo_socket)

            elif choice == "2":
                print("deconnecté")
                echo_socket.close()
                break

            elif choice == "3":
                server_message = echo_socket.recv(1024).strip()
                print(f"Server: {server_message}")

            else:
                print("Choix invalide.")

    # Gère les erreurs
    except Exception as e:
        print(f"Error: {e}")


# Gère la réception de fichiers
def receive_file(echo_socket):
    filename = input("Indiquez le nom du fichier: ").strip()
    echo_socket.sendall(filename.encode('utf-8'))
    filename_message = echo_socket.recv(1024).decode('utf-8').strip()
    if filename_message.startswith("ENVOI"):
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

        print(f"File {filename} received successfully.")
    else:
        print(f"Server: {filename_message}")


# Gère l'envoie de fichiers
def upload_file(echo_socket):
    filename = input("Indiquez le nom du fichier à uploader: ").strip()
    echo_socket.sendall(filename.encode('utf-8'))
    server_response = echo_socket.recv(1024).decode('utf-8').strip()
    if server_response.startswith("READY TO RECEIVE"):
        file_size = os.path.getsize(filename)
        echo_socket.sendall(str(file_size).encode('utf-8'))
        with open(filename, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                echo_socket.sendall(data)
        print(f"File {filename} sent successfully.")
    else:
        print(f"Server: {server_response}")


if __name__ == "__main__":
    client_program()
