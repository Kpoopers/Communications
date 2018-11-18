#client side
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import socket
import time
import sys
#import pandas as pd


#ip address
host = "172.20.10.3"
PORT_NUM = 7651
bs = 32

counter = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#need to include ip addres of server to be connected
sock.connect((host, PORT_NUM))
print ('Connected, action?')
key = "1234567890123456"
#key = bytes(raw_key, encoding = "utf-8")
#key = hashlib.sha256(raw_key.encode()).digest()
response = "#chicken|10|2|20|3000000000";
x = 0

def encryptText(plainText, key):
    raw = pad(plainText)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key.encode("utf8"),AES.MODE_CBC,iv)
    msg = iv + cipher.encrypt(raw.encode('utf8'))
    # msg = msg.strip()
    return base64.b64encode(msg)

def pad(var1):
	return var1 + str((bs - len(var1)%bs)*chr(bs - len(var1)%bs))

# while (x<3):
# #padding to ensure that the message is of fixed size
	# action = input("Enter action: ")
	# temp = str(action)
	# temp = temp.strip()
	# stringtosend = encryptText(temp, key)
	# sock.send(bytes(stringtosend)) #need to encode as a string as it is what is expected on server side
	# x = x+1
  
def sendToServer(action, shouldClose):
    finalString = encryptText(action,key)
    print(finalString)
    sock.send(finalString)
    #counter = counter+1
    #closes when logout is displayed and move has been detected by ml
    if (shouldClose):
        sock.close()
