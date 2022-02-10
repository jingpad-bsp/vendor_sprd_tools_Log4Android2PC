import logging
import time
import os
import datetime
import shutil
from result import  Result

def copyFile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        logging.info("move file error")
    else:
        fpath,fname=os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        shutil.copyfile(srcfile,dstfile)
        logging.info( "copy %s -> %s"%( srcfile,dstfile))
class LogGetManager:
    def __init__(self, path, deviceList, version):
        self.mEntryList = []
        self.mCurrentPath = path+os.sep
        self.mDeviceList = deviceList
        self.mToolVersion = version

    def addEntry(self, entry):
        self.mEntryList.append(entry)

    def start(self):
        for device in self.mDeviceList:
            device.root()
            deviceConnected = device.waitForDeviceConnected(60)
            if deviceConnected == False:
                logging.warn("device: "+device.getDeviceID()+" is not connected")
                continue
            else:
                productName = device.getProductName()
                logging.info("productName:"+ productName)
                startTime = time.time()
                nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                topDir = self.mCurrentPath +"logs"+os.sep+ productName +"_" + device.getDeviceID()+os.sep+str(nowTime)+os.sep
                if os.path.exists(topDir) == False:
                    os.makedirs(topDir)
                result = Result(topDir, device.getDeviceID())
                result.writeResult("start pull log time :" + str(nowTime) + ",tools version is "+self.mToolVersion+"\n")
                result.writeResult("productName :" + productName + "\n")
                logging.info( device.getDeviceID()+" log will save in "+topDir)
                for entry in self.mEntryList:
                    entry.excute(device, topDir, result)
                    if entry.error !=  0 :
                        if "ylog" in entry.mParam and "data" not in entry.mParam:
                            result.writeResult( entry.mParam+" pulled failed,please re-pull\n")
                            break
                        if "corefile" in entry.mParam and "data" not in entry.mParam:
                            result.writeResult(entry.mParam+"corefile pulled failed,please re-pull\n")
                            break
                        if "slog" in entry.mParam and "data" not in entry.mParam:
                            result.writeResult(entry.mParam+"slog pulled failed,please re-pull\n")
                            break
                endTime = time.time()
                spendTime = int(endTime - startTime)
                m, s = divmod(spendTime, 60)
                h, m = divmod(m, 60)
                result.writeResult("pull log spend time :"+ str(h)+" Hours,"+str(m)+" Minute,"+str(s)+" Seconds\n")
                copyFile("pulllog.log",topDir+"/pulllog.log")

