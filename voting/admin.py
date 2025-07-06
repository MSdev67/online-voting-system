# voting/admin.py
from django.contrib import admin
from .models import Election, Party, Candidate, Voter, Vote

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active')
    list_filter = ('start_time', 'end_time')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'election')
    list_filter = ('party', 'election')

admin.site.register(Party)
admin.site.register(Voter)
admin.site.register(Vote)