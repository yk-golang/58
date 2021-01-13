#coding=utf-8
from goto import with_goto
import json

f = None

@with_goto
def getData(filenames=["./58/data/2021-01-05"]):
    '''
        return data
    '''
    global f
    label .begin
    if f:
        line = f.readline()
        while line:
            ##print line, " filenames:",filenames    # 后面跟 ',' 将忽略换行符
            yield line
            line = f.readline()
        #filenames.pop(0)

    print("next file:", filenames)
    while 1:        
        if len(filenames) == 0:
            print("all file read ok!")
            break
        fileName=filenames.pop(0)
        print("read fileName:", fileName)
        f =  open(fileName, "r")
        line = f.readline()
        if line:
            yield line
            goto .begin
            #break
def getOrderBook():
    fileNames=["data/2021-01-05"]
    fileNames=["./1.txt"]
    dat = getData(fileNames)
    line = dat.next()
    while line:
        print("main line:", line)
        line = dat.next()
        print("line:", type(line), line)
    print("--------------------")


gDataPool = getData()

def getOrderBook1():
    fileNames=["data/2021-01-05"]
    fileNames = ["./1.txt"]
 
    dat = getData(fileNames)
    asks = []
    bids = []
    curTime = 0
    if dat :
        line = dat.next() ##(dat)
        lineJson = json.loads(line)
        return lineJson["asks"], lineJson["bids"], lineJson["curTime"]
    else :
        print("********************")
    return asks, bids, curTime
    
def test1():
    getOrderBook1()

def test():
    asks, bids, curTime = getOrderBook1()
    print("-----test---asks:",asks, " bids:",bids, " curTime:", curTime)

if __name__ == "__main__":
    i = 0
    while i < 50:
        test()
