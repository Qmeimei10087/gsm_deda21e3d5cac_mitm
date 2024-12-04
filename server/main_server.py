import socket
import threading
import json

from Utils.Log import*
from Utils.Constant import*
from Utils.Server import*
from Utils.Load_Config import*


if __name__ == "__main__":
    config = load_config()
    bts_list = []
    for cfg in config["OpenBTS"]:
        bts_list.append(BTS_Server(cfg["lport"],cfg["rport"]))
    
    for bts in bts_list:
        bts.run()
    mb = MB_Server(config["Mobile_Port"])    
    mb.run()
