import socket
import threading
import os
from datetime import datetime

listnom = []
listip = []

class EchoServerThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.messagelog = None
        self.filename = None
        self.nom = None
        print(f"Connection from {client_address}")

    # Définit la fonction envoie de fichier
    def send_file(self):
        filename = self.client_socket.recv(1024).decode('utf-8').strip()
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            self.client_socket.sendall(f"ENVOI {filename} {file_size}".encode('utf-8'))
            with open(filename, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    self.client_socket.sendall(data)
            print(f"File {filename} sent successfully.")
        else:
            self.client_socket.sendall("Le fichier n'existe pas".encode('utf-8'))

    # Définit la fonction réception de fichier
    def receive_file(self):
        self.filename = self.client_socket.recv(1024).decode('utf-8').strip()
        self.client_socket.sendall(f"READY TO RECEIVE {self.filename}".encode('utf-8'))
        file_size = int(self.client_socket.recv(1024).decode('utf-8').strip())
        with open(self.filename, 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                bytes_received += len(data)
        print(f"File {self.filename} received successfully.")
        self.messagelog = f"receive {self.filename} from {self.nom}"

    def trace(self):
        date_heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Ouvrir le fichier logs en mode "append" pour ajouter du text ('a')
        with open('logs.txt', 'a', encoding='utf-8') as fichier:
            # Écrire des données dans le fichier
            fichier.write(f'{self.messagelog},{date_heure}\n')

    def add_person(self):
        if self.nom not in listnom:
            listnom.append(self.nom)

        if self.client_address not in listip:
            listip.append(self.client_address)

    def remove_person(self):
        if self.nom in listnom:
            listnom.remove(self.nom)

    def run(self):
        try:
            # Informe le client de la connexion
            self.client_socket.sendall("Client connected".encode('utf-8'))

            # Reçois le nom du client, note la connection dans les logs et l'ajoute a la liste des perssone connecter
            self.nom = self.client_socket.recv(1024).decode('utf-8').strip()
            self.add_person()
            self.messagelog = self.nom + f" connected"
            self.trace()

            self.client_socket.sendall(f"connected as: {self.nom}".encode('utf-8'))
            while True:
            # Demande au client s'il veut uploader ou télécharger un fichier
                choice = self.client_socket.recv(1024).decode('utf-8').strip()
                if choice == "0":
                    self.send_file()
                    self.messagelog = "file sended"
                    self.trace()

                elif choice == "1":
                    self.receive_file()
                    self.messagelog = "file recived"
                    self.trace()

                elif choice == "2":
                    self.messagelog = f"Connection with {self.nom} :{self.client_address} closed"
                    self.trace()
                    self.remove_person()
                    self.client_socket.close()
                    break

                elif choice == "3":
                    self.messagelog = f" list of connected client send to {self.nom}"
                    self.trace()
                    self.client_socket.sendall(f"{listnom}".encode('utf-8'))

        # Gère les erreurs
        except Exception as e:
            print(f"client deconnecter")


# Définit le numéro de port du serveur
port_number = 9000

# Indique que le serveur écoute les informations arrivant sur son port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', port_number))
server_socket.listen(1)

print(f"Server is listening on port {port_number}")

while True:
    client_socket, client_address = server_socket.accept()
    EchoServerThread(client_socket, client_address).start()
