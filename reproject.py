#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 2018年12月26日

@author: QinChao
@description:对影像进行投影
'''
 
from osgeo import gdal, osr
from osgeo import gdalconst

in_src_tif = 'G:/data/gdal_reproject/aqi_2018102000_1233_708.tif'
out_src_tif = 'G:/data/gdal_reproject/aqi_2018102000_1233_708_gdal_epgs3857.tif'
in_srs_file = 'G:/data/gdal_reproject/WGS 1984 Web Mercator (auxiliary sphere).prj'
 
#获取源数据及栅格信息
gdal.AllRegister()
src_data = gdal.Open(in_src_tif)
#获取源的坐标信息
srcSRS_wkt=src_data.GetProjection()
srcSRS=osr.SpatialReference()
srcSRS.ImportFromWkt(srcSRS_wkt)

print(srcSRS_wkt)
'''
    GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0],
    UNIT["degree",0.0174532925199433],
    AUTHORITY["EPSG","4326"]]
'''

print('srcSRS', srcSRS)
'''
    GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0],
    UNIT["degree",0.0174532925199433],
    AUTHORITY["EPSG","4326"]]
'''

#获取栅格尺寸
src_width = src_data.RasterXSize #1233
src_height = src_data.RasterYSize #708
src_count=src_data.RasterCount #1 波段数

print('width-heigth-band_count', src_width, src_height, src_count)

#获取源图像的仿射变换参数
src_trans=src_data.GetGeoTransform()
OriginLX_src=src_trans[0]
OriginTY_src=src_trans[3]
pixl_w_src=src_trans[1]
pixl_h_src=src_trans[5]

print('仿射变换参数', src_trans)

OriginRX_src=OriginLX_src + pixl_w_src * src_width
OriginBY_src=OriginTY_src + pixl_h_src * src_height

print('右下角坐标', OriginRX_src, OriginBY_src)


#创建输出图像'
driver = gdal.GetDriverByName("GTiff")
driver.Register()
# dst_data = driver.Create(out_src_tif,src_width,src_height,src_count)
dst_data = driver.Create(out_src_tif, 1092, 800, src_count, gdal.GDT_Float32)

#设置输出图像的坐标系
dstSRS=osr.SpatialReference()
# dstSRS.ImportFromEPSGA(3857)
# print('3857', dstSRS)
'''3857 
    PROJCS["WGS 84 / Pseudo-Mercator",
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]],
    PROJECTION["Mercator_1SP"],
    PARAMETER["central_meridian",0],
    PARAMETER["scale_factor",1],
    PARAMETER["false_easting",0],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["X",EAST],
    AXIS["Y",NORTH],
    EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],
    AUTHORITY["EPSG","3857"]]
'''
with open(in_srs_file, 'r') as f:
    str_srs = f.readlines()
    print('esri-epsg3857', str_srs)
    dstSRS.ImportFromESRI(str_srs)
print('esri-epsg3857', dstSRS)

#投影转换
ct = osr.CoordinateTransformation(srcSRS, dstSRS)
print('ct', ct)
#计算目标影像的左上和右下坐标,即目标影像的仿射变换参数
OriginLX_dst, OriginTY_dst, temp = ct.TransformPoint(OriginLX_src, OriginTY_src)
OriginRX_dst, OriginBY_dst, temp = ct.TransformPoint(OriginRX_src, OriginBY_src)

print('OriginLX_dst, OriginTY_dst, temp', OriginLX_dst, OriginTY_dst, temp)
print('OriginRX_dst, OriginBY_dst, temp', OriginRX_dst, OriginBY_dst, temp)
 
pixl_w_dst = (OriginRX_dst - OriginLX_dst) / 1092
pixl_h_dst = (OriginBY_dst - OriginTY_dst) / 800
# pixl_w_dst = (OriginRX_dst - OriginLX_dst) / src_width
# pixl_h_dst = (OriginBY_dst - OriginTY_dst) / src_height
dst_trans=[OriginLX_dst, pixl_w_dst, 0, OriginTY_dst, 0, pixl_h_dst]

# dst_trans = [8176078.18751393, 6289.018527, 0, 7087429.99405438, 0, -6289.018527]
print('outTrans', dst_trans)

dstSRS_wkt = dstSRS.ExportToWkt()
#设置仿射变换系数及投影
dst_data.SetGeoTransform(dst_trans)
dst_data.SetProjection(dstSRS_wkt)
#重新投影
gdal.ReprojectImage(src_data ,dst_data, srcSRS_wkt, dstSRS_wkt, gdalconst.GRA_NearestNeighbour)
# #创建四级金字塔
# gdal.SetConfigOption('HFA_USE_RRD', 'YES')
# dst_data.BuildOverviews(overviewlist=[2,4,8,16])
# #计算统计值
# for i in range(0,src_count):
# 	band=dst_data.GetRasterBand(i+1)
# 	band.SetNoDataValue(-99)
# 	print(band.GetStatistics(0,1))