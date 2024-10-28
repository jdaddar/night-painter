from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt

class Canvas(QtWidgets.QLabel):
    def __init__(self, w: int, h: int):
        super().__init__()

        # Create and set pixmap for canvas, default black
        canvas_pixmap = QtGui.QPixmap(w, h)
        canvas_pixmap.fill(QtGui.QColor('black')) # TODO: load from setting
        self.setPixmap(canvas_pixmap)

        self.prev_x, self.prev_y = None, None
        self.brush_size = 3
        self.brush_primary_color = QtGui.QColor('white') # TODO: load from setting
        self.brush_secondary_color = QtGui.QColor('black') # TODO: load from setting

    def set_brush_size(self, size):
        self.brush_size = size;
    
    def set_brush_primary_color(self, color):
        self.brush_primary_color = QtGui.QColor(color)

    def set_brush_secondary_color(self, color):
        self.brush_secondary_color = QtGui.QColor(color)

    def draw_brush_point(self, x, y, color):
        """ Paint point with brush at pos(x, y) using brush of specified color """
        current_pixmap = self.pixmap() # TODO: save previous canvases so user can 'undo'
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
        current_pixmap = self.pixmap() # TODO: save previous canvases so user can 'undo'
        painter = QtGui.QPainter(current_pixmap)
        pen = painter.pen()
        pen.setWidth(self.brush_size)
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawLine(start_x, start_y, x, y)
        painter.end()
        self.setPixmap(current_pixmap)

    def mousePressEvent(self, e):
        # Set mouse position start for movement tracking
        self.prev_x = e.position().x()
        self.prev_y = e.position().y()

        # Paint point of primary/secondary color based on left/right click
        if e.buttons() == Qt.LeftButton:
            self.draw_brush_point(e.position().x(), e.position().y(), self.brush_primary_color)
        elif e.buttons() == Qt.RightButton:
            self.draw_brush_point(e.position().x(), e.position().y(), self.brush_secondary_color)

    def mouseMoveEvent(self, e):
        if self.prev_x is None: # First event
            self.prev_x = e.position().x()
            self.prev_y = e.position().y()
            return # Ignore first time, already drawing point

        # Paint line of primary/secondary color based on left/right click from previous mouse pos to current pos 
        if e.buttons() == Qt.LeftButton:
            self.draw_brush_line(self.prev_x, self.prev_y, e.position().x(), e.position().y(), self.brush_primary_color)
        elif e.buttons() == Qt.RightButton:
            self.draw_brush_line(self.prev_x, self.prev_y, e.position().x(), e.position().y(), self.brush_secondary_color)

        # Update mouse loc
        self.prev_x = e.position().x()
        self.prev_y = e.position().y()
            
    def mouseReleaseEvent(self, e):
        """ Reset previous position on mouse release """
        self.prev_x = None
        self.prev_y = None