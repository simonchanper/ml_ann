# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/xiang/ml_ann/ann_tools_eric/anntools.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

import exifread

def _get_if_exist(data, key):
    if key in data:
        return data[key]
        
    return None

def _convert_to_degress(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)
    
def get_exif_info(exif_data):
    lat = None
    lon = None
    
    image_date = _get_if_exist(exif_data, 'Image DateTime')
    gps_altitude = _get_if_exist(exif_data, 'GPS GPSAltitude')
    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    return image_date, gps_altitude, lat, gps_latitude_ref, lon, gps_longitude_ref

def get_info_from_image(image_path):
    f = open(image_path, 'rb')
    info_list = []
    tags = exifread.process_file(f)
    info_list = get_exif_info(tags)
    return info_list
