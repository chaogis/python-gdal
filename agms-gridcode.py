#-*-coding=utf-8-*-
'''
Created on 2019年01月09日

@author: chao_qin
@description: 处理大气网格化项目中网格编码
'''
from osgeo import ogr
import os

base_dir = 'F:/网格化项目/网格化项目数据/榆林网格/四级网格'

grid1_name = 'Grid1'
grid2_name = 'Grid2'
grid3_name = 'Grid3'
grid4_name = 'Grid4'




def get_layer(path, layer_name):
    # 以读写方式打开shapefile目录
    grid_ds = ogr.Open(path, 1)
    if grid_ds is None:
        sys.exit('Could not open folder.')

    return grid_ds.GetLayerByName(layer_name)


def get_codes(layer, field_name = 'code'):
    code_list = []
    for feat in layer:
        code_list.append(feat.GetField(field_name))
    layer.ResetReading()
    return set(code_list)

# 生成网格编码
def make_grid_code(level, parent_code, count):
    if count > 99:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>grid count > 99, parent code:', parent_code)
    str_count = str(count)
    if count < 10:
        str_count = '0' + str_count
    
    if level == 2:
        return str_count + '0000'
    elif level == 3:
        return parent_code[0:2] + str_count + '00'
    elif level == 4:
        return parent_code[0:4] + str_count

# 设置网格编码
def set_grid_code(layer, code_field = 'grid_code', parent_code_field = 'code', level = 2):
    #获取上级网格code
    codes = get_codes(layer)
    layer.ResetReading()
    for code in list(codes).sort():
        print('current code:', code)
        count = 1
        for feature in layer:
            parent_code = feature.GetField(parent_code_field)
            if code == parent_code:
                feature.SetField(code_field, make_grid_code(level, parent_code, count))
                layer.SetFeature(feature)
                count = count + 1
        layer.ResetReading()

# 设置网格的上级网格编码
def set_parent_code(layer, parent_layer, code_field = 'code', parent_code_field = 'grid_code'):
    count = 0
    for feat in layer:
        # 获取网格的质心
        centroid = feat.GetGeometryRef().Centroid()
        for parent_feat in parent_layer:
            if centroid.Within(parent_feat.GetGeometryRef()):
                # 将上级网格编码写入code字段
                feat.SetField(code_field, parent_feat.GetField(parent_code_field))
                layer.SetFeature(feat)
                count = count + 1
                print('count', str(count))
                break
        parent_layer.ResetReading()

if __name__ == "__main__":
    # 处理Grid3.shp的网格编码
    # grid_ds = ogr.Open(base_dir, 1)
    # if grid_ds is None:
    #     sys.exit('Could not open folder.')

    # grid3_layer = grid_ds.GetLayerByName(grid3_name)
    # set_grid_code(grid3_layer, level = 3)
    # grid_ds.SyncToDisk()

    # 处理Grid4.shp的网格编码
    grid_ds = ogr.Open(base_dir, 1)
    if grid_ds is None:
        sys.exit('Could not open folder.')

    # grid3_layer = grid_ds.GetLayerByName(grid3_name)
    grid4_layer = grid_ds.GetLayerByName(grid4_name)
    # set_parent_code(grid4_layer, grid3_layer)
    # grid_ds.SyncToDisk()

    set_grid_code(grid4_layer, level = 4)
    grid_ds.SyncToDisk()