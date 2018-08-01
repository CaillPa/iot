import serial
import urllib.parse
from urllib.request import Request, urlopen
from urllib.error import URLError

SERIAL = '/dev/ttyUSB0'
BAUD = 19200
DOMAIN = 'http://localhost:5000/'
TIMEOUT = 0.2

def run(pipe):
    if pipe is None:
        print("No pipe passed, aborting")

    ser = serial.Serial(port=SERIAL, baudrate=BAUD, timeout=TIMEOUT)

    while True:
        # forward the commands from the server to the serial
        if pipe.poll():
            pipe_data = pipe.recv()
            # the server should send custom datagrams
            # put key value
            # get key
            # no check bc yolo
            
            ser.write(pipe_data.encode())

        # read and interpret from the serial
        ser_data = ser.read(1024)
        
        if ser_data:
            try:
                cmd = ser_data.decode()
            except UnicodeDecodeError:
                break
            
            # here we should receive JSON-formatted data
            # one key-value pair by message
            # we should send it via HTTP to the server, which will store it
            process(cmd)

def process(cmd):
    # process command received from the Arduino
    tokens = list(filter(None, cmd.split(' ')))
    if not tokens:
        return

    if tokens[0] == 'get':
        pass

    elif tokens[0] == 'put':
        if len(tokens) < 3:
            return

        data = {}
        data['key'] = tokens[1]
        data['value'] = ' '.join(tokens[2:])
        data = urllib.parse.urlencode(data).encode('ascii')
        req = Request(DOMAIN+'put', data=data, method='POST')
        try:
            response = urlopen(req)
            process(response.read().decode('utf-8'))
        except URLError:
            pass
        pass
