from Utils.Constant import*
from Utils.Constant import*
from Utils.Colorful_Output import*


'''
Log_List = []

def LOG_Global(Log_Info):
	global Log_List
	if Log_Info[Level] == SUCCESS:
		color_print(GREEN,"[+] "+Log_Info[text])
	elif Log_Info[Level] == PROCESS:
		color_print(BLUE,"[*] "+Log_Info[text])
	elif Log_Info[Level] == ERROR:
		color_print(RED,"[-] "+Log_Info[text])
	elif Log_Info[Level] == WARNING:
		color_print(YELLOW,"[!] "+Log_Info[text])
	else:
		print("[UNKNOWN LEVEL] ",Log_Info[text])
	Log_List.append(Log_Info)

'''

def LOG(Level,text):
	if Level == SUCCESS:
		color_print("[+] "+text,GREEN)
	elif Level == PROCESS:
		color_print("[*] "+text,BLUE)
	elif Level == ERROR:
		color_print("[-] "+text,RED)
	elif Level == WARNING:
		color_print("[!] "+text,YELLOW)
	else:
		print("[UNKNOWN LEVEL] ",text)

'''
	
def Creat_LOG_Data(Level,From,text):
	log_data = {'Level':Level,'From':From,'text':text,'broadcasted':False}
	return log_data

def Broadcast_Log():
	pass
'''

