#-*-coding=utf-8-*-
'''
Created on 2018年12月26日

@author: QinChao
@description:请求高德地图行政区划数据
'''

adcodes = {
    # '110000':'北京市',
    # '120000':'天津市',
    # '130000':'河北省',
    # '140000':'山西省',
    # '150000':'内蒙古自治区',
    # '210000':'辽宁省',
    # '220000':'吉林省',
    # '230000':'黑龙江省',
    # '310000':'上海市',
    # '320000':'江苏省',
    # '330000':'浙江省',
    # '340000':'安徽省',
    # '350000':'福建省',
    # '360000':'江西省',
    # '370000':'山东省',
    # '410000':'河南省',
    # '420000':'湖北省',
    # '430000':'湖南省',
    # '440000':'广东省',
    # '450000':'广西壮族自治区',
    # '460000':'海南省',
    # '500000':'重庆市',
    # '510000':'四川省',
    # '520000':'贵州省',
    # '530000':'云南省',
    # '540000':'西藏自治区',
    # '610000':'陕西省',
    # '620000':'甘肃省',
    # '630000':'青海省',
    # '640000':'宁夏回族自治区',
    # '650000':'新疆维吾尔自治区',
    # '710000':'台湾省',
    # '810000':'香港特别行政区',
    # '820000':'澳门特别行政区'
    # ,'900000':'外国'
    '371700': '菏泽市'
}

url = 'https://restapi.amap.com/v3/config/district?key=27115a2d2ae7305bcda011263921423c&keywords=$&subdistrict=0&extensions=all'

import urllib.request
import simplejson
import json

def request_district(keyword):
    print('key:', url.replace('$', keyword))
    return simplejson.loads(urllib.request.urlopen(url.replace('$', keyword)).read())


def struct_feature(coords, adcodes, name):
    return {
        'type': 'Feature',
        'geometry': {
            'type': coords['type'],
            'coordinates': coords['coords']
        },
        'properties':{
            'adcodes': adcodes,
            'name': name
        }
    }

def struct_coordinates(data):
    coordinates = []
    type = 'Polygon'
    districts = data['districts'][0]
    polyline_str = districts['polyline']
    district = polyline_str.split('|')
    # 由多部分构成，为多部件
    if len(district) > 1:
        type = 'MultiPolygon'
        for part in district:
            coordinate = []
            coords = part.split(';')
            for coord in coords:
                x, y = coord.split(',')
                coordinate.append([float(x), float(y)])
            if len(coordinate) > 200:
                coordinates.append([coordinate])
    else:
        coordinate = []
        coords = district[0].split(';')
        for coord in coords:
            x, y = coord.split(',')
            coordinate.append([float(x), float(y)])
        coordinates.append(coordinate)

    return {
        'type': type,
        'coords': coordinates
    }

def write_content(file_path, content, file_type = 'txt', mode = 'w'):
    '''
        文本内容写入
        file_path--- 写入文件路径
        content--- 写入内容
        file_type--- 文件格式, 默认为txt, 其他包括json
        mode--- 文件打开模式
    '''

    with open(file_path, mode) as f:
        if file_type == 'txt':
            f.writelines(content)
        elif file_type == 'json':
            json.dump(content, f)
        f.flush()
        f.close()

if __name__ == "__main__":
    province_geojson = {
        'type': 'FeatureCollection',
        'features': []
    }
    for adcode in adcodes.keys():
        print('adcode:', adcode)
        src_data = request_district(adcode)
        coordinates = struct_coordinates(src_data)
        feature = struct_feature(coordinates, adcode, adcodes[adcode])
        province_geojson['features'].append(feature)
    write_content('G:/heze.json', province_geojson, 'json')