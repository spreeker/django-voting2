"""
Specify all kinds of different kinds of possible votes.

this needs a more portable solution.

note: it is i18n enabled.
"""

from django.utils.translation import ugettext as _

votes = {
    -1 : _(u"Against"),
    1  : _(u"For"),
}

blank_votes = {
    # content related problems with issues:
    10 : _(u'Unconvincing'),
    11 : _(u'Not political'),
    12 : _(u'Can\'t completely agree'),
    # form related problems with issues":
    13 : _(u"Needs more work"),
    14 : _(u"Badly worded"),
    15 : _(u"Duplicate"),
    16 : _(u'Unrelated source'),
    # personal considerations:
    17 : _(u'I need to know more'),
    18 : _(u'Ask me later'),
    19 : _(u'Too personal'),
}
normal_votes = votes.copy()
normal_votes.update(blank_votes)

multiply_votes = {
    20 : _("Multiply"),
}

possible_votes = normal_votes.copy() 
possible_votes.update(multiply_votes)
