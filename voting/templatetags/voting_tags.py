from django import template
from django.utils.html import escape

from voting.models import Vote
from voting.managers import possible_votes


register = template.Library()

class VoteByUserNode(template.Node):
    def __init__(self, user, object, context_var):
        self.user = user
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            user = template.resolve_variable(self.user, context)
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = Vote.objects.get_for_user(user, object)
        return ''

class VotesByUserNode(template.Node):
    def __init__(self, user, objects, context_var):
        self.user = user
        self.objects = objects
        self.context_var = context_var
    #TODO if anonymous get votes from session 
    def render(self, context):
        try:
            user = template.resolve_variable(self.user, context)
            objects = template.resolve_variable(self.objects, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = Vote.objects.get_for_user_in_bulk(user, objects)
        return ''

class VotesForObjectNode(template.Node):
    def __init__(self, object, context_var):
        self.object = object
        self.context_var = context_var

    def render(self, context):
        try:
            object = template.resolve_variable(self.object, context)
        except template.VariableDoesNotExist:
            return ''

        vote_counts = Vote.objects.get_object_votes(object)
        votes = dict.fromkeys( possible_votes.keys , 0 ) 
        votes.update(vote_counts)
        context[self.context_var] = votes 
        return ''

class VotesForObjectsNode(template.Node):
    def __init__(self, objects, context_var):
        self.objects = objects
        self.context_var = context_var

    def render(self, context):
        try:
            objects = template.resolve_variable(self.objects, context)
        except template.VariableDoesNotExist:
            return ''
        
        counts_on_objects = Vote.objects.get_for_objects_in_bulk(objects)

        for object_id in counts_on_objects.keys(): 
            # all vote types default to 0.
            vote_counts = dict.fromkeys(possible_votes.keys(), 0)
            vote_counts.update(counts_on_objects[object_id])
            vote_counts[2] = vote_counts[-1] # we cannot index -1 in templates.
            vote_counts.pop(-1)
            counts_on_objects[object_id] = vote_counts

        context[self.context_var] = counts_on_objects 
        return ''

class DictEntryForItemNode(template.Node):
    def __init__(self, item, dictionary, context_var):
        self.item = item
        self.dictionary = dictionary
        self.context_var = context_var

    def render(self, context):
        try:
            dictionary = template.resolve_variable(self.dictionary, context)
            item = template.resolve_variable(self.item, context)
        except template.VariableDoesNotExist:
            return ''
        context[self.context_var] = dictionary.get(item.id, None)
        return ''


def get_vote_by_user(parser, token):
    """
    Retrieves the ``Vote`` cast by a user on a particular object and
    stores it in a context variable. If the user has not voted, the
    context variable will be ``None``.

    Example usage::

        {% vote_by_user user on widget as vote %}
    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("'%s' tag takes exactly five arguments" % bits[0])
    if bits[2] != 'on':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'on'" % bits[0])
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    return VoteByUserNode(bits[1], bits[3], bits[5])

def get_votes_by_user(parser, token):
    """
    Retrieves the votes cast by a user on a list of objects as a
    dictionary keyed with object ids and stores it in a context
    variable.

    Example usage::

        {% votes_by_user user on widget_list as vote_dict %}
    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("'%s' tag takes exactly four arguments" % bits[0])
    if bits[2] != 'on':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'on'" % bits[0])
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    return VotesByUserNode(bits[1], bits[3], bits[5])

def get_vote_counts_for_object(parser, token):
    """
    Retrieves number of votes for an object
    it's received and stores them in a context variable which has
    ``vote`` and ``num_votes`` properties.

    Example usage::

        {% vote_counts_for_object widget as votes %}

        {{ score.score }}point{{ score.score|pluralize }}
        after {{ score.num_votes }} vote{{ score.num_votes|pluralize }}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return VotesForObjectNode(bits[1], bits[3])

def get_vote_counts_for_objects(parser, token):
    """
    Retrieves the total vote count for a list of objects and the number of
    votes they have received and stores them in a context variable.

    Example usage::

        {% vote_counts_for_objects widget_list as vote_dict %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("'%s' tag takes exactly three arguments" % bits[0])
    if bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'as'" % bits[0])
    return VotesForObjectsNode(bits[1], bits[3])

def get_dict_entry_for_item(parser, token):
    """
    Given an object and a dictionary keyed with object ids - as
    returned by the ``votes_by_user`` and ``vote_counts_for_objects``
    template tags - retrieves the value for the given object and
    stores it in a context variable, storing ``None`` if no value
    exists for the given object.

    Example usage::

        {% dict_entry_for_item widget from vote_dict as vote %}
    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise template.TemplateSyntaxError("'%s' tag takes exactly five arguments" % bits[0])
    if bits[2] != 'from':
        raise template.TemplateSyntaxError("second argument to '%s' tag must be 'from'" % bits[0])
    if bits[4] != 'as':
        raise template.TemplateSyntaxError("fourth argument to '%s' tag must be 'as'" % bits[0])
    return DictEntryForItemNode(bits[1], bits[3], bits[5])


register.tag('vote_by_user', get_vote_by_user)
register.tag('votes_by_user', get_votes_by_user)
register.tag('dict_entry_for_item', get_dict_entry_for_item)
register.tag('vote_counts_for_object', get_vote_counts_for_object)
register.tag('vote_counts_for_objects', get_vote_counts_for_objects)

# Filters

def vote_display(vote):
    """
    Given a string mapping values for up and down votes, returns one
    of the strings according to the given ``Vote``:

    Example usage::

        {{ vote|vote_display }}
    """
    vote = vote if vote != 2 else -1 # dealing with the -1 case.
    return possible_votes[vote] 

register.filter(vote_display)


