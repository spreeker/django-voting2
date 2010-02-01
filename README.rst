
django-voting2
==============

This app is heavily derived from the django-voting app.
which can be found here::

    http://code.google.com/p/django-voting/

I need to create an overview file like this one::

    http://django-voting.googlecode.com/svn/trunk/docs/overview.txt

This app is close to the original django-voting but improved in a few ways:

Support for more vote types.
  I added support for many more votes types, easy changeable by editing voting/vote_types.py 
  Now not only up and down votes but any kind of vote is supported. 

No more raw sql 
  The original code contained raw sql. The newer django ORM has support for aggregation

More managers functions 
  like get controversial which looks op voted objects which are splitting up the community.

many small code clean ups, 
  more consistent functions arguments, small but necessarily changes to the template tags.


TODO
====

Make this a better package.. a better name maybe?
if you find this code useful don't hesitate to let me know.
