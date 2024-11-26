import os
import socket
import threading
import random
import getpass
from stable_baselines3 import DQN
from keras.models import load_model

class CloudServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))
        self.server.listen(5)
        self.username = getpass.getuser()
        self.model = load_model('cifar100_1.h5')

    def start(self):
        print("Server Listening on %s:%d..." % (self.ip, self.port))
        while True:
            connectionSock, addr = self.server.accept()
            print(f'Client {addr} connected')
            threading.Thread(target=self.handle_client, args=(connectionSock, addr)).start()

    def handle_client(self, connectionSock, addr):
        while True:
            try:
                text = connectionSock.recv(1024).decode()
                if text == '1':
                    self.Download(connectionSock)
                elif text == '2':
                    self.Upload(connectionSock)
                elif text == '3':
                    self.DeleteFile(connectionSock)
                else:
                    connectionSock.sendall("Invalid Command".encode())
            except Exception as e:
                print(f"Error: {e}")
                connectionSock.close()
                break

    def Download(self, connectionSock):
        filename = connectionSock.recv(1024).decode()
        print(f"Requested file: {filename}")
        filepath = self.find_files(filename)
        if filepath:
            fileSize = os.path.getsize(filepath)
            connectionSock.sendall(str(fileSize).encode())
            with open(filepath, 'rb') as f:
                data = f.read(fileSize)
                connectionSock.sendall(data)
            print(f"File {filename} sent successfully.")
        else:
            connectionSock.sendall("File not found.".encode())

    def Upload(self, connectionSock):
        filename = connectionSock.recv(1024).decode()
        filesize = int(connectionSock.recv(1024).decode())
        data = connectionSock.recv(filesize)
        result = self.classify(filename)
        new_dir = os.path.join(os.getcwd(), result)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        with open(os.path.join(new_dir, filename), 'wb') as f:
            f.write(data)
        print(f"File {filename} uploaded successfully.")

    def DeleteFile(self, connectionSock):
        filename = connectionSock.recv(1024).decode()
        filepath = self.find_files(filename)
        if filepath:
            os.remove(filepath)
            connectionSock.sendall(f"File {filename} deleted.".encode())
        else:
            connectionSock.sendall(f"File {filename} not found.".encode())

    def find_files(self, filename):
        start_dir = f"C:/Users/{self.username}/Desktop/Newbie_Assignment/server"
        for dirpath, _, filenames in os.walk(start_dir):
            if filename in filenames:
                return os.path.join(dirpath, filename)
        return None

    def classify(self, filename):
        # Assuming classification is done using the model
        return "classified_folder"

# Start the server
server_ip = socket.gethostbyname(socket.gethostname())
server_port = 9009
server = CloudServer(server_ip, server_port)
server.start()
