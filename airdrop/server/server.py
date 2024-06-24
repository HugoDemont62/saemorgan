import socket
import threading
import os
from datetime import datetime

listnom = []
listip = []
listfichier = []


class EchoServerThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.messagelog = None
        self.filename = None
        self.nom = None
        self.choixnom = None
        print(f"connection from {client_address}")

    # Défini la fonction envoie de fichier
    def send_file(self):
        self.filename = self.client_socket.recv(1024).decode('utf-8').strip()
        if os.path.exists(self.filename):
            file_size = os.path.getsize(self.filename)
            self.client_socket.sendall(f"send {self.filename} {file_size}".encode('utf-8'))
            with open(self.filename, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    self.client_socket.sendall(data)
            print(f"File {self.filename} sent successfully.")
        else:
            self.client_socket.sendall("the file doesn't exist".encode('utf-8'))

    # Défini la fonction réception de fichier
    def receive_file(self):
        self.filename = self.client_socket.recv(1024).decode('utf-8').strip()
        self.client_socket.sendall(f"ready to receive {self.filename}".encode('utf-8'))
        file_size = int(self.client_socket.recv(1024).decode('utf-8').strip())
        with open(self.filename, 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                bytes_received += len(data)
        print(f"file {self.filename} received successfully.")
        if self.nom not in listfichier:
            listfichier.append(self.filename)

    # Permet d'écrire dans le log
    def trace(self):
        date_heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Ouvre le fichier logs en mode "append" pour ajouter du text ('a')
        with open('logs.txt', 'a', encoding='utf-8') as fichier:
            # Écrit des données dans le fichier
            fichier.write(f'{self.messagelog},{date_heure}\n\n')

    # Permet d'ajouter le nom d'une personne se connectant
    def add_person(self):
        self.nom = self.client_socket.recv(1024).decode('utf-8').strip()
        if self.nom not in listnom:
            listnom.append(self.nom)
            self.client_socket.sendall("ok".encode('utf-8'))
            self.choixnom = 1
        else :
            self.client_socket.sendall("invalid name".encode('utf-8'))
            self.choixnom = 0
        if self.client_address not in listip:
            listip.append(self.client_address)

    # Permet de retirer le nom d'une personne se déconnectant
    def remove_person(self):
        if self.nom in listnom:
            listnom.remove(self.nom)
        if self.client_address in listip:
            listip.remove(self.client_address)

    def run(self):
        try:
            # Informe le client de la connexion
            self.client_socket.sendall("client connected".encode('utf-8'))

            # Reçoit le nom du client, note la connection dans les logs et l'ajoute à la liste des personnes connectées
            while self.choixnom != 1:
                self.add_person()


            self.messagelog = self.nom + f" connected"
            self.trace()

            self.client_socket.sendall(f"connected as: {self.nom}".encode('utf-8'))
            while True:
                # Demande au client s'il veut uploader ou télécharger un fichier
                choice = self.client_socket.recv(1024).decode('utf-8').strip()
                if choice == "do":
                    self.send_file()
                    self.messagelog = "file "+self.filename+" sent to "+self.nom
                    self.trace()

                elif choice == "up":
                    self.receive_file()
                    self.messagelog = "file "+self.filename+" received from "+self.nom
                    self.trace()

                elif choice == "di":
                    self.messagelog = f"connection with {self.nom} :{self.client_address} closed"
                    self.trace()
                    self.remove_person()
                    self.client_socket.close()
                    break

                elif choice == "cl":
                    self.messagelog = f"list of connected client sent to {self.nom}"
                    self.trace()
                    self.client_socket.sendall(f"{listnom}".encode('utf-8'))

                elif choice == "fl":
                    self.messagelog = f"list of file sent to {self.nom}"
                    self.trace()
                    self.client_socket.sendall(f"{listfichier}".encode('utf-8'))

        # Gère les erreurs
        except Exception:
            print(f"client disconnected")


# Défini le numéro de port du serveur
port_number = 9000

# Indique que le serveur écoute les informations arrivant sur son port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', port_number))
server_socket.listen(1)

print(f"server is listening on port {port_number}")

while True:
    client_socket, client_address = server_socket.accept()
    EchoServerThread(client_socket, client_address).start()
