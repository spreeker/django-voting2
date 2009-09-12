

django-voting2
--------------

This app is derived from the django-voting app.

It is improved in a few ways:

-Support more vote types.
I added support for many more votes types,
easy changable by editing voting/vote_types.py
Now not only up and down votes but any kind of vote is supported.
It is stored as an integer
In the vote_types.py you can see i needed extensive support for blank vote types.

-No more raw sql
The origingal code contained raw sql. The newer ORM has support fro aggegration
which i thanfully use.

-More managers functions, like get controversial which looks op
 voted objects which are spliting up the community.

-many small code clean ups.
-small but neccesairy changes to the template tags.

TODO

Make this a better package.. a better name maybe?
if you find this code use full dont hessitate to let me know.
