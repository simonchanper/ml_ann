# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""

import xml.etree.ElementTree as ET
import untangle

def remove_all_object(xml_file):
    if xml_file != '':
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for item in root.findall("object"):
            if item != None:
                root.remove(item)
                
        tree.write(xml_file,"UTF-8")
    else:
         print ('no xml file')

def remove_final_object(xml_file):
    '''
    can not work yet
    '''
    if xml_file != '':
        tree = ET.parse(xml_file)
        root = tree.getroot()
        iterator = root.getiterator("annotation")
        for item in iterator:
            oldElement = item.find("object")
            if oldElement != None:
                root.remove(oldElement)
                
        #tree = ET.ElementTree(root)
        tree.write(xml_file,"UTF-8")
    else:
         print ('no xml file')

def object_isCheck(xml_file):
    '''
    check whether there exists annotation coordinate
    '''
    if xml_file != '':
        tree = ET.parse(xml_file)
        elementName = 'object'
        root = tree.getroot()
        for item in root:
            oldElement = root.find(elementName)
            if oldElement !=None:
                return True
            else:
                return False
    else:
         print ('no xml file')

def read_xml_object(input_xml_file):
    '''
    read the object position from xml file
    '''
    if input_xml_file != '':
        obj_ann = untangle.parse(input_xml_file)
        obj_ann_dict = {}
        if object_isCheck(input_xml_file) is True:
            for obj_item in obj_ann.annotation.object:
                obj_ann_dict[obj_item['id']] = obj_item.cdata
            return obj_ann_dict.values()
        else:
            print ('No objects')
            return False
    else:
        print ('no xml file')
    
def conv_prop(scene_pos_list, x_proportion, y_proportion):
    '''
    convert the proportion
    '''
    img_pox_list = []
    if scene_pos_list != None:
        img_pox_list = [round(scene_pos_list[0]*x_proportion), round(scene_pos_list[1]*y_proportion), round(scene_pos_list[2]*x_proportion), round(scene_pos_list[3]*y_proportion)]
        return img_pox_list
    else:
        print ('list no load')
    
def insert_object(xml_file, pos_list):
    '''
    save the annotation position to xml file
    '''
    if xml_file != '':
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ob_ann_dict = read_xml_object(xml_file)
    
        if object_isCheck(xml_file) is True:
            id_num = len(ob_ann_dict) +1
        else:
            id_num = 1
    
        obj_ann = ET.SubElement(root, 'object')
        obj_ann.set('id', str(id_num))
        obj_ann.text = '%s, %s, %s, %s' % (str(pos_list[0]), str(pos_list[1]), str(pos_list[2]), str(pos_list[3]))
        tree.write(xml_file,"UTF-8")
    else:
        print ('no xml file')

