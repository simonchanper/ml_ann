# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
import os, sys, math
from time import sleep
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QRubberBand, QGraphicsScene, QFrame, QMainWindow, QFileDialog, QMessageBox, QDesktopWidget, QProgressBar
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QPalette
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSlot, QDir, QStringListModel, QModelIndex, QThread

from Ui_anntools import Ui_MainWindow
from xml_process import xml_generator, xml_parsing
from exif_info import get_info_from_image
from comm_xml import insert_object, remove_all_object, object_isCheck, read_xml_object, conv_prop, rect_size_isChecked
from PIL import Image
from PyQt5.QtWidgets import QWidget

class Overlay(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setAttribute(Qt.WA_PaintOnScreen)
        #self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Qt.NoPen))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 200)))

        for i in range(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(QBrush(QColor(120, 120, 120, 220)))

            else:
                painter.setBrush(QBrush(QColor(180, 180, 180, 220)))
            painter.drawEllipse(self.width() / 2 + 30 * math.cos(2 * math.pi * i / 6.0) -
                                    10, 
                                self.height() / 2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10, 
                                20, 20)

        #painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()
        if self.counter == 25:
            self.killTimer(self.timer)
            self.hide()
        
class MainWindow(QMainWindow, Ui_MainWindow):
    
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
        
        aps_ratio = 83/100 # set prefer ratio if you want 
        
        height = screenSize.height()*aps_ratio
        print ('height',  height, screenSize.width(), screenSize.height())
        self.setFixedSize(screenSize.width(), height);
        
        self.prevGraphicsView.setFrameShape(QFrame.NoFrame)
        self.currGraphicsView.setFrameShape(QFrame.NoFrame)
        
        self.prevImgPath = ''
        self.currImgPath = ''
        self.prevXMLPath = ''
        self.currXMLPath = ''
        self.prev_image_list = None
        
        self.prevScene = QGraphicsScene()
        self.prevGraphicsView.setScene(self.prevScene)
        self.currScene = QGraphicsScene()
        self.currGraphicsView.setScene(self.currScene)
        
        self.num_of_index = ' '
        self.curr_image_list = []
        self.prev_xml_list = []
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        
        self.prev_count_mouse_click = None
        self.curr_count_mouse_click = None
        
        self.prevGraphicsView.mousePressEvent = self.prev_mouse_press
        self.prevGraphicsView.mouseMoveEvent = self.prev_mouse_move
        self.prevGraphicsView.mouseReleaseEvent = self.prev_mouse_release
        self.currGraphicsView.mousePressEvent = self.curr_mouse_press
        self.currGraphicsView.mouseMoveEvent = self.curr_mouse_move
        self.currGraphicsView.mouseReleaseEvent = self.curr_mouse_release
        
        self.overlay = Overlay()
                
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
    
    def draw_init_gview(self, xml_path, gview, gscene, color, image_path):
        pixmap = QPixmap(gview.viewport().size())
        pos_list = read_xml_object(xml_path)
        x_p, y_p = self.image2scene(pixmap, image_path)
        print ('xml -> image', pos_list)
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
            
    def draw_init_scene(self, event, xml_path, gview, gscene, color, img_path):
        
        if object_isCheck(xml_path) is False:
            pixmap = QPixmap(gview.viewport().size())
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(Qt.yellow)
            painter.drawRect(0, 0, 0, 0)
            painter.end()
            gscene.addPixmap(pixmap)
        else:
            gscene.clear()
            self.draw_init_gview(xml_path, gview, gscene, color, img_path)
        
        print ('initialize the scene successfully')
        
    def draw_on_gview(self, event, xmlpath, gview, gscene, color, image_path):
        mousePos = gview.mapToScene(event.pos())
        self.pixmap = QPixmap(self.prevGraphicsView.viewport().size())
        self.pixmap.fill(Qt.transparent)
        painter = QPainter(self.pixmap)
        painter.setPen(color)
        painter.drawRect(mousePos.x()-(self.endx-self.startx), mousePos.y()-(self.endy-self.starty), self.endx-self.startx, self.endy-self.starty)
        painter.end()
            
        gscene.addPixmap(self.pixmap)
        gscene.update()
        gview.update()
        
        pos_insert = [mousePos.x()-(self.endx-self.startx), mousePos.y()-(self.endy-self.starty), self.endx-self.startx, self.endy-self.starty]
        print ('scene -> image: ', pos_insert)
        
        if rect_size_isChecked(self.endx-self.startx, self.endy-self.starty) is True:
            if image_path != '':
                x_p,  y_p = self.scene2image(self.pixmap, image_path)
                pos_i = conv_prop(pos_insert, x_p, y_p)
                print ('image -> xml: ', pos_i)
                insert_object(xmlpath, pos_i)
                print ('position has been saved')
            else:
                gscene.clear()
                print ('load dataset first')
        else:
            print ('Recentangle invaild')

    def prev_mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            self.endx=event.x()
            self.endy=event.y()
            
            if self.prev_count_mouse_click is False:
                self.prev_count_mouse_click = True
                self.draw_init_scene(event, self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
            elif self.prev_count_mouse_click is True:
                self.draw_on_gview(event, self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green,  self.prevImgPath)
            
        elif event.button() == Qt.RightButton:
            self.clean_bbox(self.prevScene, self.prevXMLPath)
            
        self.status_of_ob_isChecked(self.prev_image_list)
        qlist_for_display = self.read_from_dat('store.dat')
        prev_image_qlist = QStringListModel(qlist_for_display)
        self.fileListView.setModel(prev_image_qlist)
            
    def curr_mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()
            self.endx=event.x()
            self.endy=event.y()
            
            if self.curr_count_mouse_click is False:
                self.curr_count_mouse_click = True
                self.draw_init_scene(event, self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)
            elif self.curr_count_mouse_click is True:
                self.draw_on_gview(event, self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)  
            
        elif event.button() == Qt.RightButton: 
            self.clean_bbox(self.currScene, self.currXMLPath)
        
        self.status_of_ob_isChecked(self.prev_image_list)
        qlist_for_display = self.read_from_dat('store.dat')
        prev_image_qlist = QStringListModel(qlist_for_display)
        self.fileListView.setModel(prev_image_qlist)
        
    def image_show_gview(self, index):
        self.overlay.show()
        prevImgPath = os.path.join(self.file_dir, 'prev', self.prev_image_list[index])
        self.prevImgPath = QDir.toNativeSeparators(prevImgPath)
        currImgPath = os.path.join(self.file_dir, 'curr', self.curr_image_list[index])
        self.currImgPath = QDir.toNativeSeparators(currImgPath)
        
        self.prevGraphicsView.setStyleSheet("border-image: url(%s);" % self.prevImgPath)
        self.currGraphicsView.setStyleSheet("border-image: url(%s);" % self.currImgPath)
        
        self.fileNameLineEdit.setText(self.curr_image_list[index])
        self.timer_flag = 1
        
    def status_of_ob_isChecked(self, list_of_image):
        temp_output = open('store.dat', 'w')
        if list_of_image is not None:
            for each in list_of_image:
                file_each = each[:-3] + 'xml'
                prev_xml_check_path = os.path.join(self.file_dir, 'ob_prev', file_each )
                curr_xml_check_path = os.path.join(self.file_dir, 'ob_curr', file_each)
                if os.path.exists(prev_xml_check_path) is True:
                    if object_isCheck(prev_xml_check_path) is True and object_isCheck(curr_xml_check_path) is True:
                        w = each + ' ✓' + ' ✓' + '\r\n'
                    elif object_isCheck(prev_xml_check_path) is False and object_isCheck(curr_xml_check_path) is True:
                        w = each + ' -' + ' ✓' + '\r\n'
                    elif object_isCheck(prev_xml_check_path) is True and object_isCheck(curr_xml_check_path) is False:
                        w = each + ' ✓' + ' -' + '\r\n'
                    elif object_isCheck(prev_xml_check_path) is False and object_isCheck(curr_xml_check_path) is False:
                        w = each + ' -' + ' -' + '\r\n'
                    temp_output.write(w)
                else:
                    pass
        else:
            print ('load image first')
        temp_output.close()
        
    def read_from_dat(self, dat_file_name):
        dat_input = open(dat_file_name, 'r')
        list_of_file_name = []
        for each in dat_input:
            list_of_file_name.append(each.strip())
        dat_input.close()
        return list_of_file_name

    @pyqtSlot()
    def on_fileNameLineEdit_returnPressed(self):
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
            
            self.prev_xml_list = self.map_2_imglist(self.prev_image_list)
            
            self.num_of_index = 0
            self.image_show_gview(self.num_of_index)
            
            self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
            self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
            
            self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
            self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
            
            self.draw_init_gview(self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
            self.draw_init_gview(self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)
            
            self.prev_count_mouse_click = False
            self.curr_count_mouse_click = False
            
            self.status_of_ob_isChecked(self.prev_image_list)
            qlist_for_display = self.read_from_dat('store.dat')
            prev_image_qlist = QStringListModel(qlist_for_display)
            self.fileListView.setModel(prev_image_qlist)
            
    def map_2_imglist(self, image_list):
        list_xml = []
        for img_item in self.prev_image_list:
            img_name = img_item.split('.')
            xml_name = img_name[0] + '.xml'
            list_xml.append(xml_name)
        return list_xml
    
    def info_from_xml(self, xml_path, text_edit):
        text_edit.clear()
        xml_info = xml_parsing(xml_path)
        for key, values in xml_info.items():
            text_edit.appendPlainText('%s: %s' % (key, values))
        
        text_edit.setFixedHeight(text_edit.document().size().height()+110)
    
    @pyqtSlot()
    def on_prevPushBtn_clicked(self):
        self.prevScene.clear()
        self.currScene.clear()
        if self.num_of_index is ' ':
            print ('please open path')
        elif self.num_of_index is 0:
            self.num_of_index = len(self.curr_image_list)-1
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
        self.prevScene.clear()
        self.currScene.clear()
        if self.num_of_index is ' ':
            print ('please open path')
        elif self.num_of_index is len(self.curr_image_list)-1:
            self.num_of_index = 0
        else:
            self.num_of_index += 1
        
        self.image_show_gview(self.num_of_index)
        self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
        self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
        self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
        self.info_from_xml(self.currXMLPath, self.currPlainTextEdit)
        
        self.draw_init_gview(self.prevXMLPath, self.prevGraphicsView, self.prevScene, Qt.green, self.prevImgPath)
        self.draw_init_gview(self.currXMLPath, self.currGraphicsView, self.currScene, Qt.red, self.currImgPath)

    @pyqtSlot(QModelIndex)
    def on_fileListView_clicked(self, index):
        sel_file_name = index.data()
        self.num_of_index = self.curr_image_list.index(sel_file_name[:-4].strip())
        self.image_show_gview(self.num_of_index)
        self.prevScene.clear()
        self.currScene.clear()
            
        self.prevXMLPath = os.path.join(self.file_dir, 'ob_prev', self.prev_xml_list[self.num_of_index])
        self.currXMLPath = os.path.join(self.file_dir, 'ob_curr', self.prev_xml_list[self.num_of_index])
        
        self.info_from_xml(self.prevXMLPath, self.prevPlainTextEdit)
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
        
    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    #ui.showMaximized()
    ui.show()
    sys.exit(app.exec_())
   
