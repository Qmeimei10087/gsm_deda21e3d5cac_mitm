import json

def load_config():
	with open("config.json",'r',encoding='UTF-8') as f:
		result = json.load(f)
	return result

def load_imsi_black_list():
	with open("blacklist.json",'r',encoding='UTF-8') as f:
		result = json.load(f)
	return result
