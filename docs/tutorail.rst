=====================
Overview and Tutorial
=====================

Welcome to GraphiteSend!

This is a quick dive in at some of the features of graphitesend.

What is GraphiteSend?
=====================

As the ``README`` says:

Graphitesend is a python library that can be used to easily push data into graphite using python.

More specifically, Graphite is:

* A common way for you to push all your metrics that your going to gather in
  python to your graphite server.

The most common usage of this is to either

- quickly put to gether a new script that is going to metrics into graphite. 
- extending an oldscript to standarize how to push metrics into graphite.


Hello, ``graphite``
===================

Very basic sending of a metric called ``hello world`` with the current value of 53.

This will make a connection to the a graphite server called (configurable) and pass the following

    >>> graphitesend.send('hello world', 45)
    systems.ubuntu.hello_world 45.000000 1386490491

As you can see ``graphitesend`` has done a few things for you..

* Added a default ``prefix`` of "systems." to make sure all your metrics land in the same namespace
* Added the ``system_name`` as the current hostname after the prefix.
* Fixed the space in the metric name
* validated and converted the value into a float
* Used the current timestamp
* Send all the above to the graphitesend on the plain text protocol, default port 2003

Sending Dicts of data
=====================

Instead of sending single metrics to the graphite server you can group them up into a ``dict`` or
``list``.

    >>> graphitesend.send_dict({'hello world': 45, 'goodbye world': 54})
    systems.ubuntu.hello_world 45.000000 1386490491
    systems.ubuntu.goodbye_world 54.000000 1386490491

As long as you keep the format of ``{metric: value}`` the data will be sent over to graphite.
   
    >>> graphitesend.send_dict(
    ...  {
    ...   'hello world': 45,
    ...   'this world': 54
    ...   'goodbye world': 54
    ...  }
    ... )

Sending lists of data
=====================

You can do the same as sending dicts however by providing a list.

    >>> graphitesend.send_list([('hello world', 45), ('goodbye world', 54))
    systems.ubuntu.hello_world 45.000000 1386490491
    systems.ubuntu.goodbye_world 54.000000 1386490491

As long as you keep the format of ``metric, value, [timestamp]`` the data will be sent over to graphite.

The optional timestamp needs to be provided in unix epoch format.
   
    >>> graphitesend.send_list(
    ...  [
    ...   ('hello world', 45),
    ...   ('this world', 54),
    ...   ('goodbye world', 54, 10000)
    ...  ]
    ... )


