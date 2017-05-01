#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib
import datetime as dt

from matplotlib import pyplot as plt

# Import modules from /batterym/ folder.
import os
import sys
sys.path.append(os.path.abspath('../batterym'))
import log
import model
import history
import mathstat


# Emulates the aesthetics of ggplot (a popular plotting package for R).
plt.style.use('ggplot')

#logs = log.get_battery('../logs/capacity_example')
logs = log.get_battery()
h = history.History(logs, smoothing=True)
hdata = h.data()

data = pd.DataFrame(hdata)
data = data.rename(columns={'time': 'timestamp'})
data = data.sort_values(by='timestamp', ascending=True)

print data.head()

# Extract capacity time series.
# Parameters
X_NOW = 9
X_BEGIN = X_NOW - 5
X_END = X_NOW + 25.0
Y_MAX = 101
Y_MIN = 0
blue = '#2e7eb3'
light_blue = '#81b1d1'
green = '#4aa635'
light_green = '#7db471'


y1 = data['capacity'].values
y2 = data['capacity_raw'].values
f = data['status'].values
x = data['virtual_time_hour']
cap = pd.DataFrame({'capacity': y1, 'capacity_raw': y2, 'status': f}, index=x)
cap = cap[X_END:X_BEGIN]
cap_old = cap[X_END:X_NOW]
cap_new = cap[X_NOW:X_BEGIN]

charging = cap[cap['status'] == 'Charging']
discharging = cap[cap['status'] == 'Discharging']

charging_old = charging[X_END:X_NOW]
charging_new = charging[X_NOW:X_BEGIN]
discharging_old = discharging[X_END:X_NOW]
discharging_new = discharging[X_NOW:X_BEGIN]

cap_raw_old = cap_old['capacity_raw']
cap_raw_new = cap_new['capacity_raw']

fig, ax = plt.subplots(2)

# ax[0].fill_between(cap_raw_old.index, 0,
#                    cap_raw_old.values, facecolor='#999999')
# ax[0].fill_between(cap_raw_new.index, 0,
#                    cap_raw_new.values, facecolor='#cccccc')
# ax[0].plot(cap['capacity'], color='b')
# ax[0].plot(charging_old['capacity'], color='#00FF00',
#            marker='o', linestyle='None')
# ax[0].plot(discharging_old['capacity'], color='#0000FF',
#            marker='o', linestyle='None')
# ax[0].plot([X_NOW, X_NOW], [Y_MIN, Y_MAX], color='r')
# ax[0].set_xlim(X_BEGIN, X_END)
# ax[0].set_ylim(Y_MIN, Y_MAX)
# ax[0].invert_xaxis()

# ax[1].hist(cap['capacity'], bins=10)

# hdata = h.data()
# print 'len hdata:', len(hdata)
# logs = filter(lambda e: e['virtual_time_hour'] < 2.0, hdata)
# print 'len logs:', len(logs)
# h = history.History(logs, smoothing=True)

status = 'Charging'

for i in [0.1, 0.5, 0.9]:
    color = 'r'

    bat_model = model.StatBateryModel(h)
    bat_model.percentile = i
    bat_model.history_limit = 1000.0
    bat_model.calculate()

    if status == 'Charging':
        capacity = bat_model.charge
        bins = bat_model.charge_bins
        slopes = bat_model.charge_slopes
        timeline_total = bat_model.charge_timeline_total
    if status == 'Discharging':
        capacity = bat_model.discharge
        bins = bat_model.discharge_bins
        slopes = bat_model.discharge_slopes
        timeline_total = bat_model.discharge_timeline_total

    # data = pd.DataFrame(capacity)
    # x = data['time'].values
    # y = data['capacity'].values
    # ax[3].plot(pd.Series(y, index=x), color=color, marker='o')
    # ax[3].set_ylim(top=102)

    # y = data['slope'].values
    # ax[4].plot(pd.Series(y, index=x), color=color, marker='o')
    # ax[4].set_ylim(top=5)

    xs = []
    ys = []
    for x in bins.keys():
        for y in bins[x]:
            xs.append(x)
            ys.append(y)
    ax[0].scatter(xs, ys)

    x1 = slopes.keys()
    y1 = slopes.values()
    ax[0].plot(pd.Series(y1, index=x1), color=color, marker='o')
    ax[0].set_xlim(0, 101)

    x2, y2 = zip(*timeline_total)
    x2 = list(reversed(x2))
    #y2 = list(reversed(y2))
    #x2, y2 = zip(*bat_model.discharge_timeline_total)
    ax[1].plot(pd.Series(y2, index=x2), color=color)
    ax[1].set_ylim(top=105)

# status = 'Charging'
# charging_hdata = filter(lambda e: e['status']==status, hdata)
# charging_bins = model.get_slopes_capacity_bins(charging_hdata)

# for i in [0.4, 0.5, 0.6]:
#     new_slopes = model.get_slopes_by_percentile(charging_bins, i)
#     new_slopes = model.extrapolate(new_slopes, 0, 100)
#     timeline = model.reconstruct_timeline(new_slopes, range(0, 100))
#     x2, y2 = zip(*timeline)

#     d = data[data['status'] == status]
#     d = d[d['slope'] != 0]
#     x = d['capacity_round']
#     y = d['slope']
#     ax.scatter(x, y)
#     x1 = new_slopes.keys()
#     y1 = new_slopes.values()
#     ax.plot(pd.Series(y1, index=x1), color='#FF0000', marker='o')
#     ax.set_xlim(0, 101)

#     # ax.plot(pd.Series(y2, index=x2), color='#FF0000', marker='+')

# ax.set_ylim(0, 101)
# ax.invert_xaxis()


# Full screen plot window.
mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())

# Show plot.
plt.show()
