from django.db import models, IntegrityError
from django.db import connection
from django.db.models import Avg, Count, Sum

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

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

    def get_user_votes(self, user, obj=None):
        """
        Get queryset for active votes by user
        """
        return self.filter(user=user, is_archived=False).order_by("-time_stamp")
    
    def get_for_object(self, obj, all=False):
        """
        Get a dictionary mapping vote to votecount
        """
        object_id = obj._get_pk_val()
        ctype = ContentType.objects.get_for_model(obj)
        queryset = self.filter(content_type=ctype, object_id=object_id)
    
        if not all:
            queryset = queryset.filter(is_archived=False) # only pick active votes

        queryset = queryset.values('vote')
        queryset = queryset.annotate(vcount=Count("vote")).order_by()

        vote_dict = {}
        
        for count in queryset:
            if count['vote'] >= 10 : # sum up all blank votes
                vote_dict[0] = vote_dict.get(0,0) + count['vcount']
            vote_dict[count['vote']] = count['vcount']

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

        queryset = queryset.values('object_id', 'vote',)
        queryset = queryset.annotate(vcount=Count("vote")).order_by()
       
        vote_dict = {}
        for votecount  in queryset:
            object_id = votecount['object_id']
            votes = vote_dict.setdefault(object_id , {})
            if votecount['vote'] >= 10:  # sum up all blank votes
                votes[0] = votes.get(0,0) + votecount['vcount']
            votes[votecount['vote']] =  votecount['vcount']

        return vote_dict

    def get_popular(self, Model, object_ids=None):
        """ return qs ordered by popularity """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 

        if object_ids: # to get the most popular from a list
            queryset = queryset.filter(object_id__in=object_ids)

        queryset = queryset.values('object_id',)
        queryset = queryset.annotate(totalvotes=Count("vote")).order_by()
        queryset = queryset.order_by('-totalvotes')
        #queryset = queryset.values_list('object_id' , 'totalvotes')
       
        return queryset

    def get_controversial(self, Model, object_ids=None):
        """ 
        return qs ordered by controversy , 
        meaning it divides the ppl in 50/50.
        since for is 1 and against is -1, a score close to 0
        indicates controversy.
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 
        queryset = queryset.filter(vote__in=[-1,1])

        if object_ids: # to get the most popular from a list
            queryset = queryset.filter(object_id__in=object_ids)

        queryset = queryset.values('object_id',)
        queryset = queryset.annotate(avg=Avg("vote")).order_by()
        queryset = queryset.order_by('avg')
        queryset = queryset.filter(avg__gt= -0.3 )
        queryset = queryset.filter(avg__lt= 0.3 )
        #queryset = queryset.values_list('object_id' , 'avg')

        return queryset

    def get_for_direction(self, Model, directions=[1,-1]):
        """
        return objects with a specific direction for ...
        TODO
        """
        ctype = ContentType.objects.get_for_model(Model)
        queryset = self.filter(content_type=ctype,)
        queryset = queryset.filter(is_archived=False) 
        queryset = queryset.filter(vote__in=directions)

        return queryset

    def record_vote(self, user, obj, direction, keep_private=False, api_interface=None):
        """
        Archive old votes by switching the is_archived flag to True
        for all the previous votes on <obj> by <user>.
        And we check for and dismiss a repeated vote.
        We save old votes for research, probable interesting
        opinion changes.
        """
        if not direction in possible_votes.keys():
            raise ValueError('Invalid vote %s must be in %s' % (direction, possible_votes.keys()))

        ctype = ContentType.objects.get_for_model(obj)
        votes = self.filter(user=user, content_type=ctype, object_id=obj._get_pk_val(), is_archived=False)

        voted_already = False
        repeated_vote = False
        if votes:
            voted_already = True
            for v in votes:
                if direction == v.vote: #check if you do the same vote again.
                    repeated_vote = True
                else:
                    v.is_archived = True
                    v.save()            
        vote = None
        if not repeated_vote:
            vote = self.create( user=user, content_type=ctype,
                         object_id=obj._get_pk_val(), vote=direction,
                         api_interface=api_interface, is_archived=False, 
                         keep_private=keep_private
                        )
            vote.save()
        return repeated_vote, voted_already, vote
