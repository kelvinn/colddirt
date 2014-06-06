from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.template import RequestContext
from django.views.generic import list_detail
from django.http import Http404, HttpResponseRedirect
from colddirt.dirty.models import *
from colddirt.forms import *
import datetime, colddirt.captcha

def live_update(request):
    from django.http import HttpResponse
    from django.core import serializers
    # To get my designed feature set, plus not kill the load 
    # on my server, this is all a bit hackery.  If you see
    # a better way to handle it, *especially* the JS, let
    # me know!
    if request.method == 'GET':
        new_pk = request.GET.get('pk')
        if new_pk:
            data = serializers.serialize("json", Dirt.objects.filter(pk__gte=new_pk).order_by('-publish_date')[:10])
    return HttpResponse(data, mimetype='application/json') 

def dirt_count(request):
    from django.http import HttpResponse
    countd = str(Dirt.objects.all().count())
    return HttpResponse(countd, mimetype='text/plain')

def live(request):
    dirt_form = DirtyForm()
    html_captcha = colddirt.captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    return render_to_response("dirty/live_dirt.html", {
                                "form": dirt_form.as_ul(),
                                'html_captcha': html_captcha})
    
def index(request):
    import re
    from django.template.defaultfilters import slugify
    # I display the form on every page, so I don't need an if/else here.  However, You would normall put the below two lines after an else:
    dirt_form = DirtyForm()
    html_captcha = colddirt.captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    if request.method == 'POST':
        check_captcha = colddirt.captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            # Captcha is wrong show a error ...
            return render_to_response('dirty/dirt_list.html',
                                      { 'form': dirt_form.as_ul(),
                                       'html_captcha': html_captcha,
                                       'errorlist_captcha': True},
                                      context_instance=RequestContext(request))
        dirt_form = DirtyForm(request.POST)
        if dirt_form.is_valid():
            # I opted not to create an m2m relationship for several
            # reasons. Note: the latest_word is some random word.
            latest_word = Word.objects.filter(is_taken__exact=False).order_by('?')[:1]            
            latest_word[0].is_taken=True
            latest_word[0].save()
            new_dirt = Dirt(description=dirt_form.cleaned_data['description'],
                            dirtword=latest_word[0].dirtyword)
            new_dirt.save()
            # Credit for the tag parsing goes to Ubernostrum (James B)
            # from the Cab (great for learning!) project
            # I opted to not store tag_list in each entry
            # Splitting to get the new tag list is tricky, because people
            # will stick commas and other whitespace in the darndest places.
            new_tag_list = [t for t in re.split('[\s,]+', dirt_form.cleaned_data['tag_list']) if t]
            # Now add the tags
            for tag_name in new_tag_list:
                tag, created = Tagling.objects.get_or_create(name=slugify(tag_name), slug=slugify(tag_name))
                new_dirt.tags.add(tag)
            return HttpResponseRedirect(new_dirt.get_absolute_url())
    return list_detail.object_list(
           request,
           queryset = Dirt.objects.order_by('?')[:100],
           template_name = "dirty/dirt_list.html",
           template_object_name = "dirty",
           paginate_by = 10,
           extra_context = {'form': dirt_form.as_ul(),
                            'html_captcha': html_captcha},
        )

def submit(request):
    import re
    from django.template.defaultfilters import slugify
    dirt_form = DirtyForm()
    html_captcha = colddirt.captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    if request.method == 'POST':
        check_captcha = colddirt.captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            # Captcha is wrong show a error ...
            return render_to_response('dirty/dirt_list.html',
                                      { 'form': dirt_form.as_ul(),
                                       'html_captcha': html_captcha,
                                       'errorlist_captcha': True},
                                      context_instance=RequestContext(request))
        dirt_form = DirtyForm(request.POST)
        if dirt_form.is_valid():
            # I opted not to create an m2m relationship for several
            # reasons. Note: the latest_word is some random word.
            latest_word = Word.objects.filter(is_taken__exact=False).order_by('?')[:1]            
            latest_word[0].is_taken=True
            #latest_word[0].save()
            new_dirt = Dirt(description=dirt_form.cleaned_data['description'],
                            dirtword=latest_word[0].dirtyword)
            new_dirt.save()
            # Credit for the tag parsing goes to Ubernostrum (James B)
            # from the Cab (great for learning!) project
            # I opted to not store tag_list in each entry
            # Splitting to get the new tag list is tricky, because people
            # will stick commas and other whitespace in the darndest places.
            new_tag_list = [t for t in re.split('[\s,]+', dirt_form.cleaned_data['tag_list']) if t]
            # Now add the tags
            for tag_name in new_tag_list:
                tag, created = Tagling.objects.get_or_create(name=slugify(tag_name), slug=slugify(tag_name))
                new_dirt.tags.add(tag)
            return HttpResponseRedirect(new_dirt.get_absolute_url())
    return render_to_response('dirty/dirt_list.html',
                              { 'form': dirt_form.as_ul(),
                               'html_captcha': html_captcha},
                              context_instance=RequestContext(request))
    
def tag_list(request, slug):
    dirts = Dirt.objects.filter(tags__slug__iexact=slug)
    html_captcha = colddirt.captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    return list_detail.object_list(
           request,
           queryset = dirts,
           template_name = "dirty/dirt_list.html",
           template_object_name = "dirty",
           paginate_by = 25,
           extra_context = {'form': DirtyForm().as_ul(),
                            'html_captcha': html_captcha,
                            'tag_search': slug }
        )  
    
def search(request):
    from django.db.models import Q
    q = request.GET.get("q", "")
    if q and len(q) >= 3:
        clause = Q(dirtword__icontains=q)               \
               | Q(description__icontains=q)       \
               | Q(tags__name__icontains=q)        
        site_search = Dirt.objects.filter(clause).distinct()
    else:
        site_search = Dirt.objects.order_by('?')[:100]
    return list_detail.object_list(
        request              = request,
        queryset             = site_search,
        template_name        = "dirty/search.html",
        template_object_name = "dirty",
        paginate_by          = 20,
        extra_context        = {"q" : q},
    )    

def tag_cloud(request):
    #make tag cloud
    populartags = Tagling.objects.popular_tags()
    maxtags = []
    for tag in populartags:
        maxtags.append(tag.tagcount)
    #we need max count for the tagcloud
    maxtagcount = max(maxtags)
    html_captcha = colddirt.captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
    return render_to_response("dirty/tag_cloud.html", {
                                "populartags" : populartags,
                                "maxtagcount" : maxtagcount,
                                'html_captcha': html_captcha,
                                'form': DirtyForm().as_ul()})

def huh(request, template="dirty/huh.html",redirect_to="/"):
    from django.core.mail import send_mail
    contact_form = ContactForm()
    user = request.user
    description = ''
    status = ''
    subject = ''
    from_email = ''
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            description = contact_form.cleaned_data['description']
            status = contact_form.cleaned_data['status']
            subject = contact_form.cleaned_data['subject']
            from_email = contact_form.cleaned_data['from_email'] 
            send_mail('Cold Dirt ' + subject,
                      'Type: ' + status + description,
                      from_email,
                      ['kelvin@kelvinism.com'], fail_silently=True)
    return render_to_response(template, {'contact_form':contact_form.as_ul(),
                                      'description': description,
                                      'status': status,
                                      'subject': subject,
                                      'from_email': from_email,
                                      'user': user})

def report(request, report_id):
    # This is super ghetto, but works for now
    new_report = Report(item=report_id)
    new_report.save()
    return HttpResponseRedirect("/reported/success/")