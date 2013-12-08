Graphitesend is a python library that can be used to easily push data into graphite using python.


.. graphviz::

   digraph foo {
       "bar" -> "baz";
   }


Usage Example
-------------

Very basic sending of a metric called metric with a value of 45

    >>> import graphitesend
    >>> graphitesend.init()
    >>> graphitesend.send('metric', 45)
    >>> graphitesend.send('metric2', 55)

The above would send the following metric to graphite over the plaintext (default) protocol on port 2003 (default)

::

    system.localhostname.metric  45 epoch-time-stamp
    system.localhostname.metric2 55 epoch-time-stamp

Cleaning up the interface and using a group of cpu to alter the metric prefix

    >>> import graphitesend
    >>> g = graphitesend.init(group='cpu')
    >>> g.send('metric', 45)
    >>> g.send('metric2', 55)

The above would send the following metric to graphite

::

    system.localhostname.cpu.metric 45 epoch-time-stamp
    system.localhostname.cpu.metric2 55 epoch-time-stamp


Using graphitesend from the commandline
=======================================

A cli script that allows for anything to send metrics over to 
graphite (not just python).

The usage is very simple you need to give the command a metric and a value.

	
::
 
    $ graphitesend name.of.the.metric 666

Send more\* then 1 metric and value

::

    $ graphitesend name.of.the.metric 666
    $ graphitesend name.of.the.other_metric 2



Example Scripts using graphitesend
==================================

The github repo of https://github.com/daniellawrence/graphitesend-examples
has lots of examples using graphitesend to grab data from your local linux system.
