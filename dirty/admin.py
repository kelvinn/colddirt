from django.contrib import admin
from colddirt.dirty.models import Tagling, Report, Word, Dirt

class TaglingAdmin(admin.ModelAdmin):
    ordering = ['name']
    
class ReportAdmin(admin.ModelAdmin):
    ordering = ['item']

class WordAdmin(admin.ModelAdmin):
    ordering = ['dirtyword']

class DirtAdmin(admin.ModelAdmin):
    list_display   = ('dirtword', 'publish_date',)
    list_filter    = ('publish_date',)
    ordering       = ('-publish_date',)
    search_fields  = ('slug', 'description',)