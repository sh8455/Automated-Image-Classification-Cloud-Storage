import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from socket import *
import os
from os.path import exists
from PyQt5.QtCore import *
import socket
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileSystemModel
import pickle
from PyQt5.QtGui import QStandardItemModel

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class_1 = uic.loadUiType("connect_ui.ui")[0]
form_class_2 = uic.loadUiType("system_ui.ui")[0]

# 서버 접속 창 (first window)
class Connect(QMainWindow, form_class_1) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle('connect system')
        self.conBtn.clicked.connect(self.btnConnect)
        self.ip_edit.setText('163.180.116.33') # 내 ip주소를 가져오기 위해

    # 소켓 연결 함수
    def btnConnect(self):
        global IP
        global PORT
        global username
        global clientSock

        IP = self.ip_edit.text()
        PORT = self.port_edit.text()
        username = self.username_edit.text()

        clientSock = socket.socket(AF_INET, SOCK_STREAM)
        clientSock.connect((str(IP), int(PORT)))

        clientSock.send(username.encode())

        path = "C:/Users/User/Desktop/"+ username

        if not os.path.exists(path):
            os.makedirs(path)
            print(username+'의 드라이브가 생성되었습니다.')
        else:
            print(username+'의 기존 드라이브에 연결합니다.')

        # print(path)

        print('연결 성공')

        self.hide()
        self.secwin = System()
        self.secwin.exec() # 두번째 창 닫을때까지 기다림
        self.show() # 두번째 창 닫으면 다시 커넥트 창 보여짐

# 파일 다운로드 쓰레드
class downloadThread(QThread):
    def __init__(self,parent,clientSock):
        super().__init__(parent)
        self.parent = parent
        self.clientSock = clientSock

    def run(self):
        text = '1'
        self.clientSock.send(text.encode('utf-8'))

        self.clientSock.send(fileName.encode('utf-8'))
        data_transferred = 0

        reSize = self.clientSock.recv(1024)
        reSize = reSize.decode('utf-8')

        if not reSize:
            print('파일 [%s]가 서버에 존재하지 않음' %fileName)
            sys.exit()
        
        nowdir = os.getcwd()
        with open(nowdir+"\\"+fileName, 'wb') as f:
            data = self.clientSock.recv(int(reSize))
            f.write(data)
            data_transferred += len(data)
        print('파일 [%s] 받기 완료. 전송량 [%d]' %(fileName,data_transferred))

# 파일 업로드 쓰레드
class uploadThread(QThread):
    def __init__(self,parent,filename,clientSock):
        super().__init__(parent)
        self.parent = parent
        self.filename = filename
        self.clientSock = clientSock

    def run(self):
        text = '2'
        self.clientSock.send(text.encode('utf-8'))
        self.clientSock.send(filename.encode('utf-8'))

        data_transferred = 0

        if not exists(filename):
            print('해당 디렉토리에 파일[%s]이 존재하지 않음' %filename)
            sys.exit()

        nowdir = os.getcwd()
        fileSize = os.path.getsize(nowdir+"\\"+filename)
        fileSize = str(fileSize)

        self.clientSock.send(fileSize.encode('utf-8'))

        print('파일[%s] 업로드 시작...' %filename)
        with open(filename, 'rb') as f:
            data = f.read(int(fileSize))
            data_transferred += self.clientSock.send(data)
        print('파일 [%s] 업로드 완료. 전송량 [%d]' %(filename,data_transferred))


# 파일 삭제 쓰레드
class deleteThread(QThread):
    def __init__(self,parent,clientSock):
        super().__init__(parent)
        self.parent = parent
        self.clientSock = clientSock

    def run(self):
        text = '3'
        self.clientSock.send(text.encode('utf-8'))
        self.clientSock.sendall(fileName.encode('utf-8'))
        print('파일 [%s]을 서버에서 삭제하였습니다.' %fileName)

# 클라우드 시스템 창 (second window)
class System(QDialog, form_class_2) :
    def __init__(self) :
        super(System,self).__init__()
        self.setupUi(self)
        self.show()

        self.setWindowTitle('Cloud system')

        self.fileBtn.clicked.connect(self.filechoiceBtn)
        self.downBtn.clicked.connect(self.actiondownThread)
        self.upBtn.clicked.connect(self.actionupThread)
        self.delBtn.clicked.connect(self.actiondelThread)

        # QTreeview 설정
        name_list = self.printfiledir(clientSock)
        file_list = self.splitfile(name_list)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["File Name"])

        self.showTreeview(file_list)
        self.fileTree.clicked.connect(self.fileTree_Clicked)


    # 파일 다운로드 쓰레드 활성
    def actiondownThread(self):
        t = downloadThread(self,clientSock)
        t.start()

    # 파일 업로드 쓰레드 활성
    def actionupThread(self):
        t = uploadThread(self,filename,clientSock)
        t.start()

        name_list = self.printfiledir(clientSock)
        file_list = self.splitfile(name_list)
        self.showTreeview(file_list)
    
    # 파일 삭제 쓰레드 활성
    def actiondelThread(self):
        t = deleteThread(self,clientSock)
        t.start()

        name_list = self.printfiledir(clientSock)
        file_list = self.splitfile(name_list)
        self.showTreeview(file_list)

    # 파일 선택 버튼
    def filechoiceBtn(self):
        global filename
        filename = QFileDialog.getOpenFileName(self, 'Open file', '', 'All File(*);; Image File(*.png *.jpg *.jpeg)')
        filename = os.path.basename(filename[0])

        print('파일 [%s] 선택' %filename)

        if filename:
            pixmap = QPixmap(filename)

            self.imgLbl.setPixmap(pixmap)
            return filename
        else:
            QMessageBox.about(self, 'Warning', '파일을 선택하지 않음')

    # Qtreeview에서 파일 선택했을 때 파일 이름, 경로 반환 함수
    def fileTree_Clicked(self):
        global fileName

        selected_item = self.fileTree.currentIndex()
        model_item = self.model.itemFromIndex(selected_item)
        fileName = model_item.text()

        print(fileName)

        return fileName
    
    # 서버로부터 해당 유저 드라이브의 폴더/파일명을 받는 함수
    def printfiledir(self, clientSock):
        self.clientSock = clientSock
        data = self.clientSock.recv(4096)
        name_list = pickle.loads(data)

        return name_list

    # 받아온 폴더/파일명에서 파일만 분리하는 함수
    def splitfile(self, name_list):
        self.name_list = name_list
        result_filelist = []

        for word in self.name_list:
            if '.png' in word:
                result_filelist.append(word)

        return result_filelist
    
    # 분리한 폴더명, 파일명을 통해 트리뷰에 띄워주는 함수
    def showTreeview(self, file_list):
        self.file_list = file_list

        self.model.removeRows(0, self.model.rowCount())

        appleKey = "apple"
        babyKey = "baby"
        butterflyKey = "butterfly"

        apple = []
        baby = []
        butterfly = []

        myDic = {'apple' : '1.png'}

        for word in file_list:
            if ('1' or '11' or '12' or '14' or '15') in word:
                apple.append(word)
            elif '2' in word:
                baby.append(word)
            elif '3' in word:
                baby.append(word)
            elif '4' in word:
                baby.append(word)
            elif '5' in word:
                baby.append(word)
            elif '6' in word:
                butterfly.append(word)
            elif '7' in word:
                butterfly.append(word)
            elif '8' in word:
                butterfly.append(word)
            elif '9' in word:
                butterfly.append(word)

        myDic[appleKey] = apple
        myDic[babyKey] = baby
        myDic[butterflyKey] = butterfly
        
        rootItem = self.model.invisibleRootItem()
        rootItem.setText("File Name")

        for parentName, childNames in myDic.items():
            parentitem = QStandardItem(parentName)
            rootItem.appendRow(parentitem)
            for childName in childNames:
                childitem = QStandardItem(childName)
                parentitem.appendRow(childitem)

        self.fileTree.setModel(self.model)


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    mainWin = Connect() 

    #프로그램 화면을 보여주는 코드
    mainWin.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()