from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.views.generic import list_detail
from django.views.decorators.cache import cache_page
from colddirt.dirty.models import Dirt, Word
from colddirt.dirty import views
from colddirt.feeds import LatestDirts, PerDirt
from colddirt.forms import *
import captcha

rand_dict = {
    'queryset': Dirt.objects.order_by('?')[:250],
    'template_object_name' : 'dirty',
    'paginate_by': 15,
    'extra_context': {'form': DirtyForm().as_ul(),
                      'html_captcha': captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)}
}  

newdirt_dict = {
    'queryset': Dirt.objects.order_by('-publish_date')[:250],
    'template_object_name' : 'dirty',
    'paginate_by': 15,
    'extra_context': {'form': DirtyForm().as_ul(),
                      'html_captcha': captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)}
} 

word_dict = {
    'queryset': Dirt.objects.all(), 
    'template_object_name' : 'dirt_object',
    'extra_context': {'form': DirtyForm().as_ul(),
                      'html_captcha': captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)}
}

sitemaps = {
    'flatpages': FlatPageSitemap,
    'dirtwords': GenericSitemap(newdirt_dict, priority=0.5),
}

feeds = {
    'newdirt': LatestDirts,
    'mydirt': PerDirt,
}

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', cache_page(views.index)),
    (r'dirtword/(?P<slug>[-\w]+)/$', 'django.views.generic.list_detail.object_detail', dict(word_dict, slug_field="dirtword", template_name="dirty/dirt_detail.html")),
    (r'tag/(?P<slug>[-\w]+)/$', cache_page(views.tag_list)),
    (r'tag/$', cache_page(views.tag_cloud)),
    (r'newest/$', 'django.views.generic.list_detail.object_list', dict(newdirt_dict)),
    (r'random/$', 'django.views.generic.list_detail.object_list', dict(rand_dict)),
    (r'yourdirt/$', cache_page(views.index)),
    (r'^search/$', cache_page(views.search)),
    (r'^huh/$', cache_page(views.huh)),
    (r'^live_update/.*', views.live_update),
    (r'^dirt_count/$', views.dirt_count),
    (r'^live/$', views.live),
    (r'^submit/$', views.submit),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^report/(?P<report_id>[-\w]+)/$', views.report),
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^admin/(.*)', admin.site.root),
)
