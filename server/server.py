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
import pickle

from keras.models import load_model

import classification

model = load_model('cifar100_1.h5')

def handle_client(connectionSock):
    path = "C:/Users/User/Desktop/"+ username
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(username+'의 드라이브가 생성되었습니다.')
    else:
        print(username+'의 드라이브에 연결합니다.')

    while True:
        try:
            t = Thread(target=CheckSystem(connectionSock))
            t.start()
        except Exception as e:
            connectionSock.close()
            print('Connection closed')
            break

def accept_clients():
    while True:
        connectionSock, addr = serverSock.accept()
        print('New connection from [%s]' %addr[0])
        
        clients.append(connectionSock)
        ip.append(addr)

        global username

        username = connectionSock.recv(1024)
        username = username.decode()

        get_filedir(connectionSock)

        t = Thread(target=handle_client(connectionSock))
        t.start()

def Download(connectionSock):
    filename = connectionSock.recv(1024) #클라이언트한테 파일이름(이진 바이트 스트림 형태)을 전달 받는다
    filename = filename.decode('utf-8')
    print('요청 받은 파일: [%s] ' %filename) #파일 이름을 일반 문자열로 변환한다
    
    data_transferred = 0

    start_dir = "C:/Users/User/Desktop/"+username

    target_file = filename
    filepath = find_files(start_dir, target_file)

    if not os.path.exists(filepath):
        print('해당 디렉토리에 파일[%s]이 존재하지 않음' %filename)
        return
    else:
        print('good')
    
    fileSize = os.path.getsize(filepath)
    fileSize = str(fileSize)

    connectionSock.send(fileSize.encode('utf-8'))
    
    with open(filepath, 'rb') as f:
            data = f.read(int(fileSize)) #1024바이트 읽는다
            data_transferred += connectionSock.send(data) #1024바이트 보내고 크기 저장
    print("전송완료 %s, 전송량 %d" %(filename, data_transferred))

def Upload(connectionSock):
    filename = connectionSock.recv(1024)
    filename = filename.decode('utf-8')

    print('다운로드 받을 파일: [%s] ' %filename) #파일 이름을 일반 문자열로 변환한다
    data_transferred = 0

    reSize = connectionSock.recv(1024)
    reSize = reSize.decode('utf-8')

    if not reSize:
            print('파일[%s]: 클라이언트에 존재하지 않음' %filename)
            sys.exit()
            
    print('파일 사이즈: [%s]' %reSize)

    result = classification.classificationn(filename, model)

    clouddir = "C:/Users/User/Desktop/"+username
    dir_name = result
    new_folder_path = os.path.join(clouddir, dir_name)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

        with open(new_folder_path + "\\" + filename, 'wb') as f:
            data = connectionSock.recv(int(reSize))
            f.write(data)
            data_transferred += len(data)
        print('파일 %s 받기 완료. 전송량 %d' %(filename, data_transferred))
    else:
        with open(new_folder_path + "\\" + filename, 'wb') as f:
            data = connectionSock.recv(int(reSize))
            f.write(data)
            data_transferred += len(data)
        print('파일 %s 받기 완료. 전송량 %d' %(filename, data_transferred))

def DeleteFile(connectionSock):
    filename = connectionSock.recv(1024)
    filename = filename.decode('utf-8')

    start_dir = "C:/Users/User/Desktop/"+username
    target_file = filename

    filepath = find_files(start_dir, target_file)

    try:
        os.remove(filepath)
        print('파일[%s] 삭제 완료' %filename)
    except OSError as e:
        print('오류가 발생하였습니다.')
    

def find_files(start_dir, target_file):
    for dirpath, dirnames, filenames in os.walk(start_dir):
        for filenamee in filenames:
            if filenamee == target_file:
                ppath = os.path.join(dirpath, filenamee)
                print(ppath)
                return ppath
    print('해당 디렉토리에 파일[%s]이 존재하지 않음' %target_file)

def CheckSystem(connectionSock):
    while True:
        try:
            text = connectionSock.recv(1024)
            text = text.decode('utf-8')

            if (text == '1'):
                t = Thread(target=Download(connectionSock))
                t.start()
            elif (text == '2'):
                t = Thread(target=Upload(connectionSock))
                t.start()
                get_filedir(connectionSock)
            elif (text == '3'):
                t = Thread(target=DeleteFile(connectionSock))
                t.start()
                get_filedir(connectionSock)
            else:
                return
        except Exception as e:
            print(e)

def get_filedir(connectionSock):
    start_dir = "C:/Users/User/Desktop/"+username
    name_list = []

    for (start_dir, dirs, files) in os.walk(start_dir):
        for file in files:
            name_list.append(file)
        for dir in dirs:
            name_list.append(dir)

    data = pickle.dumps(name_list)
    connectionSock.sendall(data)

def create_thread():
    t = Thread(target=accept_clients)
    t.start()


if __name__ == '__main__':
    serverSock = socket.socket(AF_INET, SOCK_STREAM)
    serverSock.bind((gethostbyname(gethostname()), 9009))
    serverSock.listen()

    print('Server listening on [%s],9009' %gethostbyname(gethostname()))

    clients = []
    ip = []

    create_thread()


