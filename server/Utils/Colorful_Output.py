from Utils.Constant import*
import colorama
from colorama import init,Fore,Back,Style


def color_print(text,color):
    #init(autoreset=True)
    if color == RED:
        print('\033[1;31;31m'+text)
    if color == GREEN:
        print('\033[1;31;32m'+text)
    if color == YELLOW:
        print('\033[1;31;33m'+text)
    if color == BLUE:
        print('\033[1;31;34m'+text)
    if color == WHITE:
        print('\033[1;31;37m'+text)



