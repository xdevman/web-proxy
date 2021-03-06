#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, socket, threading, select, json
from urlparse import urlparse

__version__ = '0.1.0 Draft 1'
BUFLEN = 2000000
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.client = connection
	self.client_buffer = ''
	self.timeout = timeout
	self.method, self.path, self.protocol = self.get_base_header()
	if urlparse(self.path).netloc == "":
            self.path = ""
	elif urlparse(self.path).netloc == "sanjesh.org":   ##Enter your address
            self.path = ""
	print self.path
	if self.method == 'CONNECT':
	    self.method_CONNECT()
	elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE'):
            self.method_others()
	dar = float(self.dar / 1024.0)
	dar = "%.5s" %( str(dar) )
	dar = "%s KB" %( dar)
	print 'Recived: {}'.format(dar)
	self.dar = float(0)
	self.client.close()
	self.target.close()
    def get_base_header(self):
        while 1:
            
            self.client_buffer += self.client.recv(BUFLEN)
	    end = self.client_buffer.find('\n')
	    if end!=-1:
		break
	self.dar = float(len(self.client_buffer))
        #dar = float(dar / 1024.0)
	#dar = "%.5s" %( str(dar) )
	#dar = "%s KB" %( dar)
	#print '{}'.format(self.client_buffer[:end])
	#print 'Recived: {}'.format(dar)
	data = (self.client_buffer[:end+1]).split()
	self.client_buffer = self.client_buffer[end+1:]
	return data
    
    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(HTTPVER+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()

    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]
        path = self.path[i:]
        self._connect_target(host)
        self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+
                         self.client_buffer)
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i!=-1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 80
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family)
        self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count +=1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    self.dar += float(len(self.client_buffer))
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        out.send(data)
                        count = 0
            if count == time_out_max:
                break
def start_server(host='0.0.0.0', port=8080, IPv6=False, timeout=60, handler=ConnectionHandler):
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type)
    soc.bind((host, port))
    print "Serving on %s:%d."%(host, port) #debug
    soc.listen(0)
    while 1:
        conn, addr = soc.accept()
        t=threading.Thread(target=handler, args=(conn, addr, timeout))
        t.setDaemon(True)
        t.start()
if __name__ == '__main__':
    start_server()
