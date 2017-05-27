# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""

import xml.etree.ElementTree as ET
from xml.etree import ElementTree as etree
from xml.dom import minidom
import untangle

def xml_generator(input_filename, input_foldername, exif_list, root_path):
    root = ET.Element('annotation')
    
    source = ET.SubElement(root, 'source')
    image_date = ET.SubElement(source, 'date')
    image_date.text = str(exif_list[0])
    folder_name = ET.SubElement(source, 'folder')
    folder_name.text = input_foldername
    file_name = ET.SubElement(source, 'filename')
    file_name.text = input_filename

    gpsinfo = ET.SubElement(root, 'gpsinfo')
    gps_altitude = ET.SubElement(gpsinfo, 'GPSAltitude')
    gps_altitude.text = str(exif_list[1])
    gps_latitude = ET.SubElement(gpsinfo, 'GPSLatitude')
    gps_latitude.text = str(exif_list[2])
    gps_latitude_ref = ET.SubElement(gpsinfo, 'GPSLatitudeRef')
    gps_latitude_ref.text = str(exif_list[3])
    gps_longitude = ET.SubElement(gpsinfo, 'GPSLongitude')
    gps_longitude.text = str(exif_list[4])
    gps_longitude_ref = ET.SubElement(gpsinfo, 'GPSLongitudeRef')
    gps_longitude_ref.text = str(exif_list[5])
    
    '''
    There should be position annotation inside 'object' tag
    '''
    #ann_obj = ET.SubElement(root, 'object')
    
    xml_string = etree.tostring(root)
    tree = minidom.parseString(xml_string)
    xml_string = tree.toxml()
    
    save_path = '%s/ob_%s/%s.xml' % (root_path, input_foldername, input_filename[:-4])
    
    f=open(save_path,'wb')
    f.write(tree.toprettyxml(encoding='utf-8'))
    f.close()

def xml_parsing(input_xml_file):
    obj = untangle.parse(input_xml_file)
    
    date_time = obj.annotation.source.date.cdata
    GPSAltitude = obj.annotation.gpsinfo.GPSAltitude.cdata
    GPSLatitude = obj.annotation.gpsinfo.GPSLatitude.cdata
    GPSLatitudeRef = obj.annotation.gpsinfo.GPSLatitudeRef.cdata
    GPSLongitude = obj.annotation.gpsinfo.GPSLongitude.cdata
    GPSLongitudeRef = obj.annotation.gpsinfo.GPSLongitudeRef.cdata
    
    xml_info_keys = ['Date', 'GPSAltitude', 'GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']
    xml_info_value = [date_time, GPSAltitude, GPSLatitude, GPSLatitudeRef, GPSLongitude, GPSLongitudeRef]
    xml_info_dict = dict(zip(xml_info_keys, xml_info_value))
    return xml_info_dict

#im = '/Users/xiang/ml_ann/ann_tools_eric/dataset/ob_curr/00001.xml'
#xml_parsing(im)
