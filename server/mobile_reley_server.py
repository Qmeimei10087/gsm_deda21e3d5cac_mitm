import socket
import json
import threading
import sys

from Utils.Log import*
from Utils.Constant import*
init(autoreset=True)

def handle_msg(msg):
    return msg.replace(" ","")


class Client:
    def __init__(self,rport,rhost,lport):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((rhost, rport))
        LOG(SUCCESS,f"SUCCESS to connect the remote server(TCP) "+rhost+":"+str(rport))
        self.client_socket.settimeout(15.0)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1',lport))
        self.server_socket.listen(1)
        LOG(PROCESS,f"Mobile local server(TCP) is listening on "+str(lport))
        



    def mobile_server(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(addr)
            
            raw_msg = conn.recv(1024)
            msg = handle_msg(raw_msg.decode())
            print(msg)
            parts = msg.split(";")
            imsi = parts[1]
            rand = parts[0]
            LOG(SUCCESS,"[From Mobile-"+imsi+"]Received authorization request! RAND:"+rand+",now send to remote server")
            data = json.dumps({"IMSI":imsi,"RAND":rand})
            self.client_socket.send(data.encode())
            LOG(PROCESS,"Waiting for SRES.............")
            
            try:
                raw_msg = self.client_socket.recv(1024)
                msg = json.loads(raw_msg.decode())
                if msg["SRES"] == '00000000':
                    LOG(WARNING,"Detect sres :00000000, it is dummy sres. Is OpenBTS Server running? Or the imsi is not found in tmsis_table")
                LOG(SUCCESS,"Received SRES from server :"+str(msg)+" ,now send to Mobile-"+imsi)
                conn.send(msg["SRES"].encode())

            except socket.timeout:
                LOG(ERROR,"Timeout! Is remote server running? now send dummy SRES to Mobile-"+imsi)
                dummy_sres = "00000000"
                conn.send(dummy_sres.encode())


            

    def run(self):
        threading.Thread(target=self.mobile_server).start()


if __name__ == "__main__":
    rhost = sys.argv[1]  # 第一个参数
    rport = sys.argv[2]
    client = Client(int(rport),rhost,8888)
    client.run()




