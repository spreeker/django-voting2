r"""
# to exectute these tests:
# python manage.py test tests --settings=voting.tests.settings
#
>>> from django.contrib.auth.models import User
>>> from voting.models import Vote
>>> from voting.tests.models import Item

##########
# Voting #
##########

# Basic voting ###############################################################

>>> i1 = Item.objects.create(name='i1')
>>> users = []
>>> for username in ['u1', 'u2', 'u3', 'u4']:
...     users.append(User.objects.create_user(username, '%s@test.com' % username, 'test'))
>>> Vote.objects.get_object_votes(i1)
{}
>>> Vote.objects.record_vote(users[0], i1, 1)
(False, False, <Vote: 1 on i1  by u1>)
>>> Vote.objects.get_object_votes(i1)
{1: 1}
>>> _, _, _ = Vote.objects.record_vote(users[0], i1, -1)
>>> Vote.objects.get_object_votes(i1)
{-1: 1}
>>> for user in users:
...     _, _, _ = Vote.objects.record_vote(user, i1, +1)
>>> Vote.objects.get_object_votes(i1)
{1: 4}
>>> for user in users[:2]:
...     _,_,_ = Vote.objects.record_vote(user, i1, 10)
>>> Vote.objects.get_object_votes(i1)
{0: 2, 1: 2, 10: 2}
>>> for user in users[:2]:
...     _,_,_ = Vote.objects.record_vote(user, i1, -1)
>>> i2 = Item.objects.create(name='i2')
>>> _,_,_ = Vote.objects.record_vote(users[0], i2, 10)
>>> Vote.objects.get_object_votes(i1)
{1: 2, -1: 2}
>>> try:
...     Vote.objects.record_vote(i1, user, -2)
... except ValueError: 
...     pass

# Retrieval of votes #########################################################

>>> i3 = Item.objects.create(name='i3')
>>> i4 = Item.objects.create(name='i4')
>>> _,_,_ = Vote.objects.record_vote( users[0], i2, +1)
>>> _ = Vote.objects.record_vote(users[0], i3, -1)
>>> _ = Vote.objects.record_vote(users[0], i4, 11)
>>> vote = Vote.objects.get_for_user(users[0], i2)
>>> (vote.direction)
1
>>> vote = Vote.objects.get_for_user(users[0], i3 )
>>> (vote.direction)
-1
>>> vote = Vote.objects.get_for_user(users[0], i4)
>>> vote.direction
11

## In bulk

>>> votes = Vote.objects.get_for_user_in_bulk(users[0], [i1, i2, i3, i4])
>>> [(id, vote.direction) for id, vote in votes.items()]
[(1, -1), (2, 1), (3, -1), (4, 11)]
>>> Vote.objects.get_for_user_in_bulk(users[0], [])
{}

>>> for user in users[1:]:
...     _ = Vote.objects.record_vote(user, i2, +1)
...     _ = Vote.objects.record_vote(user, i3, +1)
...     _ = Vote.objects.record_vote(user, i4, +1)

>>> votes = Vote.objects.get_for_user_in_bulk(users[1], [i1, i2, i3, i4])
>>> [(id, vote.direction) for id, vote in votes.items()]
[(1, -1), (2, 1), (3, 1), (4, 1)]

>>> Vote.objects.get_for_objects_in_bulk([i1, i2, i3, i4])
{1: {1: 2, -1: 2}, 2: {1: 4}, 3: {1: 3, -1: 1}, 4: {0: 1, 1: 3, 11: 1}}
>>> Vote.objects.get_for_objects_in_bulk([])
{}

# Popular #################################################

[(1, 4), (2, 4), (3, 4), (4, 4), (6, 2), (5, 1)]
>>> qs = Vote.objects.get_controversial(Item, min_tv=2)
>>> qs.values_list('object_id' , 'avg')
[(1, 0.0)]
>>> qs = Vote.objects.get_top(Item)
>>> qs.values_list('object_id' , 'score')
[(2, 1.0), (4, 1.0), (3, 0.5), (1, 0.0)]
>>> qs = Vote.objects.get_count(Item)
>>> qs.values_list('object_id' , 'score')
[(2, 4), (3, 3), (4, 3), (1, 2)]
"""
