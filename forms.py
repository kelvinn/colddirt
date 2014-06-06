from django import forms
from colddirt import settings

CONTACT_TYPES = (
    ('hate', 'Hate Mail'),
    ('comment', 'General Comment'),
    ('press', 'Press'),
    ('techissue', 'Technical Problem'),
)

attrs_dict = { 'class': 'norm_required' }
textbox_dict = { 'class': 'text_required' }
tag_dict = { 'class': 'tag_required' }

class ContactForm(forms.Form):
    from_email = forms.EmailField(widget=forms.TextInput(attrs=attrs_dict), label='Email')
    subject = forms.CharField(widget=forms.TextInput(attrs=attrs_dict), max_length=100)
    status = forms.CharField(widget=forms.Select(choices=CONTACT_TYPES, attrs=tag_dict), max_length=200, label='Type of contact')
    description = forms.CharField(widget=forms.Textarea(attrs=textbox_dict), label='Comments and suggestions')
  
class DirtyForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs=textbox_dict), label='What\'s your cold dirt?')
    tag_list = forms.CharField(max_length=150, widget=forms.TextInput(attrs=tag_dict), label='Tags')

    def clean_description(self):
         if self.cleaned_data.get('description'):
            value = self.cleaned_data['description']
            import re
            if len(value) > 20 and not re.search('[<>]', value):
                profane_seen = [w for w in settings.PROFANITIES_LIST if w in value]
                if profane_seen:
                    raise forms.ValidationError(u'Extremily dirty words, racial slurs and random crap characters are not allowed in dirt.') 
                else:
                  return value
            else:
               raise forms.ValidationError(u'A little more detail please. No HTML.')
               
    def clean_tag_list(self):
        if self.cleaned_data.get('tag_list'):
            value = self.cleaned_data['tag_list']
            profane_seen = [w for w in settings.PROFANITIES_LIST if w in value]
            if profane_seen:
                raise forms.ValidationError(u'Extremily dirty words, racial slurs and random crap characters are not allowed in dirt.') 
            else:
              return value
              