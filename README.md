graphitesend
============

Easy python bindings to write to Carbon ( Re-write of carbonclient)



Example
-------

Very basic sending of a metric called metric with a value of 45

````python
    >>> import graphitesend
    >>> graphitesend.init()
    >>> graphitesend.send('metric', 45)
    >>> graphitesend.send('metric2', 55)
````

The above would send the following metric to graphite

    system.localhostname.metric 45 epoch-time-stamp
    system.localhostname.metric2 55 epoch-time-stamp


Cleaning up the interface and using a group of cpu to alter the metric prefix

````python
    >>> import graphitesend
    >>> g = graphitesend.init(group='cpu')
    >>> g.send('metric', 45)
    >>> g.send('metric2', 55)
````

The above would send the following metric to graphite

    system.localhostname.cpu.metric 45 epoch-time-stamp
    system.localhostname.cpu.metric2 55 epoch-time-stamp


Using a different prefix (other then system.hostname)

````python
    >>> import graphitesend
    >>> g = graphitesend.init(prefix='apache.rc')
    >>> g.send('404', 4)
    >>> g.send('200', 500)
````

The above would send the following metric to graphite

    apache.rc.404 4 epoch-time-stamp
    apache.rc.200 500 epoch-time-stamp


Sending a dict()

````python
    >>> import graphitesend
    >>> g = graphitesend.init()
    >>> g.send_dict({'metric': 45, 'metric2': 55})
````

installing
----------

*pip*

````sh
$ pip install graphitesend
````

or

*source*

````sh
$ git clone git://github.com/daniellawrence/graphitesend.git
$ cd graphitesend
$ python ./setup.py install
````



Porcelain Overview
==================

init
-----  
Create the module instance of GraphiteSend.

send
-----
Make sure that we have an instance of the GraphiteClient. 
Then send the metrics to the graphite server.

send_dict
---------
Make sure that we have an instance of the GraphiteClient.
Then send the metrics to the graphite server.

reset
-----
Disconnect from the graphite server and destroy the module instance.


