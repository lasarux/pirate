from django.db import models
#from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from choices import *
from apps.members.models import Member

class I18N(models.Model):
    language = models.CharField(_("Language"), max_length=2,
                                choices=CHOICES_I18N)
    translation = models.TextField(_("Translation"))

    def __unicode__(self):
        return self.translation

class Poll(models.Model):
    author = models.ForeignKey(Member)
#    question = models.ForeignKey(I18N)    # !?!
    question = models.TextField(_("Question"))
    slug = models.SlugField(_("Slug"), max_length=128)
    url = models.URLField(_("URL"), max_length=256)
    date = models.DateTimeField(_("Date"), auto_now=True)
    winner = models.IntegerField(_("Winner"), blank=True, null=True)
    date_start = models.DateTimeField(_("Date start"))
    date_end = models.DateTimeField(_("Date end"))
    status = models.CharField(_("Status"), max_length=5,
                              choices=CHOICES_STATUS)

    def __unicode__(self):
        return self.question
        
    class Admin:
        list_display = ('question', 'author', 'date_start', 'date_end', 'status', 'url')

class Option(models.Model):
    poll = models.ForeignKey(Poll)
    #item = models.ForeignKey(I18N)
    item = models.TextField(_("Item"))
    date = models.DateTimeField(_("Date"), auto_now=True)
    status = models.CharField(_("Status"), max_length=5,
                              choices=CHOICES_STATUS)

    def __unicode__(self):
        return self.item #.translation
    
    class Admin:
        list_display = ('poll', 'status', 'item')

class Ballot(models.Model):
    member = models.ForeignKey(Member)
    option = models.ForeignKey(Option)
    date = models.DateTimeField(_("Date"), auto_now=True)

    class Admin:
        pass

class Delegate(models.Model):
    delegate = models.ForeignKey(Member)
    date = models.DateTimeField(_("Date"), auto_now=True)
    date_start = models.DateTimeField(_("Date start"), auto_now=True)
    date_end = models.DateTimeField(_("Date end"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=5,
                              choices=CHOICES_STATUS, blank=True, null=True)
    status_date = models.DateTimeField(_("Date"), blank=True, null=True)

    def __unicode__(self):
        return self.delegate.username
        
    class Admin:
        pass

class Delegation(models.Model):
    user = models.ForeignKey(Member, related_name="me")
    delegate = models.ForeignKey(Member)
    date = models.DateTimeField(_("Date"), auto_now=True)
    date_start = models.DateTimeField(_("Date start"), auto_now=True)
    date_end = models.DateTimeField(_("Date end"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=5,
                              choices=CHOICES_DELEGATE, blank=True, null=True)
    status_date = models.DateTimeField(_("Date"), blank=True, null=True)

    def __unicode__(self):
        return self.user.username

    class Admin:
        pass
