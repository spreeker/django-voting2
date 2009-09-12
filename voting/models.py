"""
This is the core of the democracy voting system. 
The Vote model in this module can be generically 
linked to anything that users whould be able to vote
on.

This module implements:
-voting database interactions

Note that game rules should not be added to this module.
"""

from datetime import datetime
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from piston.models import Consumer

from voting.managers import VoteManager 
from voting.managers import possible_votes

class Vote(models.Model):
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField() 
    payload = generic.GenericForeignKey('content_type', 'object_id')

    vote = models.IntegerField(choices = possible_votes.items() )
    time_stamp = models.DateTimeField(editable = False , default=datetime.now )
    # optional **kwargs
    is_archived = models.BooleanField(default = False)
    keep_private = models.BooleanField(default = False)
    api_interface = models.IntegerField(null=True , blank=True) #key naar oauth consumer 
   
    objects = VoteManager()

    def __unicode__(self):
        return unicode(self.vote) + u" on \"" + str(self.payload) + u"\" by " + self.user.username

    class Meta:
        db_table = 'votes'

