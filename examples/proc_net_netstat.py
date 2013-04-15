#!/usr/bin/env python

import graphitesend

lines = open('/proc/net/netstat').readlines()

tcp_metrics = lines[0].split()[1:]
tcp_values = lines[1].split()[1:]
ip_metrics = lines[2].split()[1:]
ip_values = lines[3].split()[1:]

data_list = zip(tcp_metrics + ip_metrics, tcp_values + ip_values)

g = graphitesend.init(group='netstat.', lowercase_metric_names=True)
print g.send_list(data_list)
