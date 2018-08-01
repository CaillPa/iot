import argparse
import socket
import select
import serial

import json
import urllib.parse
from urllib.request import Request, urlopen
from urllib.error import URLError

HOST = ''                   # Symbolic name meaning all available interfaces
PORT = 50012                # Arbitrary non-privileged port
TIMEOUT = 0.4               # read timeout for non-blocking I/O
SERIAL = '/dev/ttyUSB0'     # address of the serial device
BAUD = 9600                 # baudrate for the serial
DOMAIN = 'localhost:5000/'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', choices=['serial', 'interactive'], default='serial')
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setblocking(False)
        sock.bind((HOST, PORT))
        sock.listen(1)

        if args.m == 'interactive':
            run_prompt(sock)
        else:
            run_serial(sock)

def run_prompt(sock):
    while True:
        # input a line from STDIN
        print('> ', end='')
        try:
            line = input()
        except EOFError:
            print()
            break
        if line:
            print(line)

        # read from socket
        r, _, _ = select.select([sock], [], [], TIMEOUT) # one-direction socket
        if r:
            conn, addr = sock.accept()
            print('Connected by', addr)
            sock_data = conn.recv(1024)
            print('From socket :', sock_data)

def run_serial(sock):
    ser = serial.Serial(port=SERIAL, baudrate=BAUD, timeout=TIMEOUT)
    while True:
        # read from socket
        r, _, _ = select.select([sock], [], [], TIMEOUT) # one-direction socket
        if r:
            conn, addr = sock.accept()
            print('Connected by', addr)
            sock_data = conn.recv(1024)
            print('From socket :', sock_data)

        # read from serial
        ser_data = ser.read(1024)
        if(ser_data):
            cmd = ser_data.decode()
            print('From serial :', cmd)
            run_from_serial(cmd)

def run_from_serial(command: str):
    tokens = list(filter(None, command.split(' ')))
    # test for empty list
    if not tokens:
        _syntax_error(command)
        return

    if tokens[0] == 'get':
        # get needs a second token
        if len(tokens) < 2:
            _syntax_error(command)
            return

        data = {}
        data['key'] = tokens[1]
        url = DOMAIN + 'get?' + urllib.parse.urlencode(data)
        req = Request(url)
        try:
            response = urlopen(req)
            process(response.read().decode('utf-8'))
        except URLError as err:
            if hasattr(err, 'reason'):
                print('Failed to GET resource:', tokens[1])
                print('\tReason:', err.code, err.reason)
            elif hasattr(err, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', err.code)

    elif tokens[0] == "put":
        # put needs 3 tokens (put identifier value)
        if len(tokens) < 3:
            _syntax_error(command)
            return

        data = {}
        data['key'] = tokens[1]
        data['value'] = ' '.join(tokens[2:])
        data = urllib.parse.urlencode(data).encode('ascii')
        req = Request(DOMAIN+'put', data=data, method='POST')
        try:
            response = urlopen(req)
            process(response.read().decode('utf-8'))
        except URLError as err:
            if hasattr(err, 'reason'):
                print('Failed to PUT value:', tokens[1])
                print('\tReason:', err.code, err.reason)
            elif hasattr(err, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', err.code)

    elif tokens[0] == "send":
        # send value to the arduino
        pass
    
    elif tokens[0] == "read":
        # retrieve values from the arduino
        pass

    else:
        _syntax_error(command)
    pass

def process(result):
    print(result)

def _syntax_error(line):
    print('SYNTAX ERROR: '+line)

if __name__ == '__main__':
    main()
