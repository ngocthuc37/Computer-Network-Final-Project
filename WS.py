import socket
import time
import threading
import re
import os


"""
HTTP Web Server
"""

class WebServer:
    """ port mac dinh la 80, gioi han truy cap cung luc la 5 """
    HTTP_PORT = 80
    _BACKLOG = 5

    """
    khoi tao cac gia tri ban dau cua webserver voi port la 80.
    
    """
    def __init__(self, port = HTTP_PORT):
        self._host = socket.gethostname()   #lay host name cua may chu
        self._addr = socket.gethostbyname(self._host) # lay ip cua may chu
        self._port =  port # port 
        self._serverDir = os.getcwd().split('\\WS Python')[0] + '\\WB HTML'           #thu muc hien tai chua file server va cac web brower

    """
    tao server socket su dung dia chi IPv4 va giao thuc TCP
    """
    def create(self):
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         #tao server socket, AF_INET: thiet lap duoi dang IPv4, sock_stream: giao thuc TCP

        try:
            self._serverSocket.bind((self._host, self._port))                          #lang nghe den dia chi host tren cong port
            #in cac thong tin cua server
            print("\nThong tin Server:")
            print(f"\tHost : {self._host}")
            print(f"\tIP address: {self._addr}")
            print(f"\tPort: {self._port}\n")
        # ngoai le    
        except Exception as e:
            print(f"Khong the ket noi den server tren port {self._port}.")
            print(e)
            self._serverSocket.shutdown(socket.SHUT_WR)
            
        self._listen()                                                                  #lang nghe ket noi tu client

    """
    ham lang nghe ket noi tu client
    """
    def _listen(self):
        self._serverSocket.listen(self._BACKLOG)                                       # thiet lap mo ket noi tren server voi gioi han truy cap dong thoi la 5
        #tao vong lap ket noi
        while True:
            (clientSocket, clientAddr) = self._serverSocket.accept()                  # chap nhan 1 ket noi va tra ve thong so la conn va address cua client de co the gui nguoc ve client
            print(f"Ket noi tu {clientAddr} duoc chap thuan.")
            threading.Thread(target = self._handleClientRequest, args = (clientSocket, clientAddr)).start() # xu li da luong: goi ham _handleClientRequest voi cac tham so cS, cA 
    """
    ham xu ly yeu cau tu client.
    """
    def _handleClientRequest(self, clientSocket, clientAddr):
        #ten dang nhap va mat khau mac dinh
        _USERNAME = "admin"
        _PASSWORD = "admin"
        PACKET_SIZE = 4096 # maximum byte of packet from client
        location = None # vi tri cua trang hien tai
        
        data = clientSocket.recv(PACKET_SIZE).decode()                                 #doc noi dung tu client gui den ( method (get or post) tu trang index )
    
        #khong ton tai -> ket thuc
        
        if not data:
            return

        #tach du lieu tu client de xem yeu cau la gi
        methodRequest = data.split(' ')[0]

        #neu la GET thi redirect den trang index.html
        if methodRequest == "GET":
            fileRequested = data.split(' ')[1]
          
            if fileRequested == '/':
                fileRequested = "/index.html" 
                location = "index.html"
                responseCode = 301
            else:
                responseCode = 200
        elif methodRequest == "POST":     #neu la POST
            #lay username va password tu yeu cau cua POST
            pattern = r"(?:username=)(?P<username>.*)(?:&password=)(?P<password>.*)"    
            match = re.search(pattern, data) # ham search: tim kiem su xuat hien dau tien cua pattern ben trong string 
            
            #neu username va password dung thi chuyen den trang info.html, sai chuyen toi 404.html
            if match:
                if match.group("username") == _USERNAME and match.group("password") == _PASSWORD:   
                    fileRequested = "/info.html"
                    location = "info.html"  
                else:   
                    fileRequested = "/404.html"
                    location = "404.html"

                responseCode = 301
                
        #mo file yeu cau va tao header tra ve
        try:
            fileResponseClient = open(self._serverDir + fileRequested, 'rb') #mo file
            dataResponse = fileResponseClient.read() # doc du lieu tra ve
            responseHeader = self._createResponseHeader(responseCode, location) #tao header tra ve
            
        #neu ko mo duoc file resquest 
        except:  
            responseCode = 404
            fileResponseClient = open(self._serverDir + "/404.html", 'rb') #mo file
            dataResponse = fileResponseClient.read() #doc du lieu  tra ve
            responseHeader = self._createResponseHeader(responseCode) # tao header tra ve qua ham _createResponseHeader 
            
        finally:
            fileResponseClient.close()
        
        #gui header va data den client
        responseToClient = responseHeader.encode() # ma hoa (utf-8) header response
        responseToClient += dataResponse 

        clientSocket.send(responseToClient) # gui du lieu tu client

        #Dong ket noi
        clientSocket.close()

    """
    Tao HTTP header
    Tro giup cac code 200, 301, 404
    Tra ve header bao gom status line, header lines  nhu slide 12
    """
    def _createResponseHeader(self, responseCode, location = None):
        #status line
        SERVER_NAME = 'Python.Webserver'
        HTTP_200_HEADER = 'HTTP/1.1 200 OK\r\n'
        HTTP_301_HEADER = 'HTTP/1.1 301 Moved Permanently\r\n'
        HTTP_404_HEADER = 'HTTP/1.1 404 Not Found\r\n'

        #append header 
        header = ''
        if responseCode == 200:
            header += HTTP_200_HEADER
        elif responseCode == 301:
            header += HTTP_301_HEADER
        elif responseCode == 404:
            header += HTTP_404_HEADER
            
        # them location vao header
        if location:
            header += f"Location: /{location}\n"
        
     #header lines
        #dinh dang header lines bao gom thoi gian, server, loai ket noi 
        cur_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += f"Date: {cur_time}\r\n"
        header += f"Server: {SERVER_NAME}\r\n"
        header += "Connection: close\r\n\n"
        
        return header
"""
    ket thuc class WebServer
"""

if __name__ == "__main__":
    web_server = WebServer(80)
    web_server.create()
