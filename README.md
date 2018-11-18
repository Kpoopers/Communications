# Communications and Interfacing Hardware
Ensuring reliable communications between Arduino, Raspberry Pi and the Final Server

## Arduino
* All files in this folder should be included together in one folder.
* Compile and upload the code in `tasks_setup.ino` to the Arduino Mega.

## RPi
* All files in this folder should be included together in one folder.

### final_eval_server.py
* The final eval server program and client program can either run on the same computer (ip address set to 'localhost') or run on separate computers.
* Need to include three parameters when running the final eval server program: [ipaddress] [port number] [group number]
 
* an example : `python final_eval_server.py localhost 7651 05`

* Once server is running, run the *receive_data.py* program to run the main program on the pi.
* The `receive_data.py` program will call the `client.py` program to establish a connection.

### client.py 
* AES key is defined in the client program, so any changes to the key should be done here.
* Default Key is `1234567890123456`

### receive_data.py
* This is the main program running the process of reading data from the Arduino and the one sending the data to the machine learning model.
* Run this only after the `final_eval_server.py` has been run.
