"""
The fsm_gui module

This module contains the Fsm_Gui class.
"""

import os
import time
from PyQt5 import QtCore, QtWidgets, QtSvg
from lxml import etree


active_state_color = 'orange'
top_bottom_margin = 50		# margin in pixel at the top and bottom of the screen
# for the window title bar and the task bar, etc


class Fsm_Gui(QtWidgets.QMainWindow):
    """
    The Fsm_Gui class

    This class implements the fsm gui for the state_machine_guck tool.
    """

    def __init__(self, screen, parent=None):
        """
        The constructor of the Fsm_Gui class
        :param screen: the screen object
        :param parent: the parent object
        """
        super(Fsm_Gui, self).__init__()

        self.screen = screen

        self.active_state = None
        self.active_state_color = None

        self.svg_base_name = None
        self.svg_tree = None
        self.svg_root = None

        self.init_ui()

    def init_ui(self):
        """
        The init_ui method

        Initializes the user interface.
        """

        self.setWindowTitle('FSM GUI')

        self.svg_widget = QtSvg.QSvgWidget()

        self.central_widget = QtWidgets.QWidget()
        self.vertical_layout = QtWidgets.QVBoxLayout()

        self.vertical_layout.addWidget(self.svg_widget)
        self.central_widget.setLayout(self.vertical_layout)

        self.setCentralWidget(self.central_widget)

        self.show()

    def load_svg(self, svg_file):
        """
        The load_svg method

        Loads the svg file and sets the window title.

        :param svg_file: the svg file to load
        """

        self.svg_widget.load(svg_file)

        self.svg_base_name = os.path.basename(svg_file)
        self.setWindowTitle(self.svg_base_name)

        self.resize(self.svg_widget.sizeHint())
        self.svg_widget.renderer().setAspectRatioMode(QtCore.Qt.KeepAspectRatio)
        self.svg_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.svg_tree = etree.parse(svg_file)
        self.svg_root = self.svg_tree.getroot()

    def set_active_state(self, state_name):
        """
        The set_active_state method

        Sets the active state in the svg file and marks it with a different
        color. The old active state is set back to its original color. The svg
        file is reloaded to show the new active state. The window is furthermore
        activated to bring it to the front.

        :param state_name: the name of the state to set active
        """

        print(f'\nfsm: {self.svg_base_name} --> Entered: {state_name}')
        if self.svg_base_name.find('overview') != -1:
            if state_name.find('.') != -1:
                return

        print('  deactivate old state')
        try:
            self.active_state(self.svg_root)[
                0][0].attrib['fill'] = self.active_state_color
            self.svg_widget.load(etree.tostring(self.svg_root))
            time.sleep(0.1)
        except:
            pass

        print('  activate new state')
        state = etree.ETXPath(
            "//{http://www.w3.org/2000/svg}g[@id='%s']" % (state_name))

        try:
            state_color = state(self.svg_root)[0][0].attrib['fill']

            state(self.svg_root)[0][0].attrib['fill'] = active_state_color
            try:
                self.svg_widget.load(etree.tostring(self.svg_root))
            except:
                print('  load error')
            time.sleep(0.1)

            self.active_state = state
            self.active_state_color = state_color

            self.activateWindow()
        except:
            print('  state not found: %s' % (state_name))
            return

    def resizeEvent(self, event):
        """
        The resizeEvent method

        :param event: the event object
        """

        self.svg_widget.renderer().setAspectRatioMode(QtCore.Qt.KeepAspectRatio)

        aspectRatio = self.svg_widget.sizeHint().width() / \
            self.svg_widget.sizeHint().height()

        w = event.size().width()
        if w < self.svg_widget.sizeHint().width():
            w = self.svg_widget.sizeHint().width()

        if w > self.screen.size().width():
            w = self.screen.size().width()

        h = int(w / aspectRatio)

        if h > self.screen.size().height() - top_bottom_margin:
            h = self.screen.size().height() - top_bottom_margin
            w = int(h * aspectRatio)

        self.resize(w, h)

    def closeEvent(self, event):
        """
        The closeEvent method

        :param event: the event object
        """

        print('closeEvent')

        self.action_exit(event)

    def action_exit(self, event):
        """
        The action_exit method

        :param event: the event object
        """

        print('action_exit')
        QtWidgets.qApp.quit()
        print('action_exit done')
        event.accept()
