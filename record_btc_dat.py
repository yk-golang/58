#coding=utf-8
import time
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions
#from selenium.webdriver.common.by import By
#from selenium import webdriver
#import selenium.common.exceptions as  s_exp
#
#from selenium.webdriver.common.action_chains import ActionChains

#######################
#
#
#	status 0:未成交
#	status 2:已成交
#
#######################

import random
import os
import traceback
import json
from exchange import Exchange
import datetime
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig( format='[%(asctime)s %(levelname)s %(process)d %(filename)s %(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %p',
                    #level=logging.INFO)
                    level=logging.WARNING)
                    #level=logging.DEBUG)
maxsize = 200*1024*1024*1024
handler = RotatingFileHandler("log_ccyt.log","a", maxsize, backupCount=1)
formatter = logging.Formatter('[%(asctime)s %(levelname)s %(process)d %(filename)s %(lineno)d] - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)



gIsHeadless = False
#gIgnored_exceptions= [s_exp.TimeoutException]

gAmount = 0.001
orderInfoDict = {}
maxSize = 2

gOPenOrders={}
gOPenOrders[1]=[]
gOPenOrders[2]=[]

class Coin58(Exchange):
    def __init__(self, chrome_path="/Users/wumingqi/work/work/weixin/chromedriver", ck_file="./cookies_58.json", login_url="https://www.58ex.com/", timeout=10):
        super(Coin58, self).__init__()
        self.chrome_path = chrome_path
        self.ck_file    =   ck_file
        self.login_url = login_url
        self.timeout    = timeout

        #self._init_chrom()

    def _init_chrom(self):
        os.environ["webdriver.chrome.driver"] = self.chrome_path

        #实例化谷歌设置选项
        option = webdriver.ChromeOptions()
        #添加保持登录的数据路径：安装目录一般在C:\Users\黄\AppData\Local\Google\Chrome\User Data
        #option.add_argument(r"--user-data-dir=~/Library/Application\ Support/Google/Chrome/Default/")
        option.add_argument(r"user-data-dir=~/Library/Application\ Support/Google/Chrome/coin58/")

        option.add_experimental_option('excludeSwitches', ['enable-automation'])

	##添加代理
        ###option.add_argument('--proxy-server=http://3.113.26.220:8888') 

        #无头浏览器
        if gIsHeadless :
            option.add_argument('--headless')
        option.add_argument('--start-maximized')
        option.add_argument('disable-infobars')

        self.browser = webdriver.Chrome(self.chrome_path, options=option)
        #print "1 get_window_size:", self.browser.get_window_size()
        self.browser.maximize_window()
        #print "2 get_window_size:", self.browser.get_window_size()
        #self.browser.fullscreen_window()
        #print "3 get_window_size:", self.browser.get_window_size()
        ##2560 x 1600
        if gIsHeadless:
            self.browser.set_window_size(2560, 1600)
        print "4 get_window_size:", self.browser.get_window_size()

        self.browser.implicitly_wait(10)

    def _save_cookie(self):
        cookies = self.browser.get_cookies()
        jsonCookies = json.dumps(cookies)
        with open(self.ck_file, 'w') as f:
            f.write(jsonCookies)
        print "_save_cookie"    
    
    def _get_cookie(self):
        '''
            True:success
            False: failed
        '''
        ret = False
        if not os.path.exists(self.ck_file):
            return ret
        
        with open(self.ck_file, 'r') as f:
            listCookies = json.loads(f.read())
            if not listCookies :
                self.browser.delete_all_cookies()
    
            for cookie in listCookies:
                print "cookie:", cookie
                self.browser.add_cookie({
                    'domain': cookie['domain'],
                    'name':cookie['name'],
                    'value':cookie['value'],
                    'path':'/',
                    'expires':None
                })
                #'expires':cookie.get('expiry', None)
                ret = True
            
        print "****get_cookie:", ret        
        return ret
    def login(self):
        ret = True
        try:
            self.__login()
            self.setCookie(self.browser.get_cookies())
        except :    
            traceback.print_exc()
            self.close()
            ret = False
        return ret    

    def __login(self):
        self.browser.get(self.login_url)
        #if self._get_cookie():
        #    self.browser.get(self.wechatPN_url)
        
        loginRet = False 
        try :
            self.browser.save_screenshot("58_login_click.png")

            isCookieLoginOk = False
            try: 
                #ret = WebDriverWait(self.browser, 3, 1, gIgnored_exceptions).until( expected_conditions.visibility_of_element_located((By.XPATH,'//div[@class="userInfo"]')))  
                ret = WebDriverWait(self.browser, 3, 1, gIgnored_exceptions).until( expected_conditions.visibility_of_element_located((By.XPATH,'//div[@class="asset-box"]')))  
                print ("是否找到用户个人信息的class:", ret)
                isCookieLoginOk = True   
            except:
		print "cookie login failed:"
                traceback.print_exc()
	    if not isCookieLoginOk :
            	try :
                    print ("login with user and password!!")
            	    self.browser.get("https://www.58ex.com/manage/login")
            	    ret = WebDriverWait(self.browser, 3, 1, gIgnored_exceptions).until( expected_conditions.visibility_of_element_located((By.XPATH,'//input[@class="st-input"]')))  
            	except :
            	    print "点击首页[登陆]失败"
            	    traceback.print_exc()
            	    

            	###真正的点击登陆
            	self.browser.find_element_by_xpath('//input[@class="st-input"]').send_keys('13161731897')
            	self.browser.find_element_by_xpath('//input[@autocomplete="new-password"]').send_keys('yue@5627218')
            	##self.browser.find_element_by_class_name('submit-btn sub').click()
            	login_js= "document.getElementsByClassName('submit-btn sub')[0].click()"
            	self.browser.execute_script( login_js )
            	print "click login"
            	time.sleep(1)



                obj = self.browser.find_element_by_xpath('//div[@class="st-form"]')
                #print("obj2::::", obj.get_attribute('innerHTML') )

                objHtml = obj.get_attribute('innerHTML')
                #####print("obj2:", objHtml, " size:", objHtml.find("down-input st-input"))
                if objHtml.find("down-input st-input") != -1 :
                    ##sendObj = obj.find_element_by_xpath('//div[@class="send-SMS code"]')
                    sendObj = obj.find_element_by_xpath('//a[@class="get-code button"]')
                    sendObj.click() ##发送验证码

                    slideBtn = self.browser.find_element_by_xpath('//span[@class="nc_iconfont btn_slide"]')  ##滑动解锁按钮
                    print("--------------slideBtn:", slideBtn, " id-:",slideBtn.get_attribute("id"))
                    ActionChains(self.browser).click_and_hold(on_element=slideBtn).perform() ###第一步,点击元素
                    #ActionChains(self.browser).move_to_element(slideBtn).perform() ###第一步,移动到元素上
                    time.sleep(0.2) 

                    destBtn = self.browser.find_element_by_xpath('//span[@class="nc-lang-cnt"]')
                    #第二步，拖动元素
                    ##ActionChains(self.browser).move_to_element_with_offset(to_element=slideBtn, xoffset=loc + 30, yoffset=y - 445).perform()
                    print("--------------------------move_to_element_with_offset")
                    #ActionChains(self.browser).move_to_element_with_offset(to_element=destBtn, xoffset=278, yoffset=40).perform()
                    ActionChains(self.browser).move_to_element_with_offset(to_element=destBtn, xoffset=278, yoffset=20).perform()
                    time.sleep(60)
                    #释放鼠标
                    print ("----------------------------release")
                    ###ActionChains(self.browser).release(on_element=slideBtn).perform()
                    ActionChains(self.browser).release().perform()
                    time.sleep(60)
                    

                    codeStr = raw_input("telphone code: ")
                    print("input code:", codeStr,"-")

                    obj.find_element_by_xpath('//input[@class="down-input st-input"]').send_keys(codeStr)

                    loginBtnObj = self.browser.find_element_by_xpath('//input[@class="submit-btn sub success-sub"]')
                    loginBtnObj.click()
                    time.sleep(1)



            while 1 : #用户名密码登陆成功跳出
                while 1 :
                    ret = WebDriverWait(self.browser, 3, 1).until( expected_conditions.visibility_of_element_located((By.XPATH,'//div[@class="main-nav flex-box flex-direction-row flex-justify-start flex-align-item-start flex-wrap-nowrap"]/div[1]')))  
                    #ret = WebDriverWait(self.browser, 3, 1).until( expected_conditions.visibility_of_element_located((By.LINK_TEXT,'币币交易')))  
                    if ret :
                        break
                    print "finding [币币交易] 按钮"

                while 1:
                    ##点击币币交易
                    bibiObj = self.browser.find_element_by_xpath('//div[@class="main-nav flex-box flex-direction-row flex-justify-start flex-align-item-start flex-wrap-nowrap"]/div[2]/div/a')
                    #print ("---:", bibiObj.get_attribute("")  )
                    #print ("---", bibiObj.text)
                    bibiUrl = bibiObj.get_attribute("href")
                    self.browser.get(bibiUrl)

                    #ret = WebDriverWait(self.browser, 1000, 1).until_not( expected_conditions.visibility_of_element_located((By.XPATH,'//div[@class="weui-desktop-qrcheck__img-area"]/img')))  
                    ret = False
                    try :
                        self.browser.save_screenshot("58_bibi.png")

                        ret = WebDriverWait(self.browser, 3, 1, gIgnored_exceptions).until( expected_conditions.visibility_of_element_located((By.XPATH,'//div[@class="header flex-box flex-direction-row flex-justify-start flex-align-item-center flex-wrap-nowrap"]/div')))  
                    except :
                        print " find [买入]和[卖出]选项卡 failed, 点击[币币交易]失败:%s" % traceback.format_exc()
                    if ret :
                        break
                print "qrcode disappeared, login succ!!"    
                break
        except :
            traceback.print_exc()
            return False
        ##############登陆状态######
        self._save_cookie()
        print "login success!!!!!!!"
        return True

    def close(self):
        self.browser.close()
        self.browser.quit()

    def getMoney(self):
        '''
           如果返回错误，返回空, 返回值是2层dict
        '''
        ret = {}
        headers = None
        body = ""
        response = self.fetch("https://api.58ex.com/account/assets/detail", "POST", headers, body)
        if (response["code"] == 0) and response.has_key("data") and response["data"].has_key("assetsDetail"):
            ret = response["data"]["assetsDetail"]
        return ret

    def getWhichMoney(self, firstIdx, secIdx, name, moneyDict):
        "返回2个结果，(code,money), code是0代表正常"
        if moneyDict.get(firstIdx) and moneyDict[firstIdx].get(secIdx) and moneyDict[firstIdx][secIdx]["currencyName"] == name:
            return 0, moneyDict[firstIdx][secIdx].get("available", 0)
        else :
            logging.error("moneyDict:%s" % moneyDict)
            return 1, 0

    def GetUserBtcAndUSDT(self):
        "return btcAmount, usdtAmount"
        btcAmount = 0
        usdtAmount = 0

        btc=["1","1"]
        usdt=["8","1"]

        moneyDict = self.getMoney()

        btcCode, btcAmount = self.getWhichMoney("1", "1", "BTC", moneyDict)
        usdtCode, usdtAmount = self.getWhichMoney("8", "1", "USDT", moneyDict)

        return btcAmount, usdtAmount

    def PlaceSellOrder(self, price, amount):
	'''
		side=2 卖
                oderid is int
	'''
        ret = {}
        ret["price"] = price
        ret["amount"] = amount
        ret["side"] = 2
        #body="stp=1&orderFrom=0&productId=65544&type=1&side=2&price=11000&size=0.001&timeInForce=1&postOnly=0&tradePass="
        body="stp=1&orderFrom=0&productId=65544&type=1&side=2&price=%s&size=%s&timeInForce=1&postOnly=0&tradePass=" % ( str(price), str(amount) )
        headers=None
        ###bTime = time.time()
        response = self.fetch("https://api.58ex.com/orders/place", "POST", headers, body)
        if response["code"]==0 and response["data"] and response["data"]["order"]:
            ret["orderid"] = response["data"]["order"]
            return ret
        else :
            print ("PlaceSellOrder error:", response, " ret:", ret)
        
        return ret

    def CancelOrder(self, orderid):
        body = "productId=65544&orderIds=%d" % orderid  
        headers = None
        response = self.fetch("https://api.58ex.com/orders/cancel", "POST", headers, body)
        ret = False
        if response["code"]==0 :
            ret = True
        else :
	    logging.error("CancelOrder orderid:%s response:%s" % ( str(orderid), str(response)) )
        return ret

    def PlaceBuyOrder(self, price, amount):
	'''
		side=1 买
	'''
        ret = {}
        ret["price"] = price
        ret["amount"] = amount
        ret["side"] = 1

        body="stp=1&orderFrom=0&productId=65544&type=1&side=1&price=%s&size=%s&timeInForce=1&postOnly=0&tradePass=" % ( str(price), str(amount) )
        headers=None
        ##bTime = time.time()
        response = self.fetch("https://api.58ex.com/orders/place", "POST", headers, body)
        ###print("response:", response, " type:", type(response), "message:", response["message"], " time:", time.time()-bTime)
        if response["code"]==0 and response["data"] and response["data"]["order"]:
            ret["orderid"] = response["data"]["order"]
            return ret
        else :
            print ("PlaceBuyOrder error:", response, " ret:", ret)
        
        return ret
    def FetchOpenOrders(self):
	'''
		返回dict,未成交订单
	'''
	ret = {}
	body = "productId=65544&status=0,1&page=1&pageSize=2000"
	headers = None
	response = self.fetch("https://api.58ex.com/orders/list", "POST", headers, body)
	if response.get("code") == 0:
		if response.get("data") and response["data"].get("orders"):
			ret = self.__getDictFromList(response["data"]["orders"], "open orders")
	return ret
	
    def FetchHistoryOrders(self):
	'''
		历史成交订单
	'''
	ret = {}
	body = "productId=65544&status=-1,2,3&page=1&pageSize=200"
	headers = None
	response = self.fetch("https://api.58ex.com/orders/list", "POST", headers, body)
	if response.get("code") == 0:
		if response.get("data") and response["data"].get("orders"):
			ret = self.__getDictFromList(response["data"]["orders"], "history orders")
	return ret
			
    def __getDictFromList(self, orderLst, name):
	ret = {}
	for orderInfo in orderLst:
		if ret.get( orderInfo["id"] ):
			print (name, " orderid repeate", orderInfo, " order111:", ret.get( orderInfo["id"] ), orderLst)
		else :
			ret[orderInfo["id"]] = orderInfo
	return ret

    def __sort__(self, data, reverse=False):	
	return sorted(data, key=lambda student: student[0], reverse=reverse)

    def GetHisOrders(self, sleepTime=0.1):
        openOrdersDict = {}
        while 1:
            openOrdersDict = self.FetchHistoryOrders() 
            if openOrdersDict:
                break
            time.sleep(sleepTime)
        return openOrdersDict

    def IsOrderIdInHisOrders(self, orderId, sleepTime=0.1):
        openOrdersDict = {}
        while 1:
            openOrdersDict = self.FetchHistoryOrders() 
            if openOrdersDict:
                break
            ##print ("hisOrdersDict failed:", openOrdersDict)
            time.sleep(sleepTime)
        if  orderId  in openOrdersDict:
            logging.Debug("IsOrderIdInHisOrders orderId:%s HisOrders:%s" % ( str(orderId), str(openOrdersDict[orderId])  ) )
            return True
        return False

    def getData(self):
        '''
		return buyOrderId, sellOrderId
                没有orderid返回None
	'''
	global gAmount,orderInfoDict, maxSize

        headers = None
        body="product=65544"
	response = self.fetch("https://api.58ex.com/market/order_book", "POST", headers, body)
        if (not response["data"]) or (not response["data"].get("order_book")) or ( len(response["data"]["order_book"])==0 ):
            return

        order_book = response["data"]["order_book"][0]
        asks = order_book["asks"]  #返回升序，
        bids= order_book["bids"]  #返回升序

	asks_float = map(lambda x:map(float, x), asks)
	bids_float = map(lambda x:map(float, x), bids)

	asks_dest=self.__sort__(asks_float, False)
	bids_dest=self.__sort__(bids_float, True)
        ###print ("asks::", asks)
        ###print ("asks_dest::", asks_dest)

        ###print("bids:", bids)
        ###print("bids_dest:", bids_dest)
       

        sellPrice = asks_dest[0][0] - 0.01
        buyPrice  = bids_dest[0][0] + 0.01 
        if buyPrice >= sellPrice :
            return
        ###print("getData:", response, " sellPrice:", sellPrice, " buyPrice:", buyPrice)
        buyInfo = self.PlaceBuyOrder(buyPrice, gAmount)
  	sellInfo = self.PlaceSellOrder(sellPrice, gAmount)
        print( time.time(), " buyInfo:", buyInfo, " sellInfo:", sellInfo)
        buyOrderId = buyInfo.get("orderid")
	sellOrderId = sellInfo.get("orderid")
        
	orderInfoDict[buyOrderId] = sellOrderId
        maxSize = maxSize - 1	

        return buyInfo.get("orderid"), sellInfo.get("orderid") 
 
    def getOrderBook(self):
	'''
		return asks, bids	
	'''
        headers = None
        body="product=65544"
        response = self.fetch("https://api.58ex.com/market/order_book", "POST", headers, body)
        if (not response["data"]) or (not response["data"].get("order_book")) or ( len(response["data"]["order_book"])==0 ):
            return [], []
        order_book = response["data"]["order_book"][0]
        asks = order_book["asks"]  #返回升序，
        bids= order_book["bids"]  #返回升序

        asks_float = map(lambda x:map(float, x), asks)
        bids_float = map(lambda x:map(float, x), bids)
        asks_dest=self.__sort__(asks_float, False)
        bids_dest=self.__sort__(bids_float, True)

        return asks_dest, bids_dest

def test_PlaceSellOrder():
    sellPrice = 10000
    sellAmount = 0.001
    coin58.PlaceSellOrder(sellPrice, sellAmount)

def test_getData():
    global orderInfoDict, maxSize
    while 1:
        if maxSize > 0:
        	coin58.getData()
                ##Alg1()
	
	for buyOrderId, sellOrderId in orderInfoDict.items():
		isBuy, isSell = orderIdIsSucc(buyOrderId, sellOrderId)
		if isBuy and isSell :
                        orderInfoDict.pop(buyOrderId)
                        print ("isok buyOrderId:",buyOrderId, " sellOrderId:", sellOrderId)
			maxSize += 1
                        break

        time.sleep(2)



def test_getData1():
    global orderInfoDict, maxSize
    preTime = time.time()
    while 1:
        buyOrderId, sellOrderId = Alg1()
	for buyOrderId, sellOrderId in orderInfoDict.items():
		isBuy, isSell = orderIdIsSucc(buyOrderId, sellOrderId)
		if isBuy and isSell :
                        orderInfoDict.pop(buyOrderId)
                        print ("isok buyOrderId:",buyOrderId, " sellOrderId:", sellOrderId)
			maxSize += 1
                        break

        curTime = time.time()
        sleepTime = preTime+3-curTime
        time.sleep( sleepTime )

def test_FetchOpenOrders():
    '''
	status 0:未成交
	status 2:已成交
    '''	
    openOrders = coin58.FetchOpenOrders()
    size = len(openOrders)
    time.sleep(0.1)
    while 1:
        openOrders = coin58.FetchOpenOrders()
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " test_FetchOpenOrders openOrders:",openOrders)
        if len(openOrders) != size:
            break

        ##ret = openOrders.has_key(281613285937710)
        ##print ("test_FetchOpenOrders:", openOrders, " ret:", ret)
        ##if not ret:
        ##    break
        time.sleep(0.1)

def test_FetchHistoryOrders():
    print ("test_FetchHistoryOrders:", coin58.FetchHistoryOrders())	

def Alg1(buyFlowRadio=0.5, sellFlowRadio=0.5, isBuy=True, isSell=True):
    global gAmount,orderInfoDict, maxSize

    asks, bids = coin58.getOrderBook()
    if (not asks) or (not bids):
	print ("asks or bids is None asks:", asks, " bids:",bids) 
	return 
    print ("Alg1 asks:", asks, " bids:", bids)

    sellPrice1 = asks[0][0] 
    buyPrice1  = bids[0][0]
    if buyPrice1 >= sellPrice1 :
        return
    
    avgPrice = (sellPrice1 + buyPrice1) / 2	

    buyPrice = avgPrice - buyFlowRadio
    sellPrice = avgPrice + sellFlowRadio
    if buyFlowRadio < 0:
	#buyPrice = buyPrice1 + 0.01
	buyPrice = buyPrice1 + abs(buyFlowRadio)
    if sellFlowRadio < 0:
        #sellPrice = sellPrice1 - 0.01
        sellPrice = sellPrice1  + sellFlowRadio
    
    if  isBuy and isSell and  (buyPrice >=sellPrice):
    	print("Alg1 sellPrice1:", sellPrice1, " buyPrice1:", buyPrice1, " avgPrice:", avgPrice, " buyPrice:", buyPrice, " sellPrice:", sellPrice, " buyFlowRadio:", buyFlowRadio, " sellFlowRadio:", sellFlowRadio)
	return	None, None

    
    buyInfo = {}
    sellInfo = {}
    if isBuy :
        buyInfo = coin58.PlaceBuyOrder(buyPrice, gAmount)
    if isSell :
    	sellInfo = coin58.PlaceSellOrder(sellPrice, gAmount)
    print( time.time(), "  Alg1 buyInfo:", buyInfo, " sellInfo:", sellInfo, " buyFlowRadio:", buyFlowRadio, " sellFlowRadio:", sellFlowRadio, " buyPrice1:", buyPrice1, " sellPrice1:",sellPrice1)
    curTime = time.time()
    buyOrderId = buyInfo.get("orderid") 
    sellOrderId = sellInfo.get("orderid")

    ###orderInfoDict[buyOrderId] = sellOrderId
    ###maxSize = maxSize - 1	
 
    return buyOrderId, sellOrderId

def getCorrectOpenOrders():
    openOrdersDict = {}
    while 1:
    	openOrdersDict = coin58.FetchOpenOrders() 
    	if openOrdersDict:
            break
        print ("openOrdersDict failed:", openOrdersDict)
        time.sleep(1)
    return openOrdersDict

def getHisOrders():
    openOrdersDict = {}
    while 1:
    	openOrdersDict = coin58.FetchHistoryOrders() 
    	if openOrdersDict:
            break
        ##print ("hisOrdersDict failed:", openOrdersDict)
        time.sleep(1)
    return openOrdersDict


def orderIdIsStrictSucc(orderId):
    '''
        严格检查，如果orderid是None，返回false
	orderid是否已成交订单中，在的话，True，否则False
    '''
    if not orderId:
        return False
    
    hisOrdersDict = getHisOrders()
    return hisOrdersDict.has_key( orderId  )

def orderIdIsSucc(buyOrderId, sellOrderId):
    '''
	orderid是否已成交订单中，在的话，True，否则False
    '''	
    openOrdersDict = getHisOrders()
    isBuy = True
    isSell = True
    if not buyOrderId:
	isBuy = True
    else :
	isBuy = openOrdersDict.has_key(buyOrderId)

    if not sellOrderId:
	isSell = True
    else :
	isSell = openOrdersDict.has_key(sellOrderId)

    print ( openOrdersDict, " isBuy:",isBuy, " isSell:", isSell, " buyOrderId:", buyOrderId, " sellOrderId:",sellOrderId, " maxSize:", maxSize)
    ##print ("hisOrdersDict:", openOrdersDict, " isBuy:",isBuy, " isSell:", isSell, " buyOrderId:", buyOrderId, " sellOrderId:",sellOrderId, " maxSize:", maxSize)
    return isBuy, isSell
	
###def test_Alg1():
###    while 1:
###        buyOrderId, sellOrderId = coin58.getData()
###        time.sleep(1)
###        firstOrderTime = time.time()
###        while 1:
###            curTime = time.time()
###            if firstOrderTime + 60 < curTime:
###                print ("break, next a nother order, firstOrderTime:", firstOrderTime, " curTime:", curTime)	
###                break
###            isBuySucc, isSellSucc = orderIdIsSucc(buyOrderId, sellOrderId)
###            print ("isBuySucc:",isBuySucc, " isSellSucc:", isSellSucc, " buyOrderId:", buyOrderId, " sellOrderId:",sellOrderId)
###            if isBuySucc and isSellSucc:
###                print ("direct next order, isBuySucc:",isBuySucc, " isSellSucc:",isSellSucc)
###		break
###            buyFlowRadio = 0.5
###            sellFlowRadio = 0.5
###            if isBuySucc :
###		buyFlowRadio = -1
###            if isSellSucc:
###		sellFlowRadio = -1
###            secBuyOrderId, secSellOrderId = Alg1(buyFlowRadio, sellFlowRadio)
### 	    time.sleep(2)
###            while 1:
### 		isSecBuySucc, isSecSellSucc = orderIdIsSucc(secBuyOrderId, secSellOrderId)
###		if isSecBuySucc and isSecSellSucc :
### 			break
###                print ("secBuyOrderId:",secBuyOrderId, " secSellOrderId:",secSellOrderId, " isSecBuySucc:",isSecBuySucc, " isSecSellSucc:",isSecSellSucc)
###            	curTime = time.time()
###            	if firstOrderTime + 60 < curTime:
###            	    print ("break  secBuyOrderId, firstOrderTime:", firstOrderTime, " curTime:", curTime)	
###            	    break
###
### 		time.sleep(2)

def Alg2(buyFlowRadio=2, sellFlowRadio=2):
    asks, bids = coin58.getOrderBook()
    if (not asks) or (not bids):
	print ("asks or bids is None asks:", asks, " bids:",bids) 
	return 
    print ("Alg1 asks:", asks, " bids:", bids)

    sellPrice1 = asks[0][0] 
    buyPrice1  = bids[0][0]
    if buyPrice1 >= sellPrice1 :
        return
    
    avgPrice = (sellPrice1 + buyPrice1) / 2	

    buyPrice = avgPrice - buyFlowRadio
    sellPrice = avgPrice + sellFlowRadio
    
    if buyPrice >=sellPrice:
    	print("Alg1 sellPrice1:", sellPrice1, " buyPrice1:", buyPrice1, " avgPrice:", avgPrice, " buyPrice:", buyPrice, " sellPrice:", sellPrice, " buyFlowRadio:", buyFlowRadio, " sellFlowRadio:", sellFlowRadio)
	return	None, None

    buyInfo = coin58.PlaceBuyOrder(buyPrice, gAmount)
    sellInfo = coin58.PlaceSellOrder(sellPrice, gAmount)
    print( time.time(), "  Alg1 buyInfo:", buyInfo, " sellInfo:", sellInfo, " buyFlowRadio:", buyFlowRadio, " sellFlowRadio:", sellFlowRadio)

def test_Alg2():
    pass		

def test_getOrderBook():
    while 1:
        asks, bids = coin58.getOrderBook()
        if (not asks) or (not bids):
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " empty asks:", asks, " bids:", bids)
        else :
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " asks[0]", asks[0], " bids[0]:", bids[0], " asks[1]:", asks[1], " bids[1]:", bids[1])
        time.sleep(0.1)


def test_FetchOpenOrdersAndPlaceBuyOrder():
    buyPrice = 8000
    buyInfo = coin58.PlaceBuyOrder(buyPrice, gAmount)
    print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " test_FetchOpenOrdersAndPlaceBuyOrder buyInfo:", buyInfo)
    buyOrderId = buyInfo.get("orderid")
     
    
    while 1:
        openOrders = coin58.FetchOpenOrders()
        if buyOrderId in openOrders:
            print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " in openOrders:",openOrders, " buyOrderId:", buyOrderId)
            test_CancelOrder(buyOrderId)
            while 1:
                openOrders = coin58.FetchOpenOrders()
                if buyOrderId not in openOrders:
                    print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " not in openOrders:",openOrders, " buyOrderId:", buyOrderId)
                    break
                time.sleep(0.1)
            break
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " not in openOrders:",openOrders, " buyOrderId:", buyOrderId)
        time.sleep(0.1)

def test_PlaceBuyOrderAndCancel():
    buyPrice = 8000
    buyInfo = coin58.PlaceBuyOrder(buyPrice, gAmount)
    print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " test_FetchOpenOrdersAndPlaceBuyOrder buyInfo:", buyInfo)
    buyOrderId = buyInfo.get("orderid")
    test_CancelOrder(buyOrderId)
    return
    
    while 1:
        openOrders = coin58.FetchOpenOrders()
        if buyOrderId in openOrders:
            print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " in openOrders:",openOrders, " buyOrderId:", buyOrderId)
            break
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " not in openOrders:",openOrders, " buyOrderId:", buyOrderId)
        time.sleep(0.1)

def test_CancelOrder(orderid):
    while 1:
        ret = coin58.CancelOrder(orderid)
        print (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), " test_CancelOrder orderid:",orderid, " ret:", ret)
        if ret:
            break
        time.sleep(0.1)

def record_getOrderBook():
    sleepTime = 0
    result = {}
    while 1:
        curTime = time.time()
        sleepTime = int(curTime) + 1 -curTime
        if sleepTime > 0:
            asks, bids = coin58.getOrderBook()
            #if len(asks) <5 and len(bids) < 5:
            #    print("asks:", asks, " bids:", bids, " curTime:", curTime)
            #    continue
            #asks = asks[:5]
            #bids = bids[:5]
            result["asks"] = asks
            result["bids"] = bids
            result["curTime"] = curTime

            print ("getOrderBook:", result)
            filename = "./58/data/" + datetime.datetime.now().strftime('%Y%m%d%H')
            with open(filename, 'a+') as f:
                json.dump(result, f)
                f.write("\n")

        time.sleep(sleepTime)

if __name__ == "__main__" :

    coin58 = Coin58()
    #print coin58.login()

    record_getOrderBook()
    #test_getOrderBook()
    #while 1:
    #    print (coin58.GetUserBtcAndUSDT())
    #    time.sleep(3)

    #策略测试
    ###test_getData()	
    ##test_getData1()	

    ##test_FetchOpenOrdersAndPlaceBuyOrder()
    ##test_PlaceBuyOrderAndCancel()





    ##test_FetchOpenOrders()
    ##test_FetchHistoryOrders()
    ##Alg1()
    ###Alg1(-1, -1)
    ##test_Alg1()
	
    coin58.close()

