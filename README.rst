

django-voting2
--------------

This app is heavily derived from the django-voting app.
which can be found here::

    http://code.google.com/p/django-voting/

I need to create an overview file like this one::

    http://django-voting.googlecode.com/svn/trunk/docs/overview.txt

This app is really close to the original django-voting but improved in a few ways:

- Support more vote types.I added support for many more votes types,
easy changable by editing voting/vote_types.py
Now not only up and down votes but any kind of vote is supported.
In voting/vote_types.py you can see current supported vote_types which you can and 
should change for you needs.
- No more raw sql The origingal code contained raw sql. The newer ORM has support fro aggegration
- More managers functions, like get controversial which looks op
voted objects which are spliting up the community.
- many small code clean ups, more consistens functions arguments
- small but neccesairy changes to the template tags.

TODO
====

Make this a better package.. a better name maybe?
if you find this code usefull don't hessitate to let me know.
