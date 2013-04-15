#!/usr/bin/env python
import graphitesend

g = graphitesend.init(group='meminfo.', suffix='_mb',
                      lowercase_metric_names=True)
data = []
for line in open('/proc/meminfo').readlines():
    bits = line.split()

    # We dont care about the pages.
    if len(bits) == 2:
        continue

    # remove the : from the metric name
    metric = bits[0]
    metric = metric.replace(':', '')

    # Covert the default kb into mb
    value = int(bits[1])
    value = value / 1024

    data.append((metric, value))

print g.send_list(data)
