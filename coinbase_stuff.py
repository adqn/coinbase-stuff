import json
import os
import matplotlib as mp
import matplotlib.pyplot as plt
import numpy as np
from coinbase.wallet.client import Client

# API keys go here
#client = Client(API_KEY,  API_SECRET)

currency_code = 'USD'

#priceBT = client.get_spot_price(currency=currency_code)
#priceETH = client.get_spot_price(currency_pair='ETH-USD')

#print('Bitcoin price: %s' % priceBT.amount)
#print('ETH price: %s' % priceETH.amount)

# object for manipulating JSON market data
# will fix the relative directory path some other time
# there has to be a better way to do this
class prices_obj():
  def __init__(self, filepath=None):
    self.filepath = filepath

    # slicing data to 100 or so slices for pyplot scaling purposes
    self.data = self.get_json()
    self.data = self.data[:200]
    self.prices_open = self.get_prices_open()
    self.prices_close = self.get_prices_close()
    self.periods = self.get_periods()
    
    self.open_close_pairs = self.get_pairs()
    self.candlesticks = self.get_candlesticks()
  
    # placeholders for analysis results
    self.rsi_cur = []
  
  # open json file for manipulation
  def get_json(self):
    xjson = ''
    if self.filepath == None:
      with open('D://prog/python/data/14dayeth') as json_file:
        xjson = json.load(json_file)
    else:
      with open(self.filepath) as json_file:
        xjson = json.load(json_file)
    return xjson
  
  # get array of price pairs for open and close
  # add high and low, eventually 
  def get_pairs(self):
    pairs = []
    for i in range(len(self.data)):
      pairs.append([self.data[i]["open"], self.data[i]["close"]])
    pairs.reverse()
    return pairs
  
  # get array of open close deltas for candlestick plotting
  def get_candlesticks(self):
    output = []
    for pair in self.open_close_pairs:
      delta = pair[1] - pair[0]
      output.append(delta)
    return output
  
  # update prices_close (for now) with latest market price
  def get_current(self):
    return
  
  # get array of open prices for each period in json object
  # reverse list to reflect earliest => latest price
  def get_prices_open(self):
    output = []
    for period in self.data:
      output.append(period["open"])
    output.reverse()
    return output
  
  # get array of close prices
  def get_prices_close(self):
    output = []
    for period in self.data:
      output.append(period["close"])
    output.reverse()
    return output  
  
  # slice data into chunks of period_size 
  def get_periods(self, period_size=10, type='close'):
    output = []
    step = period_size
    a = 0  
    
    if type == 'open':
      for i in range(int(len(self.prices_open)/step)):
        if a+step <= len(self.prices_open)+step:
          output.append((self.prices_open[a*step:(i+1)*step]))
          a += 1
    if type == 'close':
      for i in range(int(len(self.prices_close)/step)):
        if a+step <= len(self.prices_close)+step:
          output.append((self.prices_close[a*step:(i+1)*step]))
          a += 1
      
    return output
  
  # get array of average price per slice of period_size
  def period_avg(self):
    output = []
    for p in self.periods:
      output.append(sum(p)/len(p))
    return output
  
  # of course, this is the exponental moving average
  def ema(self, periods=12):
    sma = []
    ema = []
    step = int(len(self.prices_close)/periods)
    weight = 2/(periods+1)
    j = 0
    for i in range(step):
      sma.append(sum(self.prices_close[j:(i+1)*periods])/periods)
      j += periods
    
    #ema.append()
  
  # calculate rsi for number of periods = per
  # training_size indicates amount of data points for initial calculations
  def rsi(self, per=14, training_size=0):
    gains = []
    losses = []       
    avg_gain = 0
    avg_loss = 0
    
    for i in (range(per - 1)):
      delta = self.prices_close[i+1] - self.prices_close[i]
      if delta > 0:
        gains.append(delta)
      else:
        losses.append(delta)
    for i in range(len(gains)-1):
      avg_gain += gains[i]
    avg_gain = abs(avg_gain/per)
    for i in range(len(losses)-1):
      avg_loss += losses[i]
    avg_loss = abs(avg_loss/per)
    
    #print(avg_gain)
    #print(avg_loss)
    
    
    first_rs = avg_gain/avg_loss
    first_rsi = abs(100 - (100/1+first_rs))
    smooth_rs = (((avg_gain*13)+gains[-1])/14)/(((avg_loss*13)+losses[-1])/14)
    rsi = abs(100 - (100/1+smooth_rs))
    
    # for i in range(len(self.prices_close - per)):
    
    print("rs: %s" % first_rsi)
    return rsi

# get pyplot rectangles and draw immediately
# p = prices_obj instance
def create_candlesticks(p):
  i = 0
  for delta in p.candlesticks:
    if delta != abs(delta):
      rec = plt.Rectangle((i, p.prices_open[i]), .5, delta, color='red')
    else:
      rec = plt.Rectangle((i, p.prices_close[i]-delta), .5, delta, color='green')
    plt.gca().add_patch(rec)
    i += 1

p = prices_obj()

# get domain for moving average test thing 
period_x = np.arange(0, len(p.prices_close), len(p.prices_close)/len(p.periods))

plt.figure(1, [15, 10])

create_candlesticks(p)

# plot close prices
plt.plot(p.prices_close, linewidth=1, c='green')
#test thing for moving average of arbitrary size (p.periods[i])
plt.plot(period_x, p.period_avg(), 'r--')

#plt.axes()
#rec = plt.Rectangle((0,0), 20, 20, color='red')


plt.show()