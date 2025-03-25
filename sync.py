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

CHAR_GOOD = 0
CHAR_BAD = 1
CHAR_IO = 2

MASK_DIR = 14

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

def setup():
    reset()
    start_client()
    log(ser.readline())
    log(ser.readline())
    log(ser.readline())

def cmd(name : str, *args):
    r = " ".join(args)
    command = f'{name} {r}\r'.encode('ascii')
    print(command)
    ser.write(command)
    return read_response(ser)

def tw(name : str):
    return cmd('tw', name)

def stat(name : str):
    return cmd('stat', name)

def mkdir(name : str):
    return cmd('mkdir', name)

def send_metadata(block_size : int, checksum : int = 0):
    meta = f'{block_size} {checksum}\r'.encode('ascii')
    ser.write(meta)
    return read_response(ser)

def send_raw(data):
    ser.write(data)
    return read_response(ser)

def write_file(s : serial.Serial, name : str, file : str):
    with open(file, 'rb') as f:
        content = f.read()

    tw(name)
    send_metadata(len(content), 0)
    send_raw(content)
    send_metadata(0, 0)

def copy_directory(source, target_path):
    print(source, target_path)

    if os.path.isdir(source):
        # Make this directory
        dirname = target_path
        if dirname[-1] == '/':
            dirname = dirname[:-1]

        code, _ = mkdir(dirname)
        if code != CHAR_GOOD:
            code, r = stat(dirname)
            if code != CHAR_GOOD:
                raise ValueError(f"Unable to create directory {dirname} on target, mkdir failed")
            t = int(r.split(' ')[0])
            if ((t >> MASK_DIR) & 1):
                log(f"Directory {dirname} already exists, skipping")
            else:
                raise ValueError(f"Unable to create directory {dirname} on target, already exists as a file")


        # Continue down other files
        files = os.listdir(source)
        for file in files:
            print(file)
            copy_directory(os.path.join(source, file), os.path.join(target_path, file))
    else:
        filename = target_path
        write_file(ser, filename, source)



if __name__ == '__main__':
    args = parser.parse_args()

    target_dir = args.destination
    if not os.path.exists(args.file):
        raise ValueError("Files to sync should exist")
    if os.path.isdir(args.file):
        target_dir = os.path.join(target_dir, os.path.dirname(args.file))
        print(args.file)

    setup()
    print("+++")
    copy_directory(args.file, target_dir)
    #write_file(ser, os.path.join(target_dir, os.path.basename(args.file)), args.file)
    #ser.write(b'tw linux.txt\r')
    #read_response(ser)


