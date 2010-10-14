from profiles.models import UserProfile
from issue.models import Issue
from gamelogic import actions
"""
    I wanted to proved voting for anynymous users. But once they registered i wanted their
    session votes saved as real votes. I did it with the use of some middleware.

    If you make your views save votes in the vote_history session variable with 
    { object_id , direction } key values in it. on registration their votes will be saved
    as real votes if you add this code to your middleware.

"""

class VoteHistory:
    """
    if a user did a bunch of votes when he or she was not logged in
    they should be loaded.
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.session.has_key("vote_history"):
                    self.save_votes(request, request.user, request.session["vote_history"])
                    del request.session["vote_history"]
        return None

    def save_votes(self, request, user, votes):
        """bulk load users votes to REAL saved votes.
        """
        for issue_id, direction in votes.items():
            try:
                issue = Issue.objects.get(id=issue_id)
            except Issue.DoesNotExist:
                continue
            actions.vote(user, issue, int(direction), keep_private=False)   
