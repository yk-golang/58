#coding=utf-8
import test_coin_58  as coin58
import json
import logging
import time


def calLst(lst):
    global nums
    '''
       asc
    '''
    count = 0
    for i in range(1,nums):
        if lst[i] > lst[i-1] :
            count+=1
    rate = float(count) / (nums-1)
    return rate

if __name__ == "__main__":
    fileNames = ["./1.txt"]
    fileNames = ["./data/2021-01-05"]
    coin58 = coin58.Coin58(fileNames)


    sleepTime = 3
    nums = 10
    sellLst = []
    buyLst = []
    sellAscLst = []
    curTime = -1
    while curTime != 0:
        asks, bids, curTime = coin58.getOrderBook()
        print("curTime:", curTime, " asks:", asks, " bids:", bids)
        coin58.Next()
        coin58.Next()

        sellLst.append(asks[0][0])
        buyLst.append(bids[0][0])
        if len(sellLst) >= nums:
            size = len(sellLst)
            sellLst = sellLst[size-nums:size]
            buyLst = buyLst[size-nums:size]

            sellAsyRate = calLst(sellLst)
            buyAsyRate = calLst(buyLst)
            
            sellAscLst.append(sellAsyRate)
            sellAscRateRate = None
            if len(sellAscLst) >= nums:
                size = len(sellAscLst)
                sellAscLst = sellAscLst[size-nums:size]
                sellAscRateRate = calLst(sellAscLst)

            #print("sellLst:", sellLst, " sellAsyRate:", sellAsyRate, " buyLst:", buyLst, " buyAsyRate:", buyAsyRate)
            print("sellLst:", sellLst, " sellAsyRate:", sellAsyRate, " sellAscRateRate:", sellAscRateRate, " buyLst:", buyLst)
            #print("sellLst:", sellLst, " sellAsyRate:", sellAsyRate)
            #print("buyLst:", buyLst, " buyAsyRate:", buyAsyRate)

        time.sleep(sleepTime)
