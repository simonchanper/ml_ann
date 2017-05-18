# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QApplication, QRubberBand
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QPalette, QCursor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
import os
from Ui_anntools import Ui_MainWindow

image_path = '/Users/xiang/ml_ann/ann_tools_eric/dataset/curr/00001.JPG'
scaled_ratio = 600

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.num_of_index = ' '
        self.curr_image_list = []
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        self.currGraphicsView.mousePressEvent = self.mouse_press
        self.currGraphicsView.mouseMoveEvent = self.mouse_move
        self.currGraphicsView.mouseReleaseEvent = self.mouse_release
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            
            self.startx=event.x()
            self.starty=event.y()
            #print (self.startx,self.starty)
        elif event.button() == Qt.RightButton:
            self.rubberBand.hide()
            
    def mouse_move(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.show()
            self.endx=event.x()
            self.endy=event.y()
            
            
#            painter = QPainter(self)
#            #painter.begin(self.currGraphicsView)
#            painter.setPen(Qt.red)
#            painter.drawRect(0,0,80, 80)
#            #painter.end()

    def image_show_gview(self, index):
        self.prevGraphicsView.setStyleSheet("border-image: url(%s);" % os.path.join(self.file_dir, 'prev', self.prev_image_list[index]))
        self.currGraphicsView.setStyleSheet("border-image: url(%s);" % os.path.join(self.file_dir, 'curr', self.curr_image_list[index]))
        self.fileNameLineEdit.setText(self.curr_image_list[index])
    
    @pyqtSlot()
    def on_fileNameLineEdit_returnPressed(self):
        """
        Slot documentation goes here.
        """
        fileName = self.fileNameLineEdit.text()
        if fileName is "":
            print ('Please enter an image name!')
        elif fileName.strip() in self.curr_image_list:
            self.num_of_index = self.curr_image_list.index(fileName.strip())
            self.image_show_gview(self.num_of_index)
        else:
            print ('Pleae enter a correct file name!')

    
    @pyqtSlot()
    def on_rootPathSelButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #filename = QFileDialog.getOpenFileName(self, 'Open file','/home')
        self.file_dir = QFileDialog.getExistingDirectory(self, '/home')
        if self.file_dir is '/home':
            QMessageBox.warning(self, "Cannot open folder", "Please select correct root folder.", QMessageBox.Ok)
        elif not os.path.exists(os.path.join(self.file_dir, 'curr')):
            QMessageBox.warning(self, "Cannot open folder", "The selected folder does not contain 'curr' folder.", QMessageBox.Ok)
        elif not os.path.exists(os.path.join(self.file_dir, 'prev')):
            QMessageBox.warning(self, "Cannot open folder", "The selected folder does not contain 'prev' folder.", QMessageBox.Ok)
        else:
            self.rootPathLineEdit.setText('Home Folder: %s' % self.file_dir)
            
            self.prev_image_list = os.listdir(os.path.join(self.file_dir, 'prev'))
            self.curr_image_list = os.listdir(os.path.join(self.file_dir, 'curr'))
            
            assert len(self.prev_image_list) != 0
            assert len(self.prev_image_list) == len(self.curr_image_list)
            assert self.prev_image_list == self.curr_image_list
            
            self.num_of_index = 0
            self.image_show_gview(self.num_of_index)
            
    @pyqtSlot()
    def on_prevPushBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        if self.num_of_index is ' ':
            print ('please open path')
        elif self.num_of_index is 0:
            self.num_of_index = len(self.curr_image_list)-1
            self.image_show_gview(self.num_of_index)
        else:
            self.num_of_index -= 1
            self.image_show_gview(self.num_of_index)
    
    @pyqtSlot()
    def on_nextPushBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        if self.num_of_index is ' ':
            print ('please open path')
        elif self.num_of_index is len(self.curr_image_list)-1:
            self.num_of_index = 0
            self.image_show_gview(self.num_of_index)
        else:
            self.num_of_index += 1
            self.image_show_gview(self.num_of_index)

            
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
    

