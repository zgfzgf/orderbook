from Orderbook import Orderbook
from Order import *
from Trade import Trade
from random import getrandbits, randint, random

# Benchmark
OB = Orderbook()
numOrders = 20
orders = []
for n in range(numOrders):
	if bool(getrandbits(1)):
		orders.append(LimitOrder(n, Side.BUY, randint(1, 200), randint(1, 4)))
	else:
		orders.append(LimitOrder(n, Side.SELL, randint(1, 200), randint(1, 4)))

from time import time
start = time()
for order in orders:
	print("\033[0;31;40m" + str(order) + "\033[0m")
	OB.processOrder(order)
	print(OB)
"""
end = time()
totalTime = (end-start)
print("Time: " + str(totalTime))
print("Time per order (us): " + str(1000000*totalTime/numOrders))
print("Orders per second: " + str(numOrders/totalTime))
print(OB)
"""
