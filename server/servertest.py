from socket import *
from os.path import exists
import os
import threading
from threading import Lock, Thread
import socket
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from keras.models import load_model

# import classification

import getpass

frameList = []

SERVER_IP = gethostbyname(gethostname())
PORT = 9009

username = getpass.getuser()

class CloudServer:
    def __init__(self):
        self.bListen = False
        self.clients = []
        self.ip = []
        self.threads = []
        self.lock = threading.Lock()

    def start(self, ip, port):
        self.server = socket.socket(AF_INET, SOCK_STREAM)

        try:
            self.server.bind((ip, port))
        except Exception as e:
            print('Bind Error : ', e)
            return False
        else:
            self.bListen = True
            self.t = Thread(target=self.listen, args=(self.server,))
            self.t.start()
            print('Server Listening...')
        
        return True

    def listen(self, server):
        while self.bListen:
            server.listen(5)
            try:
                connectionSock, addr = server.accept()
            except Exception as e:
                print('Accept() Error: ', e)
                break
            else:
                print(connectionSock)
                self.clients.append(connectionSock)
                self.ip.append(addr)
                while True:
                    t = Thread(target=self.CheckSystem, args=(connectionSock,))
                    self.threads.append(t)
                    t.start()

        self.server.close()

    def CheckSystem(self, connectionSock):
        self.connectionSock = connectionSock
        # while self.bListen:
        text = self.connectionSock.recv(1024)
        text = text.decode()
        if (text == '1'):
            filename =connectionSock.recv(1024) #클라이언트한테 파일이름(이진 바이트 스트림 형태)을 전달 받는다
            filename = filename.decode()
            print('요청 받은 파일: [%s] ' %filename) #파일 이름을 일반 문자열로 변환한다
        elif (text == '2'):
            # Upload()
            print('upload')
        elif (text == '3'):
            self.DeleteFile(self.connectionSock)
            print('delete')
        else:
            return


    def Download(self, connectionSock):
        # self.connectionSock = connectionSock
        filename =connectionSock.recv(1024) #클라이언트한테 파일이름(이진 바이트 스트림 형태)을 전달 받는다
        filename = filename.decode()
        print('요청 받은 파일: [%s] ' %filename) #파일 이름을 일반 문자열로 변환한다
    #     data_transferred = 0

    #     username = self.connectionSock.recv(1024)
    #     username = username.decode()

    #     start_dir = "C:/Users/"+username+"/Desktop/Newbie_Assignment/server"

    #     target_file = filename
    #     filepath = self.find_files(start_dir, target_file)

    #     if not os.path.exists(filepath):
    #         print('해당 디렉토리에 파일[%s]이 존재하지 않음' %filename)
    #         return
    #     else:
    #         print('good')
        
    #     fileSize = os.path.getsize(filepath)
    #     fileSize = str(fileSize)

    #     self.connectionSock.sendall(fileSize.encode())
        
    #     with open(filepath, 'rb') as f:
    #             data = f.read(int(fileSize)) #1024바이트 읽는다
    #             data_transferred += self.connectionSock.send(data) #1024바이트 보내고 크기 저장
    #     print("전송완료 %s, 전송량 %d" %(filename, data_transferred))

    def DeleteFile(self, connectionSock):
        self.connectionSock = connectionSock
        filename = self.connectionSock.recv(1024)
        filename = filename.decode()

        start_dir = "C:/Users/"+username+"/Desktop/Newbie_Assignment/server"
        target_file = filename

        filepath = self.find_files(start_dir, target_file)

        try:
            os.remove(filepath)
            print('파일[%s] 삭제 완료' %filename)
        except OSError as e:
            print('오류가 발생하였습니다.')

    def find_files(self, start_dir, target_file):
        for dirpath, dirnames, filenames in os.walk(start_dir):
            for filenamee in filenames:
                if filenamee == target_file:
                    ppath = os.path.join(dirpath, filenamee)
                    print(ppath)
                    return ppath
        print('해당 디렉토리에 파일[%s]이 존재하지 않음' %target_file)

cs = CloudServer()
cs.start(SERVER_IP, PORT)
                
    



# serverSock = socket.socket(AF_INET, SOCK_STREAM)
# serverSock.bind((socket.gethostname(), 9009))
# serverSock.listen()

# connectionSock, addr = serverSock.accept()
# print('[%s] 연결 성공' %addr[0])

# model = load_model('cifar100_1.h5')
# username = getpass.getuser()

# def Download():
#     filename = connectionSock.recv(1024) #클라이언트한테 파일이름(이진 바이트 스트림 형태)을 전달 받는다
#     filename = filename.decode()
#     print('요청 받은 파일: [%s] ' %filename) #파일 이름을 일반 문자열로 변환한다
#     data_transferred = 0

#     start_dir = "C:/Users/"+username+"/Desktop/Newbie_Assignment/server"

#     target_file = filename
#     filepath = find_files(start_dir, target_file)

#     if not os.path.exists(filepath):
#         print('해당 디렉토리에 파일[%s]이 존재하지 않음' %filename)
#         return
#     else:
#         print('good')
    
#     fileSize = os.path.getsize(filepath)
#     fileSize = str(fileSize)

#     connectionSock.sendall(fileSize.encode())
    
#     with open(filepath, 'rb') as f:
#             data = f.read(int(fileSize)) #1024바이트 읽는다
#             data_transferred += connectionSock.send(data) #1024바이트 보내고 크기 저장
#     print("전송완료 %s, 전송량 %d" %(filename, data_transferred))

# def Upload():
#     filename = connectionSock.recv(1024)
#     filename = filename.decode()
#     print('다운로드 받을 파일: [%s] ' %filename) #파일 이름을 일반 문자열로 변환한다
#     data_transferred = 0

#     reSize = connectionSock.recv(1024)
#     reSize = reSize.decode()

#     if not reSize:
#             print('파일[%s]: 클라이언트에 존재하지 않음' %filename)
#             sys.exit()

#     result = classification.classificationn(filename, model)

#     nowdir = os.getcwd()
#     dir_name = result
#     new_folder_path = os.path.join(nowdir, dir_name)

#     if not os.path.exists(new_folder_path):
#         os.makedirs(new_folder_path)

#         with open(new_folder_path + "\\" + filename, 'wb') as f:
#             data = connectionSock.recv(int(reSize))
#             f.write(data)
#             data_transferred += len(data)
#         print('파일 %s 받기 완료. 전송량 %d' %(filename, data_transferred))
#     else:
#         with open(new_folder_path + "\\" + filename, 'wb') as f:
#             data = connectionSock.recv(int(reSize))
#             f.write(data)
#             data_transferred += len(data)
#         print('파일 %s 받기 완료. 전송량 %d' %(filename, data_transferred))

# def DeleteFile():
#     filename = connectionSock.recv(1024)
#     filename = filename.decode()

#     start_dir = "C:/Users/"+username+"/Desktop/Newbie_Assignment/server"
#     target_file = filename

#     filepath = find_files(start_dir, target_file)

#     try:
#         os.remove(filepath)
#         print('파일[%s] 삭제 완료' %filename)
#     except OSError as e:
#         print('오류가 발생하였습니다.')
    

# def find_files(start_dir, target_file):
#     for dirpath, dirnames, filenames in os.walk(start_dir):
#         for filenamee in filenames:
#             if filenamee == target_file:
#                 ppath = os.path.join(dirpath, filenamee)
#                 print(ppath)
#                 return ppath
#     print('해당 디렉토리에 파일[%s]이 존재하지 않음' %target_file)

# def CheckSystem():
#     while True:
#         try:
#             text = connectionSock.recv(1024)
#             text = text.decode()

#             if (text == '1'):
#                 Download()
#             elif (text == '2'):
#                 Upload()
#             elif (text == '3'):
#                 DeleteFile()
#             else:
#                 return
#         except Exception as e:
#             print(e)

# # CheckSystem()
