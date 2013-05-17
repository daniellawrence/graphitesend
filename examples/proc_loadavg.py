#!/usr/bin/env python
import time
import graphitesend
# comments
g = graphitesend.init(group='loadavg_', suffix='min')

while True:
    (la1, la5, la15) = open('/proc/loadavg').read().strip().split()[:3]
    print g.send_dict({'1': la1, '5': la5, '15': la15})
    time.sleep(1)
