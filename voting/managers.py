from django.db import models, IntegrityError
from django.db import connection
from django.db.models import Avg, Count, Sum

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

#XXX likely to change
from vote_types import votes, blank_votes, normal_votes
from vote_types import possible_votes, multiply_votes

class VoteManager(models.Manager):

    def get_for_object(self, obj):
        """
        Get queryset for votes on object
        """
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type = ctype.pk,
            object_id = obj.pk)

    def get_for_model(self, Model):
        ctype = ContentType.objects.get_for_model(Model)
        return self.filter(content_type = ctype.pk)

    def get_for_user(self, user , obj):
        """
        Get the vote made on an give object by user return None if it not exists
        """
        object_id = obj._get_pk_val()
        ctype = ContentType.objects.get_for_model(obj)
        try:
            return self.get(content_type=ctype, object_id=object_id, is_archived=False, user=user )
        except Vote.DoesNotExist:
            return None 

    def get_for_user_in_bulk(self, user, objects):
        """
        Get dictinary mapping object to vote for user on given objects.
        """
        object_ids = [o._get_pk_val() for o in objects]
        if not object_ids:
            return {}
        if not user.is_authenticated():
            return {} 

        queryset = self.filter( user=user )
        queryset = queryset.filter( is_archived=False )
        ctype = ContentType.objects.get_for_model(objects[0])
        queryset = queryset.filter(content_type=ctype, object_id__in=object_ids)
        votes = list(queryset)
        vote_dict = dict([( vote.object_id, vote ) for vote in votes ])
        return vote_dict

    def get_user_votes(self, user, Model=None, obj=None):
        """
        Get queryset for active votes by user
        """
        queryset = self.filter(user=user, is_archived=False)
        if Model:
            ctype = ContentType.objects.get_for_model(Model)
            queryset = queryset.filter(content_type=ctype,)
        if obj:
            object_id = obj._get_pk_val()
            queryset = queryset.filter(object_id=object_id)

        return queryset.order_by("-time_stamp")
    
    def get_object_votes(self, obj, all=False):
        """
        Get a dictionary mapping vote to votecount
        """
        object_id = obj._get_pk_val()
        ctype = ContentType.objects.get_for_model(obj)
        queryset = self.filter(content_type=ctype, object_id=object_id)
    
        if not all:
            queryset = queryset.filter(is_archived=False) # only pick active votes

        queryset = queryset.values('direction')
        queryset = queryset.annotate(vcount=Count("direction")).order_by()

        vote_dict = {}
        
        for count in queryset:
            if count['direction'] >= 10 : # sum up all blank votes
                vote_dict[0] = vote_dict.get(0,0) + count['vcount']
            vote_dict[count['direction']] = count['vcount']

        return vote_dict

    def get_for_objects_in_bulk(self, objects, all=False):
        """
        Get a dictinary mapping objects ids to dictinary
        which maps direction to votecount
        """
        object_ids = [o._get_pk_val() for o in objects]
        if not object_ids:
            return {}
        ctype = ContentType.objects.get_for_model(objects[0])
        queryset = self.filter(content_type=ctype, object_id__in=object_ids)

        if not all: # only pick active votes
            queryset = queryset.filter(is_archived=False) 

        queryset = queryset.values('object_id', 'direction',)
        queryset = queryset.annotate(vcount=Count("direction")).order_by()
       
        vote_dict = {}
        for votecount  in queryset:
            object_id = votecount['object_id']
            votes = vote_dict.setdefault(object_id , {})
            if votecount['direction'] >= 10:  # sum up all blank votes
                votes[0] = votes.get(0,0) + votecount['vcount']
            votes[votecount['direction']] =  votecount['vcount']

        return vote_dict

    def get_popular(self, Model, object_ids=None, reverse=False, min_tv=2):
        """ return queryset ordered by popularity 
        
            min_tv = minimum total votes, to put in a threshold.
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            queryset = queryset.filter(object_id__in=object_ids)

        queryset = queryset.values('object_id',)
        queryset = queryset.annotate(score=Count("direction")).order_by()
        queryset = queryset.filter(score__gt=min_tv) 

        if reverse:
            return queryset.order_by('score')
        return queryset.order_by('-score')
       

    def get_count(self, Model, object_ids=None, direction=1):
        """
        Find list ordered by count of votes for a direction.
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            queryset = queryset.filter(object_id__in=object_ids)
        
        queryset = queryset.values('object_id',)
        queryset = queryset.filter(direction=direction)
        queryset = queryset.annotate(score=Count("direction")).order_by()
        queryset = queryset.order_by('-score')
        
        return queryset

    def get_top(self, Model, object_ids=None, reverse=False, min_tv=1):
        """
        Find the votes which are possitive recieved.

        min_tv = minimum total votes, to put in a threshold.
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            queryset = queryset.filter(object_id__in=object_ids)

        queryset = queryset.values('object_id',)
        queryset = queryset.filter(direction__in=[-1,1])
        queryset = queryset.annotate(totalvotes=Count("direction"))
        queryset = queryset.filter(totalvotes__gt=min_tv) 
        queryset = queryset.annotate(score=Avg("direction")).order_by()
        if reverse:
            queryset = queryset.order_by('score')
        else:
            queryset = queryset.order_by('-score')
        
        return queryset

    def get_bottom(self, Model, object_ids=None, min_tv=2):
        """
        Find the votes which are worst recieved
        """
        queryset = self.get_top(Model, object_ids, reverse=True, min_tv=2)

        return queryset

    def get_controversial(self, Model, object_ids=None, min_tv=1):
        """ 
        return queryset ordered by controversy , 
        meaning it divides the ppl in 50/50.
        since for is 1 and against is -1, a score close to 0
        indicates controversy.

        this is working by aproximation and should be good enough for most cases.
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 
        queryset = queryset.filter(direction__in=[-1,1])

        if object_ids: # to get the most popular from a list
            queryset = queryset.filter(object_id__in=object_ids)
        elif min_tv > 1:
            queryset = queryset.annotate(totalvotes=Count("direction"))
            queryset = queryset.filter(totalvotes__gt=min_tv) 

        queryset = queryset.values('object_id',)
        queryset = queryset.annotate(avg=Avg("direction"))
        queryset = queryset.order_by('avg')
        queryset = queryset.filter(avg__gt= -0.3 )
        queryset = queryset.filter(avg__lt= 0.3 )
        #queryset = queryset.values_list('object_id' , 'avg')

        return queryset

    def get_for_direction(self, Model, directions=[1,-1]):
        """
        return object_ids with a specific direction. 
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 
        queryset = queryset.filter(direction__in=directions)
        queryset = queryset.values('object_id',)

        return queryset

    def record_vote(self, user, obj, direction, 
                keep_private=False, api_interface=None, 
                directions=normal_votes.keys()):
        """
        Archive old votes by switching the is_archived flag to True
        for all the previous votes on <obj> by <user>.
        And we check for and dismiss a repeated vote.
        We save old votes for research, probable interesting
        opinion changes.
        """
        if not direction in directions:
            raise ValueError('Invalid vote %s must be in %s' % (direction, directions))

        ctype = ContentType.objects.get_for_model(obj)
        votes = self.filter(user=user, content_type=ctype, object_id=obj._get_pk_val(), is_archived=False)
        votes = votes.filter(direction__in=directions)

        voted_already = False
        repeated_vote = False
        if votes:
            voted_already = True
            for v in votes:
                if direction == v.direction: #check if you do the same vote again.
                    repeated_vote = True
                else:
                    v.is_archived = True
                    v.save()            
        vote = None
        if not repeated_vote:
            vote = self.create( user=user, content_type=ctype,
                         object_id=obj._get_pk_val(), direction=direction,
                         api_interface=api_interface, is_archived=False, 
                         keep_private=keep_private
                        )
            vote.save()
        return repeated_vote, voted_already, vote

# Generic annotation code to annotate queryset from other Models with
# data from the Vote table 
# 
# NOTE: my experience is that below raw sql works but is slow.
# 
#issues = vote_annotate(issues, Vote.payload, 'vote', Sum, desc=False)
#
# more info:
#
# http://djangosnippets.org/snippets/2034/
# http://github.com/coleifer/django-simple-ratings/
#
from django.contrib.contenttypes.models import ContentType
from django.db import connection, models

def vote_annotate(queryset, gfk_field, aggregate_field, aggregator=models.Sum, desc=True):
    ordering = desc and '-vscore' or 'vscore'
    content_type = ContentType.objects.get_for_model(queryset.model)
    
    qn = connection.ops.quote_name
    
    # collect the params we'll be using
    params = (
        aggregator.name, # the function that's doing the aggregation
        qn(aggregate_field), # the field containing the value to aggregate
        qn(gfk_field.model._meta.db_table), # table holding gfk'd item info
        qn(gfk_field.ct_field + '_id'), # the content_type field on the GFK
        content_type.pk, # the content_type id we need to match
        qn(gfk_field.fk_field), # the object_id field on the GFK
        qn(queryset.model._meta.db_table), # the table and pk from the main
        qn(queryset.model._meta.pk.name)   # part of the query
    )
    
    extra = """
        SELECT %s(%s) AS aggregate_score
        FROM %s
        WHERE (
            %s=%s AND
            %s=%s.%s AND
            is_archived=FALSE AND
            "votes"."direction" IN (-1,1))
    """ % params
    
    queryset = queryset.extra(select={
        'vscore': extra
    },
    order_by=[ordering]
    )
    
    return queryset
