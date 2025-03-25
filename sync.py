import argparse
import serial
import os

ser = serial.Serial('/dev/ttyACM0', 115200)

STUB = b"import client\rr = client.CPSyncClient()\rr.start_shell()\r"

parser = argparse.ArgumentParser(
        prog='CircuitPython Sync',
        description = 'Circuitpython sync tool')

parser.add_argument('--file', '-f', required = True)
parser.add_argument('--destination', '-d', default='/')

CHAR_GOOD = '0'
CHAR_BAD = '1'
CHAR_IO = '2'

def log(v):
    print(f"[*]{v}")

def reset():
    ser.write(b'\r')
    ser.write(b'\x03')
    ser.write(b'\r')

    ser.write(b'\x04')

    log(ser.readline())
    log(ser.read_until(b"Use"))
    ser.write(b'A')
    
    log(ser.read_until(b">>>"))

def start_client():
    ser.write(STUB)

def copy_directory(path, target_path):
    if os.path.isdir(path):
        d = os.listdir(path)
        for file in d:
            copy_directory(os.path.join(path, file), os.path.join(target_path, file))


def read_response(s : serial.Serial):
    meta = s.readline().strip().decode(encoding='ascii')
    log(meta)

    a, b = meta.split(' ')
    err = int(a)
    rlen = int(b)
    if rlen > 0:
        response = s.readline().decode(encoding='ascii').strip()
    else:
        response = ''
    log(response)
    return err, response

def jank():
    reset()
    start_client()
    log(ser.readline())
    log(ser.readline())
    log(ser.readline())

def write_file(s : serial.Serial, name : str, content : bytes):
    command = f'tw {name}\r'.encode('ascii')

    print(command)
    ser.write(command)
    read_response(ser)
    
    meta = f'{len(content)} 0\r'.encode('ascii')
    ser.write(meta)
    read_response(ser)

    ser.write(content)
    read_response(ser)

    ser.write(b'0 0\r')
    read_response(ser)

if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.file, 'rb') as f:
        c = f.read()

    jank()
    print("+++")
    write_file(ser, os.path.join(args.destination, os.path.basename(args.file)), c)
    #ser.write(b'tw linux.txt\r')
    #read_response(ser)


