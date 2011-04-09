from django.contrib import admin

from models import Vote

class VoteAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('direction', 'issue_title', 'user', 'time_stamp')
    list_filter = ('user', 'time_stamp', )

    def issue_title(self , obj):
        return ("%s" % obj.payload.title) 
    
admin.site.register(Vote, VoteAdmin)
