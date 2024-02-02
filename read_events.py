import sys
import threading
import serial
import re


class Read_Events(threading.Thread):
    def __init__(self, serial_line_name='/tmp/ttyACM0-V1'):
        threading.Thread.__init__(self)
        self.running = False
        self.callbacks = []

        try:
            self.serial_line = serial.Serial(
                serial_line_name, 38400, timeout=0.1)
        except:
            print(f'Error: could not open serial line "{serial_line_name}"')
            sys.exit(1)

    def start(self):
        self.running = True
        super().start()

    def stop(self):
        self.running = False

    def set_callback(self, callback):
        self.callbacks.append(callback)

    def run(self):
        p_state_enter = re.compile(
            r'^\[[\d:.,]*\] <inf>.fsm..-->.Entered: (\w*): (\w*.\w*) ')
        p_ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        while self.running:

            log_line = self.serial_line.readline()

            if len(log_line) > 0:			# and l.find(b'fsm: --> Entered:') != -1:

                log_line = log_line.decode('utf-8')
                log_line = log_line.strip()
                log_line = p_ansi_escape.sub('', log_line)

                m_state_enter = p_state_enter.match(log_line)

                if m_state_enter is not None:

                    state_type = m_state_enter.group(1)

                    if state_type == 'State':
                        state = m_state_enter.group(2)
                    elif state_type == 'StateMachine':
                        state = m_state_enter.group(2)
                        state = state.split('.')[1]

                    print(f'state: {state}')

                    for callback in self.callbacks:
                        try:
                            callback(state)
                        except:
                            print('callback failed!')
