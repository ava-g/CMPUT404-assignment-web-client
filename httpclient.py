#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
    # Copyright 2021 Ava Guo
    # 
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    # 
    #     http://www.apache.org/licenses/LICENSE-2.0
    # 
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, headers="", body=""):
        self.code = code
        self.headers = headers
        self.body = body


class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket
    

    # extract status code from server's response
    def get_code(self, data):
        return data.split("\r\n")[0].split(" ")[1]
    

    # extract headers from server's response
    def get_headers(self,data):
        headers = []
        for header in data.split("\r\n")[1:]:
            if not header:  # " " following body
                return headers
            headers.append(header)
        return headers


    # extract body from server's response
    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        

    def close(self):
        self.socket.close()


    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            # receive data from server
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    

    # helper function for extracting the content body from arguments
    def extract_body(self, args):
        # parse args to get content body
        content = ""
        if args:
            for key, value in args.items():
                content += key + "=" + value + "&"
            content = content[:-1]
        return content


    # helper function for extracting the host, port, and path from url
    def extract_host_port_path(self, url):
        # parse url to get the path
        o = urlparse(url)
        host = o.netloc.split(":")[0]
        return [host, o.port, o.path[1:]]  # [host, port, path]


    def GET(self, url, args=None):
        result = self.extract_host_port_path(url)
        host, port, path = result[0], result[1], result[2]
        
        # connect to server
        if port:
            socket = self.connect(host, port)
        else:
            socket = self.connect(host, 80)
        
        request_body = ""
        request_body += "GET /" + path + " HTTP/1.1\r\n"
        request_body += "Host: " + host + "\r\n"
        request_body += "Accept: text/html\r\n"
        request_body += "Connection: close\r\n\r\n"
        
        # send request to server
        self.sendall(request_body)

        # receive response from server
        data = self.recvall(socket)

        code = self.get_code(data)
        headers = self.get_headers(data)
        response_body = self.get_body(data)
        
        # [] As a user when I GET I want the result printed to stdout
        print("Data returned by GET:\n", data, "\n")

        return HTTPResponse(int(code), headers, response_body)


    def POST(self, url, args=None):
        # extract host, port, and path [url = "http://%s:%d/%s" % (BASEHOST,BASEPORT, path)]
        result = self.extract_host_port_path(url)
        host, port, path = result[0], result[1], result[2]

        content = self.extract_body(args)

        # connect to server
        socket = self.connect(host, port)
        
        request_body = ""
        request_body += "POST /" + path + " HTTP/1.1\r\n"
        request_body += "Host: " + host + "\r\n"
        request_body += "Content-Length: " + str(len(content)) + "\r\n"
        request_body += "Content-Type: application/x-www-form-urlencoded\r\n\r\n"
        request_body += content  # post content body

        # send post request to server
        self.sendall(request_body)

        # receive response from server
        data = self.recvall(socket)

        #code = 404
        code = self.get_code(data)
        headers = self.get_headers(data)
        response_body = self.get_body(data)

        # [] As a user when I POST I want the result printed to stdout
        print("Data returned by POST:\n", data, "\n")

        return HTTPResponse(int(code), headers, response_body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
