import pprint
import re
import socket
import threading
import time

SERVER_IP = "127.0.0.1"
#CLIENT_IP = "127.0.0.1"
PORT = 5005
MESSAGES = ["Hello",", World!"," My"," name"," is"," RobOt."]
BUFFER = {}


####CLIENTE####
#Enviar mensagens ordenadas sequencialmente
def sequencial(msgs, src_ip, dest_ip, dest_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if dest_ip == "localhost" or dest_ip == "127.0.0.1":
        dest_ip = socket.gethostbyname(socket.gethostname())
    if src_ip == "localhost" or src_ip == "127.0.0.1":
        src_ip = socket.gethostbyname(socket.gethostname())
    index = 1
    if msgs == "":
        sock.sendto("".encode("utf-8"), (dest_ip, dest_port)) #Close connection
    else:
        for msg in msgs:
            msg = src_ip + " $$ " + str(index) + " $$ " + msg
            sock.sendto(msg.encode("utf-8"), (dest_ip, dest_port))
            print ("Enviado sequencial : " + msg)
            index+=1
    sock.close()

#Enviar mensagens fora de ordem
def naoSequencial(msgs, src_ip, dest_ip, dest_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if dest_ip == "localhost" or dest_ip == "127.0.0.1":
        dest_ip = socket.gethostbyname(socket.gethostname())
    if src_ip == "localhost" or src_ip == "127.0.0.1":
        src_ip = socket.gethostbyname(socket.gethostname())
    index = 1
    if msgs == "":
        sock.sendto("".encode("utf-8"), (dest_ip, dest_port)) #Close connection
    else:
        for msg in msgs:
            if index == 1:
                msg = src_ip + " $$ " + str(2) + " $$ " + msg
            elif index == 2:
                msg = src_ip + " $$ " + str(1) + " $$ " + msg
            else:
                msg = src_ip + " $$ " + str(index) + " $$ " + msg
            sock.sendto(msg.encode("utf-8"), (dest_ip, dest_port))
            print ("Enviado fora de ordem : " + msg)
            index+=1
    sock.close()

#Simula o Envio de mansagens perdidas
def perdida(msgs, src_ip, dest_ip, dest_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if dest_ip == "localhost" or dest_ip == "127.0.0.1":
        dest_ip = socket.gethostbyname(socket.gethostname())
    if src_ip == "localhost" or src_ip == "127.0.0.1":
        src_ip = socket.gethostbyname(socket.gethostname())
    index = 2
    if msgs == "":
        sock.sendto("".encode("utf-8"), (dest_ip, dest_port)) #Close connection
    else:
        for msg in msgs:
            msg = src_ip + " $$ " + str(index) + " $$ " + msg
            sock.sendto(msg.encode("utf-8"), (dest_ip, dest_port))
            print ("Enviado com perda : " + msg)
            index+=1
    sock.close()
#Envia mensagens duplicadas
def duplicada(msgs, src_ip, dest_ip, dest_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    if dest_ip == "localhost" or dest_ip == "127.0.0.1":
        dest_ip = socket.gethostbyname(socket.gethostname())
    if src_ip == "localhost" or src_ip == "127.0.0.1":
        src_ip = socket.gethostbyname(socket.gethostname())
    index = 1
    if msgs == "":
        sock.sendto("".encode("utf-8"), (dest_ip, dest_port)) #Close connection
    else:
        for msg in msgs:
            msg = src_ip + " $$ " + str(index) + " $$ " + msg
            sock.sendto(msg.encode("utf-8"), (dest_ip, dest_port))
            print("Enviado duplicado : " + msg)
            sock.sendto(msg.encode("utf-8"), (dest_ip, dest_port))
            print ("Enviado duplicado : " + msg)
            index+=1
    sock.close()


####SERVER####
#Recebe simultaneamente msg dos clientes
    #Precisa ter identificador de origem no header
def listener(buff, port ):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ip = socket.gethostbyname(socket.gethostname())
    s.bind((ip, port))
    while True:
        data = s.recv(1024).decode()
        if not data:
            s.close()
            pprint.pprint(buff)
            break
        data = data.split(" $$ ")
        if data[0] not in buff:
            buff[data[0]] = []
        buff[data[0]].append((data[1], data[2]))

#Trata msgs duplicadas
    #Identificação de duplicidade por ID
#Trata msgs fora de ordem
#Consome o buffer do cliente
    #Trata msgs perdidas ou que não chegaram a tempo
def printMsg(buff):
    for src, msgs in buff.items():
        buff[src] = list(dict.fromkeys(msgs))  #dedup
        buff[src].sort(key=lambda tup: tup[0]) #ordena

    for src in buff:
        for i in range(1,len(list(buff[src]))): #valida pacotes faltantes
            if i != int(buff[src][i-1][0]):
                buff[src] = "Mensagem corrompida!"
                break
    pprint.pprint(buff)

def Main():

    threading.Thread(target = listener, args = (BUFFER, PORT)).start()
    sequencial(MESSAGES, "localhost", SERVER_IP, PORT)
    naoSequencial(MESSAGES, "4.4.4.4", SERVER_IP, PORT)
    perdida(MESSAGES, "1.1.0.1", SERVER_IP, PORT)
    duplicada(MESSAGES, "2.1.0.1", SERVER_IP, PORT)
    print("\n\n\nBUFFER ENVIADO\n\n\n")
    sequencial("", "0.0.0.0", SERVER_IP, PORT) #close listener
    time.sleep(1)
    print("\n\nRESULTADO!!!!!\n\n")

    printMsg(BUFFER)



if __name__ == '__main__':
	Main()

