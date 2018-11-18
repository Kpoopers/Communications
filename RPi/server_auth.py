from Crypto.Cipher import AES
import base64
import sys
import os

class server_auth:
    def __init__(self):
        super(server_auth, self).__init__()

    def decryptText(self, cipherText, Key):
        print(cipherText)
        decodedMSG = base64.b64decode(cipherText)
        print("DEcodedMSG:" + str(decodedMSG))
        iv = decodedMSG[:16]
        print("iv:" + str(iv) + str(len(iv)))
        secret_key = bytes(str(Key), encoding = "utf8")
        print("The key:" + str(secret_key))
        #secret_key = base64.b64decode(Key) #this was commented out
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)
        decryptedText = cipher.decrypt(decodedMSG[16:]).strip()
        decryptedTextStr = decryptedText.decode('utf8')
        print(decryptedTextStr)
        decryptedTextStr1 = decryptedTextStr[decryptedTextStr.find('#'):] 
        decryptedTextFinal = bytes(decryptedTextStr1[1:],'utf8').decode('utf8')
        action = decryptedTextFinal.split('|')[0]
        voltage = decryptedTextFinal.split('|')[1]
        current = decryptedTextFinal.split('|')[2]
        power = decryptedTextFinal.split('|')[3]
        cumpower = decryptedTextFinal.split('|')[4]
        return {'action': action, 'voltage': voltage, 'current': current, 'power': power, 'cumpower': cumpower} #energy





