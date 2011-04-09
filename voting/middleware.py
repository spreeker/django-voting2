from profiles.models import UserProfile
from issue.models import Issue
from gamelogic import actions
import logging

class VoteHistory:
    """
    if a user did a bunch of votes when he or she was not logged in
    they should be loaded.
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.session.has_key("vote_history"):
                    vote_history = request.session["vote_history"]
                    del request.session["vote_history"]
                    self.save_votes(request, request.user, vote_history)
        return None

    def save_votes(self, request, user, votes):
        """bulk load users votes to REAL saved votes.
        """
        for issue_id, direction in votes.items():
            try:
                issue = Issue.objects.get(id=issue_id)
            except Issue.DoesNotExist:
                continue
            try:
                actions.vote(user, issue, int(direction), keep_private=False)   
            except ValueError:
                #wrong direction code.
                pass
