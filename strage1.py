#coding=utf-8
import test_coin_58  as coin58
import json
import logging
import time

gMoney = 0

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

def getCountOrder(orders, count, diff=0.01):
    if len(orders) == 0:
        return NULL
    amount = 0
    #price = orders[0][0]
    price = None
    for order in orders:
        amount += order[1]
        if amount > count:
            price = order[0]
            break
    return price

if __name__ == "__main__":
    fileNames = ["./1.txt"]
    fileNames = ["./data/2021-01-05"]
    #fileNames = ["./data/2021-01-05", "./data/2021-01-06", "./data/2021-01-07", "./data/2021-01-08", "./data/2021-01-09"]
    ##fileNames = ["./test.dat"]

    nextTime = 180   #order timeout seconds
    baseSellCount = 8
    baseBuyCount = 8
    tokenNextOrderTime = nextTime #toke next order time

    coin58 = coin58.Coin58(fileNames, nextTime)
    amount = 0.001

    bidsOrder = []
    asksOrder = []
    bidFinishedOrder = []
    askFinishedOrder = []


    sellCount = baseSellCount
    buyCount = baseBuyCount
    
    nums = 10
    sellLst = []
    buyLst = []
    sellAscLst = []
    curTime = -1

    while curTime != 0:
        asks, bids, curTime = coin58.getOrderBook()
        if curTime ==0:
            break
        #asks = asks[0:1]
        #bids = bids[0:1]

        print("curTime:", curTime, " asks:", asks, " bids:", bids, "gMoney", gMoney)

        sellOrderCount = len(coin58.FinishOrders["asks"])
        buyOrderCount = len(coin58.FinishOrders["bids"])
        if sellOrderCount > 1 :
            sellOrderCount = 1

        if buyOrderCount > 1 :
            buyOrderCount = 1

        sellCount= baseSellCount * (1+ sellOrderCount)
        buyCount = baseBuyCount * (1+buyOrderCount)

        sellPrice = getCountOrder(asks, sellCount) - 0.01
        buyPrice = getCountOrder(bids, buyCount) + 0.01


        coin58.PlaceSellOrder(sellPrice, amount, curTime)
        coin58.PlaceBuyOrder(buyPrice, amount, curTime)
        coin58.printOrder( " sellCount:"+str(sellCount) + " buyCount:" + str(buyCount) + " curTime:" + str(curTime)  + " gMoney:" + str(gMoney))

        tmpNextTime = 1
        while tokenNextOrderTime > tmpNextTime:
            #coin58.Next()
            asks, bids, curTime = coin58.getOrderBook()
            if curTime == 0:
                break
            sellPriceMin = asks[0][0]
            buyPriceMin = bids[0][0]
            m = coin58.Check(sellPriceMin, buyPriceMin, curTime)
            gMoney += m

            tmpNextTime += 1
            if m != 0:
                print("gMoney:", gMoney)

        #time.sleep(sleepTime)
    coin58.printOrder("-------end---:")
