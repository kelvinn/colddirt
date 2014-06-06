from django.db import models, connection
import datetime

            
class TagManager(models.Manager):
    def popular_tags(self):
        # This is a custom query, which rarely needs to be done in Django
        # Sadly, I had to do one.  Have to keep my MySQL skills
        # I guess...
        query = "SELECT name, slug, COUNT(tagling_id) AS tagcount " \
            "FROM dirty_tagling JOIN dirty_dirt_tags " \
            "ON dirty_tagling.id = dirty_dirt_tags.id " \
            "GROUP BY tagling_id ORDER BY name DESC "
        cursor = connection.cursor()
        cursor.execute(query)
        result_list = []
        for row in cursor.fetchall():
            p = self.model(name=row[0], slug=row[1])
            p.tagcount = row[2]
            result_list.append(p)
        return result_list

class Tagling(models.Model):
    """A tag on an item."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(editable=False)

    objects = TagManager()
    
    class Meta:
        ordering = ["name"] 
        
    def __str__(self):
        return self.name

class Report(models.Model):
    item = models.CharField(max_length=100)
    publish_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["item"]  
        
    def __str__(self):
        return self.item
    
class Word(models.Model):
    dirtyword = models.SlugField(max_length=100, editable=False)
    is_taken = models.BooleanField(('taken'), default=False, help_text=("Designates if this word has been used or not."))
    
    class Meta:
        ordering = ["dirtyword"]
        
    def __str__(self):
        return self.dirtyword
        
    def import_words(self, file):  
        # To use this, from the shell (python manage.py shell) do:
        #   from colddirt.dirty.models import Word
        #   addwords = Word()
        #   addwords.import_words('american-english') 
        # This will max out your CPU/RAM and will take some time...
        # If your wordlist doesn't have any duplicates, you shouldn't
        # use the try/except or the second sql lookup
        import re
        from django.template.defaultfilters import slugify
        wordlist = open(file, "rb")
        i = 0
        p = re.compile(r"[^A-Za-z0-9]").sub
        for word in wordlist:
            if len(word) > 3:
                try:
                    Word.objects.get(dirtyword=word)
                    print "Duplicate: " + word
                except:
                    good_word = slugify(p("", word))
                    object = Word('',good_word, 0)
                    object.save()
                    if i % 5000 == 0:
                        print i
                    i += 1 
                
        print "Total words: %s" % i 
            
class Dirt(models.Model):
    dirtword = models.CharField(max_length=100)
    publish_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    tags = models.ManyToManyField(Tagling)

    def save(self):
        from django.template.defaultfilters import slugify
        if not self.id:
            self.publish_date = datetime.datetime.now()
        self.description = self.description
        self.dirtword = self.dirtword
        super(Dirt, self).save()
        
    class Meta:
        ordering = ('-publish_date', 'dirtword')

    def __str__(self):
        return self.dirtword
    
    def get_absolute_url(self):
        return "/dirtword/%s/" % self.dirtword
      

