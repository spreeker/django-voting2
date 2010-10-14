from django.contrib import admin

from models import Vote

class VoteAdmin(admin.ModelAdmin):
    date_hierarchy = "time_stamp"
    list_display = ('vote', 'user', 'time_stamp')
    list_filter = ('user', 'time_stamp', )

admin.site.register(Vote, VoteAdmin)
