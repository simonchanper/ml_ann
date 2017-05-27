# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
import os, sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QRubberBand, QGraphicsScene, QFrame, QMainWindow, QFileDialog, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSlot

from Ui_anntools import Ui_MainWindow
from xml_process import xml_generator, xml_parsing
from exif_info import get_info_from_image
from comm_xml import insert_object, remove_all_object, object_isCheck, read_xml_object, conv_prop
from PIL import Image

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
        screenSize = QRect()
        desktop = QDesktopWidget()
        screenSize  = desktop.availableGeometry(self);
        self.setFixedSize(screenSize.width(), screenSize.height());
        
        self.prevGraphicsView.setFrameShape(QFrame.NoFrame)
        self.currGraphicsView.setFrameShape(QFrame.NoFrame)
        
        self.prevImgPath = ''
        self.currImgPath = ''
        self.prevXMLPath = ''
        self.currXMLPath = ''
        
        self.prevScene = QGraphicsScene()
        self.prevGraphicsView.setScene(self.prevScene)
        self.currScene = QGraphicsScene()
        self.currGraphicsView.setScene(self.currScene)
        
        self.drawing_init(self.prevGraphicsView, self.prevScene)
        self.drawing_init(self.currGraphicsView, self.currScene)
        
        self.num_of_index = ' '
        self.curr_image_list = []
        self.prev_xml_list = []
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        
        self.prevGraphicsView.mousePressEvent = self.prev_mouse_press
        self.prevGraphicsView.mouseMoveEvent = self.prev_mouse_move
        self.prevGraphicsView.mouseReleaseEvent = self.prev_mouse_release
        self.currGraphicsView.mousePressEvent = self.curr_mouse_press
        self.currGraphicsView.mouseMoveEvent = self.curr_mouse_move
        self.currGraphicsView.mouseReleaseEvent = self.curr_mouse_release
        
    def scene2image(self, pixmap, image_path):
        img = Image.open(image_path)
        img_size = img.size
        print ('image size: ', img_size[0], img_size[1])
        view_size = pixmap.size()
        print ('drawing paint size: ', view_size.width(), view_size.height())
        print (img_size[0]/view_size.width(), img_size[1]/view_size.height())
        return img_size[0]/view_size.width(), img_size[1]/view_size.height()
        
    def image2scene(self, pixmap, image_path):
        if image_path != '':
            img = Image.open(image_path)
            img_size = img.size
            print ('image size: ', img_size[0], img_size[1])
            view_size = pixmap.size()
            print ('drawing paint size: ', view_size.width(), view_size.height())
            print (view_size.width()/img_size[0], view_size.height()/img_size[1])
            return view_size.width()/img_size[0], view_size.height()/img_size[1]
        else:
            print ('load image first')
    
    def drawing_init(self, gview, gscene):
        pixmap = QPixmap(gview.viewport().size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.drawRect(0, 0, 10, 10)
        painter.end()

        gscene.addPixmap(pixmap)
        gview.update()
        gscene.clear()
    
    def draw_init_gview(self, xml_path, gview, gscene, color, image_path):
        pixmap = QPixmap(gview.viewport().size())
        pos_list = read_xml_object(xml_path)
        x_p, y_p = self.image2scene(pixmap, image_path)
        print ('m->i', pos_list)
        if object_isCheck(xml_path) is True:
            for pos_item in pos_list:
                print (pos_item)
                pixmap = QPixmap(gview.viewport().size())
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setPen(color)
                xmin, ymin, xmax, ymax = pos_item.split(',')
                print (xmin, ymin, xmax, ymax)
                painter.drawRect(float(xmin)*x_p, float(ymin)*y_p, float(xmax)*x_p, float(ymax)*y_p)
                painter.end()
            
                gscene.addPixmap(pixmap)
                gview.update()
    
    def clean_bbox(self, gscene, xml_path):
        gscene.clear()
        remove_all_object(xml_path)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Z:
            self.clean_bbox(self.prevScene, self.prevXMLPath)
        elif event.key() == Qt.Key_C:
            self.clean_bbox(self.currScene, self.currXMLPath)
    
    def prev_mouse_press(self, event):
        if event.button() == Qt.LeftButton: 
            self.origin = QPoint(self.prevGraphicsView.pos()+event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

            self.startx=event.x()
            self.starty=event.y()
            
        elif event.button() == Qt.RightButton:
            self.rubberBand.hide()
    
    def curr_mouse_press(self, event):
        if event.button() == Qt.LeftButton: 
            self.origin = QPoint(self.currGraphicsView.pos()+event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            
            self.startx=event.x()
            self.starty=event.y()
            
        elif event.button() == Qt.RightButton:
            self.rubberBand.hide()
            
    def prev_mouse_move(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, self.prevGraphicsView.pos()+event.pos()).normalized())

    def curr_mouse_move(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, self.currGraphicsView.pos()+event.pos()).normalized())
        
    def draw_on_gview(self, event, xmlpath, gview, gscene, color, image_path):
        mousePos = gview.mapToScene(event.pos())
        self.pixmap = QPixmap(gview.viewport().size())
        self.pixmap.fill(Qt.transparent)
        painter = QPainter(self.pixmap)
        painter.setPen(color)
        painter.drawRect(mousePos.x()-(self.endx-self.startx), mousePos.y()-(self.endy-self.starty), self.endx-self.startx, self.endy-self.starty)
        painter.end()
            
        gscene.addPixmap(self.pixmap)
        gview.update()
        
        pos_insert = [mousePos.x()-(self.endx-self.startx), mousePos.y()-(self.endy-self.starty), self.endx-self.startx, self.endy-self.starty]
        print ('scene -> image: ', pos_insert)
        
        if image_path != '':
            x_p,  y_p = self.scene2image(self.pixmap, image_path)
            pos_i = conv_prop(pos_insert, x_p, y_p)
            print ('image -> xml: ', pos_i)
            insert_object(xmlpath, pos_i)
            print ('position has been saved')
        else:
            gscene.clear()
            print ('load dataset first')

    def prev_mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            self.endx=event.x()
            self.endy=event.y()
            
            self.draw_on_gview(event, self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green,  self.prevImgPath)
            
        elif event.button() == Qt.RightButton:
            self.clean_bbox(self.prevScene, self.prevXMLPath)
            
    def curr_mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            self.endx=event.x()
            self.endy=event.y()
            
            self.draw_on_gview(event, self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)  
            
        elif event.button() == Qt.RightButton: 
            self.clean_bbox(self.currScene, self.currXMLPath)
        
    def image_show_gview(self, index):
        
        self.prevImgPath = os.path.join(self.file_dir, 'prev', self.prev_image_list[index])
        self.currImgPath = os.path.join(self.file_dir, 'curr', self.curr_image_list[index])
        self.prevGraphicsView.setStyleSheet("border-image: url(%s);" % self.prevImgPath)
        self.currGraphicsView.setStyleSheet("border-image: url(%s);" % self.currImgPath)
        
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
            self.prevScene.clear()
            self.currScene.clear()
            
            self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
            self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
            
            self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
            self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
            
            self.draw_init_gview(self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
            self.draw_init_gview(self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)
            
        else:
            print ('Pleae enter a correct file name')

    @pyqtSlot()
    def on_rootPathSelButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.prevScene.clear()
        self.currScene.clear()
        
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
            
            if not (os.path.exists(os.path.join(self.file_dir, 'ob_prev')) and os.path.exists(os.path.join(self.file_dir, 'ob_curr'))):
                self.init_xml_file()
            else: 
                pass
            
            self.prev_xml_list = os.listdir(os.path.join(self.file_dir, 'ob_prev'))
            self.num_of_index = 0
            self.image_show_gview(self.num_of_index)
            
            self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
            self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
            
            self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
            self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
            
            self.draw_init_gview(self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
            self.draw_init_gview(self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)
    
    def info_from_xml(self, xml_path, text_edit):
        text_edit.clear()
        xml_info = xml_parsing(xml_path)
        for key, values in xml_info.items():
            text_edit.appendPlainText('%s: %s' % (key, values))
        
        text_edit.setFixedHeight(text_edit.document().size().height()+110)
    
    @pyqtSlot()
    def on_prevPushBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        
        self.prevScene.clear()
        self.currScene.clear()
        if self.num_of_index is ' ':
            print ('please open path')
        elif self.num_of_index is 0:
            self.num_of_index = len(self.curr_image_list)-1
#            self.image_show_gview(self.num_of_index)
#            self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
#            self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
#            self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
#            self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
        
        else:
            self.num_of_index -= 1
            
        self.image_show_gview(self.num_of_index)
        self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
        self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
        self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
        self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
        
        self.draw_init_gview(self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
        self.draw_init_gview(self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)
    
    @pyqtSlot()
    def on_nextPushBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        self.prevScene.clear()
        self.currScene.clear()
        if self.num_of_index is ' ':
            print ('please open path')
        elif self.num_of_index is len(self.curr_image_list)-1:
            self.num_of_index = 0
#            self.image_show_gview(self.num_of_index)
#            self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
#            self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
#            self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
#            self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
        else:
            self.num_of_index += 1
        
        self.image_show_gview(self.num_of_index)
        self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
        self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
        self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
        self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
        
        self.draw_init_gview(self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
        self.draw_init_gview(self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)

    def init_xml_file(self):
        os.makedirs(os.path.join(self.file_dir, 'ob_prev'))
        os.makedirs(os.path.join(self.file_dir, 'ob_curr'))

        for f in self.prev_image_list:
            prev_info_from_exif = get_info_from_image(os.path.join(self.file_dir, 'prev', f))
            curr_info_from_exif = get_info_from_image(os.path.join(self.file_dir, 'curr', f))
            xml_generator(f, 'prev', prev_info_from_exif, self.file_dir)
            xml_generator(f, 'curr', curr_info_from_exif, self.file_dir)
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.showMaximized()
    sys.exit(app.exec_())
    

