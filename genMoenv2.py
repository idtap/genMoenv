# -*- coding: utf-8 -*-

import arcpy
import math
import os,sys
from datetime import datetime, timedelta
import time
import csv 

#//////////////////////////////////
# 產生 polygon shp 檔
def CreatePolygonShpFile(shpPath, shpName) :
    arcpy.management.CreateFeatureclass(
        shpPath, shpName, 
        "POLYGON", 
        r"emptyPolygon.shp", "DISABLED", "DISABLED", 
        'PROJCS["TWD_1997_TM_Taiwan",GEOGCS["GCS_TWD_1997",DATUM["D_TWD_1997",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",250000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",121.0],PARAMETER["Scale_Factor",0.9999],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-5372600 -10001100 450310428.589905;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision', '', 0, 0, 0, '')

    return True

#//////////////////////////////////
# 產生 point shp 檔
def SavePointShpFile(targCsv,targShp) :
    arcpy.management.XYTableToPoint(
        targCsv, 
        targShp, 
        "tmx", 
        "tmy", 
        None, 
        'PROJCS["TWD_1997_TM_Taiwan",GEOGCS["GCS_TWD_1997",DATUM["D_TWD_1997",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",250000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",121.0],PARAMETER["Scale_Factor",0.9999],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-5372600 -10001100 450310428.589905;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision')

    return True

#//////////////////////////////////
# 載入待分析資料
sourDataArr = []                      # 待分析資料列
def load_sourCsv( csv_name ):
    lines = []
    with open( csv_name, 'r',encoding='UTF-8') as record_read:
        reader = csv.reader(record_read)
        for i, each_arr in enumerate(reader):
            if i>0 :    # 若有首行欄名，跳過
                lines.append([each for each in each_arr])
    for line in lines:
        sourData = {
            'place_code' : line[0],      # 場所管制編號 
            'TWD97_X'    : float(line[1]),      # 座標 X
            'TWD97_Y'    : float(line[2]),      #      Y
            'dest_prob'  : float(line[3]),      # 破壞機率
            'BUFFER'     : float(line[4]),      # 影響半徑
            'harm_result': float(line[5])       # 危害結果
        }
        sourDataArr.append( sourData )

    return True

#//////////////////////////////////
# 輸出 raster 網格
def CreateRaster(layerName, calcField, rasterPath, gridSize) :
    arcpy.conversion.PolygonToRaster(
       layerName, 
       calcField, 
       rasterPath, 
       "CELL_CENTER", "NONE", gridSize, "BUILD")
    
    return True

def AziMuth(ptx, pty, pt2x, pt2y) :
    
    Distx = ptx - pt2x
    Disty = pty - pt2y
    PI    = 57.295779513
    
    aziMuth = 0.0
    if Distx == 0 and Disty > 0 :    # 1.正北
        aziMuth = 0.0
    elif Distx == 0 and Disty < 0 :  # 2.正南
        aziMuth = 0.5
    elif Distx > 0 :
        if (math.atan(Disty / Distx) * PI) > 78.75 :  # 3.北
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= 78.75 and (math.atan(Disty / Distx) * PI) > 56.25 :   # 4.北北東
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= 56.25 and (math.atan(Disty / Distx) * PI) > 33.75 :   # 5.東北
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= 33.75 and (math.atan(Disty / Distx) * PI) > 11.25 :   # 6.東北東
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= 11.25 and (math.atan(Disty / Distx) * PI) > -11.25 :  # 7.東
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -11.25 and (math.atan(Disty / Distx) * PI) > -33.75 : # 8.東南東
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -33.75 and (math.atan(Disty / Distx) * PI) > -56.25 : # 9.東南
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -56.25 and (math.atan(Disty / Distx) * PI) > -78.75 : # 10.南南東
            aziMuth = 0.25
        elif (math.atan(Disty / Distx) * PI) <= -78.75 :   # 11.南
            aziMuth = 0.5
    elif Distx < 0 :
        if (math.atan(Disty / Distx) * PI) > 78.75 :   # 12.南
            aziMuth = 0.5
        elif (math.atan(Disty / Distx) * PI) <= 78.75 and (math.atan(Disty / Distx) * PI) > 56.25 :   # 13.南南西
            aziMuth = 0.25
        elif (math.atan(Disty / Distx) * PI) <= 56.25 and (math.atan(Disty / Distx) * PI) > 33.75 :   # 14.西南
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= 33.75 and (math.atan(Disty / Distx) * PI) > 11.25 :   # 15.西南西
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= 11.25 and (math.atan(Disty / Distx) * PI) > -11.25 :  # 16.西
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -11.25 and (math.atan(Disty / Distx) * PI) > -33.75 : # 17.西北西
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -33.75 and (math.atan(Disty / Distx) * PI) > -56.25 : # 18.西北
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -56.25 and (math.atan(Disty / Distx) * PI) > -78.75 : # 19.北北西
            aziMuth = 0.0
        elif (math.atan(Disty / Distx) * PI) <= -78.75 :    # 20.北
            aziMuth = 0.0

    return aziMuth

if __name__ == '__main__':

    # 取下參數
    sourCsv = arcpy.GetParameterAsText(0)
    targShp = arcpy.GetParameterAsText(1)
    left = arcpy.GetParameter(2)
    right = arcpy.GetParameter(3)
    top = arcpy.GetParameter(4)
    bottom = arcpy.GetParameter(5)
    windType = arcpy.GetParameter(6)
    gridSize = arcpy.GetParameter(7)

    time_f = datetime.now()
    arcpy.AddMessage("開始時間:{0}".format( time_f.strftime('%Y/%m/%d %H:%M:%S') ) )

    # 取下 targShp 路徑
    targPath = os.path.dirname(targShp)
    shpName = os.path.basename(targShp)
    layerName = os.path.splitext(shpName)[0]

    # Create 輸出 Polygon Shp 檔
    CreatePolygonShpFile(targPath, shpName)

    # 讀取 sourCsv  
    load_sourCsv( sourCsv )

    # XYZ csv Table
    tempCsv = targPath + "\\"+layerName+".csv"
    if os.path.exists(tempCsv):
        os.remove(tempCsv)

    # 開始對分析範圍每50公尺網格製作危害分析 point 點
    with open(tempCsv, 'w',encoding='UTF-8') as f:
        line = "aa,tmx,tmy,tmz\n"
        f.write(line)
        with arcpy.da.InsertCursor(targShp, ['SHAPE@','aa','tmx','tmy']) as cursor:
            for y in range(int(bottom),int(top),gridSize):
                yy = float(y)
                for x in range(int(left),int(right),gridSize):
                    o = 0.0
                    xx = float(x)
                    for row in sourDataArr:
                        pt2_x = row['TWD97_X']
                        pt2_y = row['TWD97_Y']
                        r = row['BUFFER']        # BUFFER
                        tDis = math.sqrt((pt2_x-xx)*(pt2_x-xx)+(pt2_y-yy)*(pt2_y-yy))
                        # 無風向計算以半徑 tDis 小於 BUFFER r 來計算該工廠 o 值
                        if tDis<r :
                            if windType==0 :    # 無風向
                                o = o + (row['harm_result'] / 16)
                            if windType==1 :    # 北風向
                                a = AziMuth(xx, yy, pt2_x, pt2_y)    # 加入風向係數
                                o = o + a*row['harm_result']

                    # 此位置 o 計算完畢，寫入 Temp
                    # 0 不產製時改成 >0
                    if o>=0 :
                        listOfPoints = [(x-int(gridSize/2), y+int(gridSize/2)),
                                        (x+int(gridSize/2), y+int(gridSize/2)),
                                        (x+int(gridSize/2), y-int(gridSize/2)),
                                        (x-int(gridSize/2), y-int(gridSize/2))
                                       ]
                        polyArray = arcpy.Array()
                        for pointsPair in listOfPoints:
                            newPoint = arcpy.Point(*pointsPair)
                            polyArray.add(newPoint)

                        newPoly = arcpy.Polygon(polyArray)
                        insertData = newPoly, o, x, y
                        cursor.insertRow(insertData)

                        # 加寫 csv table
                        line = repr(o)+","+str(x)+","+str(y)+",0\n"
                        f.write(line)
        # csv table 關閉
        f.close()

    # 輸出 raster 網格
    CreateRaster(targShp, "aa", targPath+"\\"+layerName+"_R.tif", gridSize)

    # 輸出 Point Shp
    SavePointShpFile(tempCsv,targPath+"\\"+layerName+"_P.shp")

    # 完成，計算時間
    time_e = datetime.now()
    arcpy.AddMessage("結束時間:{0}".format( time_e.strftime('%Y/%m/%d %H:%M:%S') ) )
    seconds = (time_e-time_f).seconds
    hours = int(seconds / 3600)
    minutes = int((seconds - hours*3600) / 60)
    seconds = seconds - hours*3600 - minutes*60
    arcpy.AddMessage("完成，共費時:"+str(int(hours))+" 小時,"+str(int(minutes))+" 分鐘，"+str(int(seconds))+" 秒" )

