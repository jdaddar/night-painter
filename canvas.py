from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from collections import deque

class Canvas(QtWidgets.QLabel):
    def __init__(self, w: int, h: int): #TODO: make init more functional
        super().__init__()

        # Settings
        self.canvas_bg_color = 'black' # TODO: load from setting
        max_undo = 200 # rec values: low:20, mid:50, high:200, ultra:500
                       # max mb ram:    100,    215       770

        # Create and set pixmap for canvas, using default color
        self.initial_pixmap = QtGui.QPixmap(w, h)
        self.initial_pixmap.fill(QtGui.QColor(self.canvas_bg_color))
        self.setPixmap(self.initial_pixmap)

        # Initializing useful variables 
        self.prev_x, self.prev_y = None, None
        self.pixmap_stack = deque([], max_undo)

        # Pen settings
        self.primary_color = QtGui.QColor('white') # TODO: load from setting
        self.secondary_color = QtGui.QColor(self.canvas_bg_color) # TODO: load from setting
        self.pen = QtGui.QPen()
        self.pen.setWidth(5)
        self.pen.setColor(self.primary_color)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)

    def set_pen_size(self, size):
        """ Set pen size """
        self.pen.setWidth(size)

    def get_pen_size(self):
        """ Return pen size """
        return self.pen.width()
    
    def set_primary_color(self, color):
        """ Set primary color """
        self.primary_color = QtGui.QColor(color)

    def set_secondary_color(self, color):
        """ Set pen secondary color """
        self.secondary_color = QtGui.QColor(color)

    def get_primary_color(self):
        """ Get primary color """
        return self.primary_color
    
    def get_secondary_color(self):
        """ Get secondary color """
        return self.secondary_color

    def draw_pen_point(self, x, y, color):
        """ 
        Paint point with pen at pos(x, y) using pen of specified color 
        """
        current_pixmap = self.pixmap()
        painter = QtGui.QPainter(current_pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.pen.setColor(color)
        painter.setPen(self.pen)
        painter.drawPoint(x, y)
        painter.end()
        self.setPixmap(current_pixmap)

    def draw_pen_line(self, start_x, start_y, x, y, color):
        """ 
        Paint line with pen from pos(start_x, start_y) to pos(x, y) 
        of specified color
        """
        current_pixmap = self.pixmap()
        painter = QtGui.QPainter(current_pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.pen.setColor(color)
        painter.setPen(self.pen)
        painter.drawLine(start_x, start_y, x, y)
        painter.end()
        self.setPixmap(current_pixmap)

    def mousePressEvent(self, e):
        # Set mouse position start for movement tracking
        self.prev_x = e.position().toPoint().x()
        self.prev_y = e.position().toPoint().y()

        # Paint point of primary/secondary color based on left/right click
        if e.buttons() == Qt.LeftButton:
            self.pixmap_stack.append(self.pixmap())
            self.draw_pen_point(e.position().toPoint().x(), 
                                e.position().toPoint().y(), 
                                self.primary_color)
        elif e.buttons() == Qt.RightButton:
            self.pixmap_stack.append(self.pixmap())
            self.draw_pen_point(e.position().toPoint().x(), 
                                e.position().toPoint().y(), 
                                self.secondary_color)

    def mouseMoveEvent(self, e):
        if self.prev_x is None: # First event
            self.prev_x = e.position().toPoint().x()
            self.prev_y = e.position().toPoint().y()
            return # Ignore first time, already drawing point

        # Paint line of primary/secondary color based on left/right click 
        # from previous mouse pos to current pos 
        if e.buttons() == Qt.LeftButton:
            self.draw_pen_line(self.prev_x, 
                               self.prev_y, 
                               e.position().toPoint().x(), 
                               e.position().toPoint().y(), 
                               self.primary_color)
        elif e.buttons() == Qt.RightButton:
            self.draw_pen_line(self.prev_x, 
                               self.prev_y, 
                               e.position().toPoint().x(), 
                               e.position().toPoint().y(), 
                               self.secondary_color)

        # Update mouse loc
        self.prev_x = e.position().toPoint().x()
        self.prev_y = e.position().toPoint().y()
            
    def mouseReleaseEvent(self, e):
        # Reset previous positions
        self.prev_x, self.prev_y = None, None

    def undo(self):
        """ 
        Reverts to previous pixmap, effectively undoing 
        most recent draw action 
        """
        try:
            self.setPixmap(self.pixmap_stack.pop())
        except IndexError: # IndexError can only occur if stack is empty,
            pass           # therefore pass as we have reached undo limit 

    def reset(self):
        """ 
        Reverts canvas to base state
        Clears 'undo' stack 
        """
        self.setPixmap(self.initial_pixmap)
        self.pixmap_stack.clear()

