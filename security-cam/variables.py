import os
import logging
import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])
    s.close()
    return address

class Variables:
    def __init__(self):

        self.stream_port = os.getenv('STREAM_PORT')
        if self.stream_port == None:
            self.stream_port = 3000
        else:
            self.stream_port = int(self.stream_port)

        self.stream_fps = os.getenv('STREAM_FPS')
        if self.stream_fps == None:
            self.stream_fps = 30
        else:
            self.stream_fps = int(self.stream_fps)
        
        self.hub_url = os.getenv('HUB_REST_ENDPOINT')
        if self.hub_url == None:
            self.hub_url = 'http://localhost:8080'

        self.threshold = os.getenv('THRESHOLD')
        if self.threshold == None:
            self.threshold = 30
        else:
            self.threshold = int(self.threshold)

        self.address = os.getenv("CAM_IP_ADDRESS")
        if self.address == None:
            self.address = get_ip_address('wlan0')

        self.hub_username = os.getenv("HUB_USERNAME")
        if self.hub_username == None:
            self.hub_username = "security-cam"

        self.hub_password = os.getenv("HUB_PASSWORD")
        if self.hub_password == None:
            self.hub_password = "password"
