import sys
import os

SS_COMMAND = 0
SS_TRANSFER = 1
SS_QUIT = 2

CHAR_GOOD = '0'
CHAR_BAD = '1'
CHAR_IO = '2'


class CPSyncClient:
    def __init__(self):
        self.state = SS_COMMAND
        self.directory = os.getcwd()

        self.exit_code = CHAR_GOOD

        # COMMAND
        self.emit_buffer = ""

        # TRANSFER
        self.working_file = None

        self.checksum = 0
        self.block_size = 0
        self.rec_block = False

        self.commands = {
                "q": self.quit,
                "cd": self.enter,
                "ls": self.list_dir,
                "cat": self.read,
                "tw": self.wtransfer_begin,
                }

        self.state_exits = {
                SS_TRANSFER: self.wtransfer_exit
                }

        self.state_enters = {
                }

        self.state_processes = {
                SS_COMMAND: self.command_process,
                SS_TRANSFER: self.wtransfer_process
                }

    def start_shell(self):
        while self.state != SS_QUIT:
            self.emit_buffer = ""
            self.state_processes[self.state]()
            self.respond()

    def respond(self):
        l = len(self.emit_buffer)
        print(f"{self.exit_code} {l}\n", end='')
        print(self.emit_buffer, end='')

    def command_process(self):
        try:
            #self.exit_code = self.process_command(input("> "))
            self.exit_code = self.process_command(sys.stdin.readline().strip('\n'))
        except TypeError:
            self.exit_code = CHAR_BAD


    def state_change(self, new_state):
        if self.state in self.state_exits:
            exit_func = self.state_exits[self.state]
            exit_func()
        self.state = new_state
        if new_state in self.state_enters:
            start_func = self.state_enters[new_state]
            start_func()

    def wtransfer_begin(self, file):
        try:
            self.working_file = open(file, 'wb')
        except OSError:
            return CHAR_IO
        self.state_change(SS_TRANSFER)
        self.checksum = 0
        self.block_size = 0
        self.rec_block = False
        return CHAR_GOOD

    def wtransfer_exit(self):
        if self.working_file:
            self.working_file.close()
            self.working_file = None

    def wtransfer_process(self):
        if self.rec_block:
            self.exit_code = self.wtransfer_rblock()
        else:
            self.exit_code = self.wtransfer_rdata()

    def wtransfer_rdata(self):
        
        l = sys.stdin.readline().strip('\n')
        while len(l) == 0:
            l = sys.stdin.readline().strip('\n')


        try:
            a, b = l.split(' ')
        except ValueError:
            return CHAR_BAD
        try:
            self.block_size = int(a)
            self.checksum = int(b)
        except ValueError:
            return CHAR_BAD

        self.emit(f"metadata received\n")
        self.rec_block = True
        return CHAR_GOOD

    def wtransfer_rblock(self):
        if self.block_size == 0:
            self.state_change(SS_COMMAND)
            self.emit("exiting write mode\n")
            #TODO: Verify entire file
            return CHAR_GOOD

        d = sys.stdin.read(self.block_size)
        if not self.verify_checksum(d, self.checksum):
            return CHAR_BAD

        try:
            f = self.working_file
            assert f is not None
            f.write(d.encode('ascii'))
        except OSError:
            return CHAR_IO

        self.rec_block = False
        return CHAR_GOOD

    #TODO: This doesn't work right now
    def verify_checksum(self, data, chksum):
        return True

    def calculate_checksum(self, data):
        return 0

    def process_command(self, cmd : str):
        if (len(cmd) == 0):
            return CHAR_GOOD

        tokens = cmd.split(' ')
        if len(tokens) > 1:
            args = tokens[1:]
        else:
            args = []
        
        op = tokens[0]
        if op in self.commands:
            return self.commands[op](*args)
        return CHAR_BAD


    def emit(self, contents : str):
        self.emit_buffer += contents

    def quit(self):
        self.state_change(SS_QUIT)

    def enter(self, d : str):
        try:
            os.chdir(d)
            self.directory = os.getcwd()
        except OSError:
            return CHAR_BAD
        return CHAR_GOOD

    def list_dir(self, d = None):
        if d is None:
            files = os.listdir(self.directory)
        else:
            try:
                files = os.listdir(d)
            except OSError:
                return CHAR_BAD
        self.emit(str(files) + '\n')
        return CHAR_GOOD

    def read(self, d : str):
        try:
            f = open(d, 'rb')
        except OSError:
            return CHAR_BAD
        
        self.emit(f.read().decode('ascii') + '\n')
        f.close()
        return CHAR_GOOD


if __name__ == '__main__':
    r = CPSyncClient()
    r.start_shell()
