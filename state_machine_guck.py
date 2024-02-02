#!/usr/bin/python3

__author__ = 'Thomas@chriesibaum.com'
__app_name__ = 'state_machine_guck'
__version__ = '0.1.1_dev'
__copyright__ = '(c) 2022 - 2023 CHRIESIBAUM GmbH'


import argparse
import sys
import os
import glob
from PyQt5 import QtWidgets

from fsm_gui import Fsm_Gui
from read_events import Read_Events


def main():
    """
    Main function of the state_machine_guck tool

    :return: None

    Parses the command line arguments and setups and starts the gui. For each
    svg file in the svg directory a Fsm_Gui object is created and opened (for
    the *_sub and *_overview state machine). The Read_Events object is started
    in a separate thread and the callback function of the Fsm_Gui objects is
    set. This callback function is called whenever a new state is entered.
    """

    # Instantiate the parser
    parser = argparse.ArgumentParser(description='The state_machine_guck tool')

    parser.add_argument('--version', const=True, action='store_const', default=False,
                        help='Prints the tool version')

    parser.add_argument('-d', '--svg_dir', metavar='<svg dir>', type=str, default='./svg/',
                        help='directory containing the svg files')

    parser.add_argument('-s', '--serial_line', metavar='<serial line>', type=str, default='/tmp/ttyACM0-V1',
                        help='serial line to read the fsm events from')

    args = parser.parse_args()

    # basic args check
    if args.version:
        print('%s' % (__version__))
        sys.exit(0)

    if not os.path.isdir(args.svg_dir):
        print(f'Error: directory "{args.svg_dir}" does not exist')
        sys.exit(1)

    fsm_filenames = glob.glob(args.svg_dir + '*.svg')

    if fsm_filenames == []:
        print(f'Error: no svg files found in directory "{args.svg_dir}"')
        sys.exit(1)

    event_logic = Read_Events(args.serial_line)

    app = QtWidgets.QApplication(sys.argv)

    app.setApplicationName(__app_name__)

    screen = app.primaryScreen()

    for fsm_filename in fsm_filenames:

        # just show the sub state machines and the overview fsm's
        if ((fsm_filename.find('sub') > 0) or (fsm_filename.find('overview') > 0)):

            fsm_window = Fsm_Gui(screen)
            fsm_window.load_svg(fsm_filename)
            fsm_window.show()

            event_logic.set_callback(fsm_window.set_active_state)

    event_logic.start()

    ret = app.exec_()

    event_logic.stop()

    sys.exit(ret)


if __name__ == "__main__":
    main()
