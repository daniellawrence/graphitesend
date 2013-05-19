graphitesend
============

Easy python bindings to write to Carbon ( Re-write of carbonclient).


Build status
-------------
[![Build Status](https://travis-ci.org/daniellawrence/graphitesend.png)](https://travis-ci.org/daniellawrence/graphitesend)

Blog posts
-----------
[dansysadm.com](http://dansysadm.com/blog/sending_data_to_graphte_from_python.html)

Example Scripts
----------------
The github repo of [graphitesend-examples](https://github.com/daniellawrence/graphitesend-examples)
has lots of examples using graphitesend to grab data from your local linux system.


Usage Example
--------------

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

Sending a list()

````python
    >>> import graphitesend
    >>> g = graphitesend.init()
    >>> g.send_list([('metric', 45), ('metric2', 55)])
````

Sending a list(), with a custom timestamp for all metric-value pairs

````python
    >>> import graphitesend
    >>> g = graphitesend.init()
    >>> g.send_list([('metric', 45), ('metric2', 55)], timestamp=12345)
````

Sending a list(), with a custom timestamp for each metric-value pairs

````python
    >>> import graphitesend
    >>> g = graphitesend.init()
    >>> g.send_list([('metric', 45, 1234), ('metric2', 55, 1234)])
````

Learning? Use dryrun.
----------------------

With dryrun enabled the data will never get sent to a remote service, it will
just print out what would have been sent.

````python
    >>> import graphitesend
    >>> g = graphitesend.init(dryrun=True)
    >>> g.send_list([('metric', 45, 1234), ('metric2', 55, 1234)])
````

Example: the init()
----------------

Set a metric prefix (Default arg)
````python
>>> g = graphitesend.init('prefix')
>>> print g.send('metric', 1)
sent 34 long message: prefix.metric 1.000000 1365068929
````

set a metric prefix using kwargs
````python
>>> g = graphitesend.init(prefix='prefix')
>>> print g.send('metric', 2)
sent 34 long message: prefix.metric 2.000000 1365068929
````
 
view the default prefix, hardset systems. then followed by the name of the
host that execute the send().
````python
>>> g = graphitesend.init()
>>> print g.send('metric', 3)
sent 44 long message: systems.<system_name>.metric 3.000000 1365069029
````

Set a suffix, handy if you have a bunch of timers or percentages
````python
>>> g = graphitesend.init(suffix='_ms')
>>> print g.send('metric', 4)
sent 47 long message: systems.<system_name>.metric_ms 4.000000 1365069100
````

set a system_name if your submitting results for a different system
````python
>>> g = graphitesend.init(system_name='othersystem')
>>> print g.send('metric', 5)
sent 47 long message: systems.othersystem.metric 5.000000 1365069100
````

Lowercase all the metric names that are send to the graphite server.
````python
>>> g = graphitesend.init(lowercase_metric_names=True)
>>> print g.send('METRIC', 6)
sent 47 long message: systems.<hostname>.metric 6.000000 1365069100
````


Set a group name, handy if you just parsed iostat and want to prefix all the 
metrics with iostat, after its already in the <system_name> directory.
````python
>>> g = graphitesend.init(group='groupname')
>>> print g.send('metric', 6)
sent 54 long message: systems.<system_name>.groupname.metric 6.000000 136506924
````

Connect to a different graphite server
````python
>>> graphitesend.init(graphite_server='graphite.example.com')
````

Connect to a different graphite server port
````python
>>> graphitesend.init(graphite_port=2003)
````




CLI
------------

Just added -- A cli script that allows for anything to send metrics over to 
graphite (not just python).

The usage is very simple you need to give the command a metric and a value.

````sh
	$ graphitesend name.of.the.metric 666
````

Send more\* then 1 metric and value

````sh
	$ graphitesend name.of.the.metric 666
	$ graphitesend name.of.the.other_metric 2
````

\* Call it 2 times ;)

Installing
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


TCP vs UDP
==========

There is a new branch for UDP support called 'udp and tcp'.
TCP will continue to be the default with UDP as an option
