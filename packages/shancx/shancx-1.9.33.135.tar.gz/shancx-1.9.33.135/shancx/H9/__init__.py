from shancx.H9.ahisearchtable import ahisearchtable
from shancx.H9.ahi_read_hsd import ahi_read_hsd
from tqdm import tqdm
import os
import numpy as np 
import datetime 
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
class AHIScene(ahi_read_hsd, ahisearchtable) :
    def __init__(self, subpoint=140.7, resolution=0.02):
        super().__init__(subpoint=subpoint, resolution=resolution)
        self.Tempfile = []
    def hsdBlock(self, srcHSDfiles, tmppath, fillvalue=65535) :
        ''' 对H8、H9的HSD文件进行解析、拼接成NOM '''
        # HS_H09_20230115_0400_B01_FLDK_R10_S0110.DAT.bz2
        BandID, BlockIDMin, BlockIDMax, SegmentTotal = self.setHSDInfo(srcHSDfiles)
        outdata = None
        BlockIDs = []
        with tqdm(total=len(srcHSDfiles), iterable='iterable',
                  desc = '正在进行第%i波段块合成' %(BandID), mininterval=1) as pbar:
            for hsdname in srcHSDfiles :
                if not os.path.isfile(hsdname):
                    print('文件不存在【%s】' %(hsdname))
                    pbar.update(1)
                    continue

                # 获取文件名信息
                nameinfo = self.getHSDNameInfo(hsdname)
                if nameinfo is None :
                    pbar.update(1)
                    continue
                SegmentNum = nameinfo['SegmemtID']

                # print('正在解压bz2文件【%s】' %(hsdname))
                self._unzipped = self.unzip_file(hsdname, tmppath)
                if self._unzipped:
                    self.is_zipped = True
                    filename = self._unzipped

                    self.Tempfile.append(filename)
                else:
                    filename = hsdname

                if filename.endswith('.bz2') :
                    print('解压bz2文件失败【%s】' %(filename))
                    pbar.update(1)
                    continue

                # 根据块号对数据进行拼接
                data = self.readhsd(filename, SegmentNum)
                if data is None :
                    pbar.update(1)
                    continue

                if outdata is None :
                    line, pixel = data.shape
                    outdata = np.full(shape=(line*SegmentTotal, pixel),
                                      fill_value=fillvalue, dtype=np.uint16)

                data[np.isnan(data)] = fillvalue/100.0
                outdata[(SegmentNum-BlockIDMin)*line:(SegmentNum-BlockIDMin+1)*line, :] \
                    = np.array(data*100.0, dtype=np.uint16)
                BlockIDs.append(SegmentNum)
                pbar.update(1)
        pbar.close()
        self.__del__()
        return outdata 
  
    def setHSDInfo(self, filelist):

        BandID = None
        BlockIDs = []
        for filename in filelist :
            nameinfo = self.getHSDNameInfo(filename)
            if nameinfo is None :
                continue

            if BandID is None :
                BandID = nameinfo['BandID']
            elif BandID != nameinfo['BandID'] :
                raise Exception('输入的文件列表中有多个波段的块数据文件【%s】' %(filename))
            BlockIDs.append(nameinfo['SegmemtID'])

        BlockIDMin = np.nanmin(BlockIDs)
        BlockIDMax = np.nanmax(BlockIDs)

        SegmentTotal = int(BlockIDMax-BlockIDMin+1)

        return BandID, BlockIDMin, BlockIDMax, SegmentTotal

    def getHSDNameInfo(self, filename):

        basename = os.path.basename(filename)
        basename = basename.split('.')[0]
        if len(basename) != 39 :
            print('非标准文件名，需要输入文件名【HS_H09_YYYYMMDD_HHMM_BXX_FLDK_R20_S0810】')
            return None

        nameinfo = {}
        namelist = basename.split('_')

        nameinfo['SatID'] = namelist[1]
        nameinfo['StartTime'] = datetime.datetime.strptime('%s %s' %(namelist[2], namelist[3]), '%Y%m%d %H%M')
        nameinfo['BandID'] = int(namelist[4][1:])   # 2-digit band number (varies from "01" to "16");
        nameinfo['ObsType'] = namelist[5]
        nameinfo['Resolution'] = float(namelist[6][1:])/10.0/100    # spatial resolution ("05": 0.5km, "10": 1.0km, "20": 2.0km);
        nameinfo['SegmemtID'] = int(namelist[7][1:3])
        nameinfo['SegmemtTotal'] = int(namelist[7][3:5])    # total number of segments (fixed to "10")

        return nameinfo

    def __del__(self):
        # pass
        for filename in self.Tempfile :
            if os.path.isfile(filename) :
                try:
                    os.remove(filename)
                except BaseException as e :
                    time.sleep(1)
                    try:
                        fp = open(filename, 'r')
                        fp.close()
                        os.remove(filename)
                    except BaseException as e :
                        pass
