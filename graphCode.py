import matplotlib.pyplot as plt
import json
import numpy as np


current_price = []
net_gain = []
time = []

f = open('portfolio_value.json',"r")

# returns JSON object as
# a dictionary
data = json.load(f)

count = 0
for item in data["value"]:
    count += 1

    current_price.append(item["current_value"])
    net_gain.append(item["net_gain_or_loss"])
    time.append(abs(item["time"]/1000))


plt.plot(time,net_gain)
plt.ticklabel_format(useOffset=False)
plt.xlabel("Time")
plt.ylabel("Net Gain/Loss")
plt.show()

