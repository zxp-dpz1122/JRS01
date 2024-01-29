from sklearn.preprocessing import LabelEncoder
import pandas as pd
import os
from osgeo import gdal
import numpy as np

def read_data_from_csv(file_path):
    # 读取xy数据csv文件，返回DataFrame文件
    data_raw = pd.read_csv(file_path, index_col=0)  # index_col=0,指定第一列作为行索引
    data_pro = data_raw.copy()  # 保护原始数据不收破坏
    data_pro.drop(['num', 'x', 'y'], axis=1, inplace=True)  # 删除num,x,y列，axis=1按列删除，axis=0，按行删除
    # data_.drop_duplicates(subset=None, keep="first", inplace=True)  # 去重
    y_label = data_pro.iloc[:, 0]
    label = LabelEncoder()  # 实例化
    data_pro.iloc[:, 0] = label.fit_transform(y_label)
    return data_pro

def read_data_from_excel(file_path):
    # 读取xy数据csv文件，返回DataFrame文件
    data_raw = pd.read_excel(file_path, sheet_name='data_label')
    data_pro = data_raw.copy()  # 保护原始数据不收破坏
    data_pro.drop(['num'], axis=1, inplace=True)  # 删除num,x,y列，axis=1按列删除，axis=0，按行删除
    # data_.drop_duplicates(subset=None, keep="first", inplace=True)  # 去重
    y_label = data_pro.iloc[:, 0]
    label = LabelEncoder()  # 实例化
    data_pro.iloc[:, 0] = label.fit_transform(y_label)
    return data_pro

def list_dir(path):
    list_name = []
    for file in os.listdir(path):
        # print file
        if os.path.splitext(file)[1] == '.csv':
            file_path = os.path.join(path, file)
            list_name.append(file_path)
    return list_name

class Read_Image:
    def __init__(self, infilename):
        """
        初始化变量
        :param infilename:
        """
        self.fileName = infilename
        self._get_rasterinfo()

    def _get_rasterinfo(self):
        """
          打开影像，获取影像的行列数，波段数，放射矩阵，投影信息
        """
        # 打开影像
        self.dataset = gdal.Open(self.fileName)
        # 数据描述(路径名)
        self.description = self.dataset.GetDescription()
        # 影像宽度(X方向上的像素个数)
        self.width = self.dataset.RasterXSize
        # 影像长度(Y方向上的像素个数)
        self.height = self.dataset.RasterYSize
        # 影像的波段数
        self.band_size = self.dataset.RasterCount
        # 特定的波段
        # self.band_12 = self.dataset.GetRasterBand(12)
        """
        影像的地理坐标信息
        GeoTransform[0] /* top left x 左上角x坐标*/
        GeoTransform[1] /* w--e pixel resolution 东西方向上的像素分辨率*/
        GeoTransform[2] /* rotation, 0 if image is "north up" 如果北边朝上，地图的旋转角度*/
        GeoTransform[3] /* top left y 左上角y坐标*/
        GeoTransform[4] /* rotation, 0 if image is "north up" 如果北边朝上，地图的旋转角度*/
        GeoTransform[5] /* n-s pixel resolution 南北方向上的像素分辨率*/
        """
        self.geotrans = self.dataset.GetGeoTransform()
        # 影像的投影
        self.proj = self.dataset.GetProjection()
        # 读取影像为数组
        self.data = self.dataset.ReadAsArray()
        # reshape transpose
        self.reshaped_data = self.data.reshape(self.band_size, self.width * self.height)
        self.transpose_data = np.transpose(self.reshaped_data)
        # 数据类型
        self.datatype = self.data.dtype.name
        print("read successfully")


def Image_output(output_Path, output_image, ori_image):

    """输出影像"""
    # 新建ENVI数据驱动
    driver = gdal.GetDriverByName("ENVI")
    # Create(<filename>, <xsize>, <ysize>, [<bands>], [<GDALDataType>])
    # GDALDataType分类时用gdal.GDT_CInt16,定量时用gdal.GDT_CFloat64
    # outDataset = driver.Create(output_Path,ori_image.width,ori_image.height,bands = 1,gdal.GDT_Int16)
    outDataset = driver.Create(output_Path, ori_image.width, ori_image.height, bands=1, eType=gdal.GDT_Float32)
    # 设置坐标信息
    outDataset.SetGeoTransform(ori_image.geotrans)
    # 设置投影
    outDataset.SetProjection(ori_image.proj)
    # 引入波段对象
    outBand = outDataset.GetRasterBand(1)
    # 写出数组
    outBand.WriteArray(output_image)
    print("output successfully")
    

