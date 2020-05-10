from Order import *
from sortedcontainers import SortedList
from typing import List, Union
from time import time
from Trade import Trade


class Orderbook(object):
	"""
	An orderbook.
	-------------

	It can store and process orders.
	"""
	def __init__(self):
		self.bids: SortedList[Order] = SortedList()
		self.asks: SortedList[Order] = SortedList()
		self.trades = []
		self.price = 0

	def processOrder(self, incomingOrder):
		"""
		Processes an order

		Depending on the type of order the following can happen:
		- Market Order
		- Limit Order
		- Cancel Order
		"""

		if incomingOrder.__class__ == CancelOrder:
			for order in self.bids:
				if incomingOrder.order_id == order.order_id:
					self.bids.discard(order)
					break

			for order in self.asks:
				if incomingOrder.order_id == order.order_id:
					self.asks.discard(order)
					break
			
			return # Exiting process order

		def whileClause():
			"""
			Determined whether to continue the while-loop
			"""
			if incomingOrder.side==Side.BUY:
				if incomingOrder.__class__ == LimitOrder:
					return len(self.asks) > 0 and incomingOrder.price >= self.asks[0].price # Limit order on the BUY side
				elif incomingOrder.__class__ == MarketOrder:
					return len(self.asks) > 0 # Market order on the BUY side
			else:
				if incomingOrder.__class__ == LimitOrder:
					return len(self.bids) > 0 and incomingOrder.price <= self.bids[0].price # Limit order on the SELL side
				elif incomingOrder.__class__ == MarketOrder:
					return len(self.bids) > 0 # Market order on the SELL side

		# while there are orders and the orders requirements are matched
		while whileClause():
			bookOrder = None
			if incomingOrder.side==Side.BUY:
				bookOrder = self.asks.pop(0)
				self.price = self.matchPrice(incomingOrder.price, bookOrder.price)
			else:
				bookOrder = self.bids.pop(0)
				self.price = self.matchPrice(bookOrder.price, incomingOrder.price)

			if incomingOrder.remainingToFill == bookOrder.remainingToFill:  # if the same volume
				volume = incomingOrder.remainingToFill
				incomingOrder.remainingToFill -= volume
				bookOrder.remainingToFill -= volume
				self.trades.append(Trade(
					incomingOrder.side, self.price, volume, incomingOrder.order_id, bookOrder.order_id))
				break

			elif incomingOrder.remainingToFill > bookOrder.remainingToFill:  # incoming has greater volume
				volume = bookOrder.remainingToFill
				incomingOrder.remainingToFill -= volume
				bookOrder.remainingToFill -= volume
				self.trades.append(Trade(
					incomingOrder.side, self.price, volume, incomingOrder.order_id, bookOrder.order_id))

			elif incomingOrder.remainingToFill < bookOrder.remainingToFill:  # book has greater volume
				volume = incomingOrder.remainingToFill
				incomingOrder.remainingToFill -= volume
				bookOrder.remainingToFill -= volume
				self.trades.append(Trade(
					incomingOrder.side, self.price, volume, incomingOrder.order_id, bookOrder.order_id))

				if bookOrder.side==Side.SELL:
					self.asks.add(bookOrder)
				else:
					self.bids.add(bookOrder)
				break

		if incomingOrder.remainingToFill > 0 and incomingOrder.__class__ == LimitOrder:
			if incomingOrder.side == Side.BUY:
				self.bids.add(incomingOrder)
			else:
				self.asks.add(incomingOrder)

	def getBid(self): return self.bids[0].price if len(self.bids)>0 else None
	def getAsk(self): return self.asks[0].price if len(self.asks)>0 else None
	def matchPrice(self, buy, sell): 
	    if self.price > buy:
	       return buy
	    elif self.price < sell:
	       return sell
	    return self.price

	def __repr__(self):
		lines = []
		lines.append("\033[0;32;40m" + "-"*5 + "OrderBook" + "-"*5 + "\033[0m")

		lines.append("\nAsks:" + "\033[0;32;40m")
		asks = self.asks.copy()
		while len(asks) > 0:
			lines.append(str(asks.pop()))
		lines.append("\033[0m")

		lines.append("\n" + "Bids:")
		bids = self.bids.copy()
		while len(bids) > 0:
			lines.append(str(bids.pop(0)))
     
		trades = self.trades.copy()
		lines.append("\n" + "Trades:")
		while len(trades) > 0:
			lines.append(str(trades.pop()))

		lines.append("\033[0;32;40m" + "-"*20 + "\033[0m")
		return "\n".join(lines)
	
	def __len__(self):
		return len(self.asks) + len(self.bids)
