# -*- coding: utf-8 -*-
#FIXME: transitional tables

from django.db import models
from django.utils.translation import ugettext as _

class INEProvince(models.Model):
    code = models.IntegerField(_('Code'))
    name = models.CharField(_('Name'), max_length=100)
    # google maps
    lat = models.DecimalField( decimal_places=2, max_digits=9, 
        null=True, blank=True )
    lon = models.DecimalField( decimal_places=2, max_digits=9, 
        null=True, blank=True )
    accuracy = models.IntegerField(null=True, blank=True)
        
    def __unicode__(self):
        return self.name

    class Admin:
        list_display = ('code', 'name')
        

class INEMunicipality(models.Model):
    province = models.ForeignKey(INEProvince)
    code = models.IntegerField(_('Code'))
    name = models.CharField(_('Name'), max_length=100)
    men = models.IntegerField(_('Men'))
    women = models.IntegerField(_('Women'))
    # google maps
    lat = models.DecimalField( decimal_places=2, max_digits=9, 
        null=True, blank=True )
    lon = models.DecimalField( decimal_places=2, max_digits=9, 
        null=True, blank=True )
    accuracy = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'inemunicipalities' # FIXME: it doesn't work

    class Admin:
        list_display = ('province', 'code', 'name', 'men', 'women')
        
    def __unicode__(self):
        return self.name
