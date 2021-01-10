#coding=utf-8
from goto import with_goto


f = None

@with_goto
def getOrderBook(filenames=["./58/data/2021-01-05"]):
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
def testData():
    fileNames=["./1.txt", "./2.txt"]
    dat = getOrderBook(fileNames)
    line = dat.next()
    while line:
        print("main line:", line)
        line = dat.next()
    print("--------------------")

def test():

if __name__ == "__main__":
    test()
