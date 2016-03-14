__author__ = 'c60544'

import os
import arcpy
import sys

indir = 'C:/Users/C60544/Desktop/city_sdk/source_mxd'
outdir = 'C:/Users/C60544/Desktop/city_sdk/'
mxddir = os.path.join(outdir, 'mxd_5')
datadir = os.path.join(outdir, 'data')

# read mxds in mxd_folder
file_list = []
for root, dirs, files in os.walk(r''+indir):
    for f in files:
        file_list.append(f)

print 'file_list created'

if not os.path.isdir(outdir):
    os.mkdir(outdir)
    os.mkdir(mxddir)
    os.mkdir(datadir)
    print 'directories created'
print 'directories found'


# create mxd
for file in file_list:
    mxd = arcpy.mapping.MapDocument(r""+indir+"/"+file)
    df = arcpy.mapping.ListDataFrames(mxd, "")[0]
    lyr = arcpy.mapping.ListLayers(mxd, "", df)[0]
    lyr_list = arcpy.mapping.ListLayers(mxd, "", df)
    print lyr_list
    for l in lyr_list:
        print l
        new_mxd = mxddir+'/'+str(l)+".mxd"
        print new_mxd
        mxd.saveACopy(r""+new_mxd)
        new_mxd_r = arcpy.mapping.MapDocument(r""+new_mxd)
        new_df = arcpy.mapping.ListDataFrames(new_mxd_r, "")[0]
        new_lyr_list = arcpy.mapping.ListLayers(new_mxd_r, "", new_df)
        for nl in new_lyr_list:
            if str(nl) != str(l):
                arcpy.mapping.RemoveLayer(new_df, nl)
        new_mxd_r.save()

    assets = [mxd, df, lyr, lyr_list]
    for a in assets:
        del a

# # read new mxds in mxd_folder
# layer_file_list = []
# for r, d, files in os.walk(r''+mxddir):
#     for f in files:
#         layer_file_list.append(f)
#
# print 'file_list created'
#
# for file in layer_file_list:
#     mxd2 = arcpy.mapping.MapDocument(r""+mxddir+"/"+file)
#     df2 = arcpy.mapping.ListDataFrames(mxd2, "")[0]
#     lyr2 = arcpy.mapping.ListLayers(mxd2, "", df2)[0]
#     # lyr_list2 = arcpy.mapping.ListLayers(mxd, "", df2)
#     # TODO Handle tables and layers
#     # export layer
#     arcpy.FeatureClassToFeatureClass_conversion(lyr2, datadir, lyr2.name)
#     addlyr = arcpy.mapping.Layer(os.path.join(datadir, str(lyr2.name)+".shp"))
#     arcpy.mapping.AddLayer(df2, addlyr, "TOP")
#     lyr_list2 = arcpy.mapping.ListLayers(mxd2, "", df2)
#     arcpy.ApplySymbologyFromLayer_management(lyr_list2[0], lyr_list2[1])
#     arcpy.mapping.RemoveLayer(df2, lyr_list2[1])
#     mxd2.save()
#     print lyr_list2[0].name + ' is done.'
