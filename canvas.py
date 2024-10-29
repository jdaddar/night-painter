from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from collections import deque

class Canvas(QtWidgets.QLabel):
    def __init__(self, w: int, h: int): #TODO: make init more functional
        super().__init__()

        # Settings
        self.canvas_color = 'black' # TODO: load from setting
        max_undo = 500 # rec values: low:20, mid:50, high:200, ultra:500
                       # max mb ram:    100,    215       770

        # Create and set pixmap for canvas, using default color
        self.initial_pixmap = QtGui.QPixmap(w, h)
        self.initial_pixmap.fill(QtGui.QColor(self.canvas_color))
        self.setPixmap(self.initial_pixmap)

        # Initializing useful variables 
        self.prev_x, self.prev_y = None, None
        self.pixmap_stack = deque([], max_undo)

        # Brush settings
        self.brush_size = 4
        self.brush_primary_color = QtGui.QColor('white') # TODO: load from setting
        self.brush_secondary_color = QtGui.QColor('black') # TODO: load from setting

    def set_brush_size(self, size):
        """ Set brush size """
        self.brush_size = size;
    
    def set_brush_primary_color(self, color):
        """ Set brush primary color """
        self.brush_primary_color = QtGui.QColor(color)

    def set_brush_secondary_color(self, color):
        """ Set brush secondary color """
        self.brush_secondary_color = QtGui.QColor(color)

    def draw_brush_point(self, x, y, color):
        """ 
        Paint point with brush at pos(x, y) using brush of specified color 
        """
        current_pixmap = self.pixmap()
        painter = QtGui.QPainter(current_pixmap)
        # TODO: test if brush is more sensible
        pen = painter.pen()
        pen.setWidth(self.brush_size)
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawPoint(x, y)
        painter.end()
        self.setPixmap(current_pixmap)

    def draw_brush_line(self, start_x, start_y, x, y, color):
        """ 
        Paint line with brush from pos(start_x, start_y) to pos(x, y) 
        of specified color
        """
        current_pixmap = self.pixmap()
        painter = QtGui.QPainter(current_pixmap)
        pen = painter.pen()
        pen.setWidth(self.brush_size)
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawLine(start_x, start_y, x, y)
        painter.end()
        self.setPixmap(current_pixmap)

    def saveCanvas(self, pixmap):
        """ Add pixmap to 'undo' stack """
        self.pixmap_stack.append(pixmap)

    def mousePressEvent(self, e):
        # Set mouse position start for movement tracking
        self.prev_x = e.position().toPoint().x()
        self.prev_y = e.position().toPoint().y()

        # Paint point of primary/secondary color based on left/right click
        if e.buttons() == Qt.LeftButton:
            self.saveCanvas(self.pixmap())
            self.draw_brush_point(e.position().toPoint().x(), 
                                  e.position().toPoint().y(), 
                                  self.brush_primary_color)
        elif e.buttons() == Qt.RightButton:
            self.saveCanvas(self.pixmap())
            self.draw_brush_point(e.position().toPoint().x(), 
                                  e.position().toPoint().y(), 
                                  self.brush_secondary_color)

    def mouseMoveEvent(self, e):
        if self.prev_x is None: # First event
            self.prev_x = e.position().toPoint().x()
            self.prev_y = e.position().toPoint().y()
            return # Ignore first time, already drawing point

        # Paint line of primary/secondary color based on left/right click 
        # from previous mouse pos to current pos 
        if e.buttons() == Qt.LeftButton:
            self.draw_brush_line(self.prev_x, 
                                 self.prev_y, 
                                 e.position().toPoint().x(), 
                                 e.position().toPoint().y(), 
                                 self.brush_primary_color)
        elif e.buttons() == Qt.RightButton:
            self.draw_brush_line(self.prev_x, 
                                 self.prev_y, 
                                 e.position().toPoint().x(), 
                                 e.position().toPoint().y(), 
                                 self.brush_secondary_color)

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
