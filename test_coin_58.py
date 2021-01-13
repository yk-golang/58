#coding=utf-8

import test_strage
import json

class Coin58():
    def __init__(self, fileNames=[""], times = 60):
        self.FileNames = fileNames
        self.DataPool = test_strage.getData(self.FileNames)

        self.Seconds = times

        self.OpenOrders = {}
        self.OpenOrders["bids"] = []
        self.OpenOrders["asks"] = []

        self.FinishOrders = {}   
        self.FinishOrders["bids"] = []
        self.FinishOrders["asks"] = []
    def Next(self):
        self.DataPool.next()

    def getOrderBook(self):
        try:
            line = self.DataPool.next()
            ##print("line:", line, " type:", type(line))
            lineJson = json.loads(line)
            return lineJson["asks"], lineJson["bids"], lineJson["curTime"]
        except Exception as e:
            print("Exception:", str(e))
            return [],[],0
    def PlaceSellOrder(self, price, amount, curTime):
        self.OpenOrders["asks"].append([price, amount, curTime])

    def PlaceBuyOrder(self, price, amount, curTime):
        self.OpenOrders["bids"].append([price, amount, curTime])

    def printOrder(self, d=""):
        print("self.OpenOrders:",self.OpenOrders, "self.FinishOrders:", self.FinishOrders, " d:", d)

    def checkBuyOrder(self, askPrice, curTime):
        size = len(self.OpenOrders["bids"]) 
        i = 0
        while i < size:
            price, amount, preTime = self.OpenOrders["bids"].pop(0)
            interSec = curTime - preTime
            if (price >= askPrice) and (interSec > 4) :
                self.FinishOrders["bids"].append([price, amount, preTime])
            else :
                if interSec <= self.Seconds:
                    self.OpenOrders["bids"].append([price, amount, preTime])
                else :
                    print("checkBuyOrder cancelOrder:", price, amount, " preTime:", preTime, " interSec:", interSec, " curTime:", curTime, " self.Seconds:", self.Seconds)
            i += 1 
    def checkSellOrder(self, bidPrice, curTime):
       size = len(self.OpenOrders["asks"]) 
       i = 0
       while i < size:
           price, amount, preTime = self.OpenOrders["asks"].pop(0)
           interSec= curTime - preTime
           if (price <= bidPrice) and (interSec > 4):
               self.FinishOrders["asks"].append([price, amount, preTime])
           else :
               if interSec <= self.Seconds:
                   self.OpenOrders["asks"].append([price, amount, preTime])
               else :
                   print("checkSellOrder cancelOrder:", price, amount, preTime, " interSec:", interSec, " curTime:", curTime, " self.Seconds:", self.Seconds)
           i += 1 

    def Check(self, askPrice, bidPrice, curTime):
        #self.printOrder()
        self.checkBuyOrder(askPrice, curTime) 
        self.checkSellOrder(bidPrice, curTime)

        ##self.printOrder()
        while 1:
            if len(self.FinishOrders["asks"])>0 and len(self.FinishOrders["bids"])>0:
                sellPrice, sellAmout, sellSecs = self.FinishOrders["asks"].pop(0)
                buyPrice, buyAmout, buySecs = self.FinishOrders["bids"].pop(0)
                money = sellPrice-buyPrice

                smallTime = sellSecs
                if buySecs < smallTime :
                    smallTime = buySecs
                print("gain money:", money, " sellSecs:",sellSecs, " buySecs:", buySecs, " cost time:", (curTime-smallTime), " curTime:", curTime)
                return money
            else :
                break
        return 0

if __name__ == "__main__":
    fileNames = ["./1.txt"]
    fileNames = ["./data/2021-01-05"]
    coin58 = Coin58(fileNames)
    i = 0
    while i < 50:
        asks, bids, curTime = coin58.getOrderBook()
        print("i:", i, " asks:", asks, " bids:", bids, " curTime:", curTime)
        if (not asks) and (not bids) and (curTime==0):
            break
        i += 1
