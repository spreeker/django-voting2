from django.contrib import admin

from issue.models import Issue
from models import Vote

class IssueAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('title', 'time_stamp', 'user', 'votes' ) 
    list_filter = ('title', 'time_stamp', 'user', 'votes' )

    def votes(self , obj):
        return Vote.objects.get_for_object(obj).count()

class VoteAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('vote', 'issue_title', 'user', 'time_stamp')
    list_filter = ('user', 'time_stamp', )

    def issue_title(self , obj):
        return ("%s" % obj.payload.title) 
    
admin.site.register(Issue , IssueAdmin)
admin.site.register(Vote, VoteAdmin)
