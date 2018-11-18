#Receiving data from MEGA without using a ring buffer.
# Receives data and insert into a list. Which automatically #prints out necessary data values into the csv file
#(or other method that softwareSquad prefers)
import serial
import time
import struct
import sys
import operator
import numpy as np
import pandas as pd
import functools as ft
import csv #to write to csv file, can use pandas but see how
from ml import ML
import client

class ReceiveData():
        def __init__(self, list, port):
            self.port = port
            self.list = list
            self.voltage = 0
            self.current = 0
            self.power = 0
            self.cumpower = 0

        def run(self):
            #Handshaking, keep saying 'H' to Arduino until Arduino reply 'A'
            while(self.port.in_waiting == 0 or self.port.read() != str('A').encode()):
                print ('Connecting to Arduino')
                self.port.write(str('H').encode())
                time.sleep(1)
            self.port.write(str('A').encode())
            print ('Connected')
            time.sleep(55)
            print('Start Dancing!')
            self.comms()

        def comms(self):
            store = StoreData(self.port, self.list, self.voltage, self.current, self.power, self.cumpower)
            result = False
            while(1):
                result = self.readData()
                store.updateData(self.voltage, self.current, self.power, self.cumpower)
                if(result == True):  #checksum matches
                    #print("A to send")
                    store.run()
                    self.port.write(str('A').encode())
                    #print("A sent")
                else:
                    self.port.write(str('N').encode())
                    ##print('N sent')
                #clears the list(once data has been stored) to prepare for the next packet
                #or to discard errorneous data (NACK)
                del self.list[:]

        def readData(self):
                #wait for data
                while(self.port.in_waiting <= 0):
                    time.sleep(0.03)

                #receiving data from arduino
                self.voltage = float(self.port.readline())
                self.current = float(self.port.readline())
                self.power = float(self.port.readline())
                self.cumpower = float(self.port.readline())

                size = self.port.readline()
                size = size.decode('utf-8')
                #size = int(size)
                #size = 14
                #print(size) #to check if the first data has been received
                size = int(size)

                for i in range(size - 2):
                    data = self.port.readline()
                    #print('sdifsd' + str(data))
                    data = data.decode('utf-8')
                    data = int(data)
                    self.list.append(data)
                checksum = self.port.readline()
                checksum = int(checksum)

                #check checksum
                value = 0
                for i in range(size-2):
                    value ^= self.list[i]
                ##print(value)

                ack = False
                if(value == checksum):
                    ack = True  #ack current sample
                    #print("checksum match")
                else:
                    ack = False #if data has error, NACK
                    #print("checksum does not match")

                return ack

class StoreData():
        def __init__(self, port, row_list, voltage, current, power, cumpower):
            self.port = port
            self.row_list =  row_list
            self.columns = ['ax1', 'ay1', 'az1', 'gx1', 'gy1', 'gz1','ax2', 'ay2', 'az2', 'gx2', 'gy2', 'gz2']
            self.df = pd.DataFrame(columns = self.columns)
            self.counter = 0
            self.voltage = voltage
            self.current = current
            self.power = power
            self.cumpower = cumpower
            self.model = ML()

        def run(self):
            #print("storing data")
            self.storeData()

        def storeData(self):
            #df = pd.DataFrame(self.list, columns = self.columns, header = None)

            self.df.loc[self.counter] = self.row_list
            #self.df.append(pd.DataFrame([self.row_list], columns=self.columns), ignore_index=False)
            #print("list appended!")
            #print(self.df)
            
            self.counter += 1
            
            #check if client program to end
            shouldClose  = False
            
            #collect adequate data for machine learning model
            if(self.counter == 60):
                #function call
                action = self.model.predict(self.df)
                print(action)
                
                    if action == 'logout':
                        shouldClose = True
                        data = "#" + action + "|" + str(self.voltage) + "|" + str(self.current) + "|" + str(self.power) + "|" + str(self.cumpower) + "|"
                        client.sendToServer(data, shouldClose)
                        quit()

                    else:
                        #send action to server
                        data = "#" + action + "|" + str(self.voltage) + "|" + str(self.current) + "|" + str(self.power) + "|" + str(self.cumpower) + "|"
                        client.sendToServer(data, shouldClose)
                    
                    self.df = pd.DataFrame(columns=self.columns)
                    # print('Going to sleep bye bye ...')
                    time.sleep(2)
                    print('Woke up.')
                
                self.counter = 0

            #self.send_server(action, self.voltage,self.current,self.power,self.cumpower) #send all the shit to 
            #for training of ml model and data collection purposes
                # with open('data.csv', 'a+') as f:
                # sel.df = pd.DataFrame(list, index[0])[self.columns].set_index('ax1')

                # if (self.counter == 600):
                #     print("600 Values!")
                #     self.df.to_csv('data.csv', sep =',')
                #     print("wrote to csv")
	            #writer = csv.writer(outfile)
                #     writer.writerow(data)
                #     #print("Wrote to csv")
            
        def updateData(self, voltage, current, power, cumpower):
            self.voltage = voltage
            self.current = current
            self.power = power
            self.cumpower = cumpower

class Raspberry():
        def __init__(self):
            self.list = [] #creating a list to store a packet of sensor data received by the arduino
            #dont need to use a ring buffer, as arduino side already  has one!

        def main(self):
            #set up port connection
            self.port=serial.Serial('/dev/ttyS0',115200)
            receive = ReceiveData(self.list, self.port)
            receive.run()

if __name__ == '__main__':
        pi = Raspberry()
        pi.main()
