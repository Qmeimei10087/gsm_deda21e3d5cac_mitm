import socket
import threading
import json

from Utils.Log import*
from Utils.Constant import*
init(autoreset=True)

tmsis_table = [{"test":12345},{"460072245216963":12345}]

class BTS_Server:
    def __init__(self, lport, rport):
        
        self.lport = lport
        self.rport = rport
        
        self.r_connected = False
        self.r_conn = None
        self.l_addr = None

        self.r_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.r_sock.bind(("0.0.0.0",self.rport))
        self.r_sock.listen(5)

        self.l_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.l_sock.bind(("127.0.0.1", lport))

        LOG(PROCESS,f"OpenBTS remote server(TCP) is listening on "+str(rport)+", Local server(UDP) is listening on "+str(lport))
        


    def tcp_listener(self):
        global tmsis_table
        while True:
            self.r_conn, addr = self.r_sock.accept()
            LOG(SUCCESS,"OpenBTS Server is Connected by "+str(addr))
            self.r_conn.settimeout(15.0)
            self.r_connected = True
            while True:
                try:
                    raw_msg = self.r_conn.recv(1024)
                    LOG(WARNING,"[DEBUG]"+raw_msg.decode())
                    
                    msg = json.loads(raw_msg.decode())
                    if msg["EVENT"] == "HEARTBEAT":
                        LOG(PROCESS,"[From OpenBTS-"+str(addr)+"] EVENT: HEARTBEAT")
                           
                        self.r_conn.sendall(b"ok")
                        pass
                    elif msg["EVENT"] == "AUTH":
                            #imsi = msg["IMSI"]
                        sres = msg["SRES"]
                        LOG(SUCCESS,"[From OpenBTS-"+str(addr)+"] EVENT:AUTHORIZATION "+" SRES:"+sres)
                        LOG(PROCESS,"Now send to Mobile")
                        self.l_sock.sendto(sres.encode(), self.l_addr)
                    elif msg["EVENT"] == "SIP":
                            imsi = msg["IMSI"]
                            LOG(SUCCESS,"[From OpenBTS-"+str(addr)+"}] EVENT:SUBSCRIBE IMSI:"+imsi)
                            tmsis_table.append({imsi:self.lport})
                            
                    else:
                        LOG(ERROR,"Unknown Message")
                    #except:
                        #LOG(ERROR,"process json data faild")

                except socket.timeout:
                    self.r_connected = False
                    LOG(ERROR,"OpenBTS-"+str(addr)+" dead! Reason: timeout")
                    break
                except json.decoder.JSONDecodeError:
                    LOG(ERROR,"Pocessing json data faild ")
                    break
                except:
                    self.r_connected = False
                    LOG(ERROR,"OpenBTS-"+str(addr)+" dead! Reason: Unknown")
                    break
               

                
    def udp_listener(self):
        while True:
            msg, self.l_addr = self.l_sock.recvfrom(1024)
            if self.r_connected:
                LOG(SUCCESS,"Detect OpenBTS state: active! Now send rand to OpenBTS")
                self.r_conn.sendall(msg.decode().encode())
            else:
                LOG(ERROR,"Detect OpenBTS state: dead! Now send dummy rand to OpenBTS")
                sres = b'000000000'
                self.l_sock.sendto(sres, self.l_addr)
    
    def show_lport(self):
        return self.lport
    def in_tmsis_table(imsi):
        for tmsis in self.tmsis_table:
            if tmsis == imsi:
                return True
        return False

    def run(self):
        threading.Thread(target=self.tcp_listener).start()
        threading.Thread(target=self.udp_listener).start()



class MB_Server:
    def __init__(self,rport):
        self.rport = rport
        self.r_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.r_sock.bind(("0.0.0.0",self.rport))
        self.r_sock.listen(5)
        LOG(PROCESS,f"Mobile remote server(TCP) is listening on "+str(rport))

    def find_bts_by_imsi(self,imsi):
        global tmsis_table
        for tmsis in tmsis_table:
            for key in tmsis.keys():
                if key == imsi:
                    return tmsis[key]
        return None

    def handle_connection(self,conn,addr):
        l_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        l_sock.settimeout(10.0)
        while True:
            raw_msg = conn.recv(1024)
            #LOG(WARNING,"[DEBUG]"+raw_msg.decode())
            msg = json.loads(raw_msg.decode())
            LOG(SUCCESS,"[From Mobile-"+str(addr)+"] Receive Message form Mobile ,MSG:"+str(msg)+",now finding the BTS who had the imsi")
            lport = (self.find_bts_by_imsi(msg["IMSI"]))
            if lport:
                LOG(SUCCESS,"[From Mobile-"+str(addr)+"] IMSI found,the local port: "+str(lport)+",now requesting for the sres")
                l_sock.sendto(raw_msg, ('127.0.0.1',lport))
                try:
                    LOG(PROCESS,"[[From Mobile-"+str(addr)+"]] Waiting for sres........")
                    raw_sres, _ = l_sock.recvfrom(1024)
                    sres = raw_sres.decode()
                except socket.timeout:
                    LOG(ERROR,"[From Mobile-"+str(addr)+"] Timeout! Is OpenBTS running? Now sending the dummy sres")
                    sres = "00000000"
                data = json.dumps({"IMSI":msg["IMSI"],"SRES":sres})
                conn.send(data.encode())
            else:
                LOG(ERROR,"[From Mobile-"+str(addr)+"] IMSI not found! Now sending the dummy sres")
                data = json.dumps({"IMSI":msg["IMSI"],"SRES":'00000000'})
                
                conn.send(data.encode())

    def tcp_listener(self):
        while True:
            conn, addr = self.r_sock.accept()
            LOG(SUCCESS,"Mobile server was connected by "+str(addr))
            threading.Thread(target=self.handle_connection, args=(conn, addr)).start()
    def run(self):
         threading.Thread(target=self.tcp_listener).start()



