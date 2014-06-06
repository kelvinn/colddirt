from django.contrib.syndication.feeds import Feed
from colddirt.dirty.models import Dirt

class LatestDirts(Feed):
    title = "Cold Dirt"
    link = "/"
    description = "When you have dirt, you've got dirt.  Right..."
    copyright = 'All Rights Unreserved'
    
    def items(self):
        return Dirt.objects.all()[:50]

class PerDirt(Feed):

    link = "/"
    copyright = 'Copyright (c) 2007, Blog Mozaic'
    
    def get_object(self, bits):
        from django.shortcuts import get_object_or_404
        if len(bits) != 1:
            raise ObjectDoesNotExist
        my_dirt = get_object_or_404(Dirt, dirtword__exact=bits[0])
        return my_dirt

    def title(self, obj):
        return obj.dirtword
    
    def description(self, obj):
        return obj.description
    
    def items(self, obj):
        from django.contrib.comments.models import FreeComment
        return FreeComment.objects.filter(object_id=obj.id).order_by('-submit_date')