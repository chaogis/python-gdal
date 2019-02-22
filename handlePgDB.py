#-*-coding=utf-8-*-
'''
Created on 2019年02月20日

@author: chao_qin
@description: 操作postgis数据库中的数据
'''
from osgeo import ogr
from osgeo import osr

import ospybook as pb

ds = ogr.Open('PG:user=postgres password=postgis dbname=postgis_geo_basic host=118.24.36.140 port=5432')

count = ds.GetLayerCount()

# 列出所有图层
for i in range(count):
    layer = ds.GetLayer(i)
    print('{}-{}'.format(i, layer.GetName()))

# 借助ospybook打印所有图层
pb.print_layers('PG:user=postgres password=postgis dbname=postgis_geo_basic host=118.24.36.140 port=5432')

# sql = 'CREATE TABLE public.geo_test_t(gid integer NOT NULL, name character varying(50), geom geometry(MultiPolygon,4326))'
# layer = ds.ExecuteSQL(sql)


srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

layer = ds.CreateLayer('geo_test_t', srs, geom_type = ogr.wkbPolygon)
print(layer.GetName())

