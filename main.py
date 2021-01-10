#coding=utf-8

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

if __name__ == "__main__":
