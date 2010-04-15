# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.template import Context, loader
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random, re, sha
from django.contrib.sites.models import Site

from choices import *

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class Territory(models.Model):
    """A real territory model"""
    name = models.CharField(max_length=64)
    description = models.TextField(null=True)
    #It's a tree: parent ID
    parent = models.ForeignKey(
        'self',
        null=True,
        related_name='child_set')
    class Admin:
        pass

class Member(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'), unique=True)
    created = models.DateTimeField(_('Created'), default=datetime.now())
    gender = models.CharField(_('Gender'), max_length=1,
        choices=GENDER_CHOICES, null=True)
    webstatus = models.CharField(_('Status in web'), max_length=2,
    choices=NEWSTATUS_CHOICES, null=True)
    formsaddr = models.CharField(_('From of address'), max_length=2,
        choices=FORMADDR_CHOICES, null=True, blank=True)
    firstname = models.CharField(_('First Name'), max_length=64)
    lastname = models.CharField(_('Last Name'), max_length=64, null=True)
    birthdate = models.DateField(_('Birth Date'),
        help_text=_('Format: YYYY-mm-dd'), null=True)
    country = models.CharField(_('Country'), max_length=3,
        choices=COUNTRY_CHOICES, default='esp' )
    doc_type = models.CharField(_('Document Type'),max_length=3,
        choices=DOC_CHOICES, default='DNI' )
    doc = models.CharField(_('Document'), max_length=20, null=True)
    nationality = models.CharField(
        _('Nationality'),max_length=3, choices=COUNTRY_CHOICES,
        default="esp" )
    security_phrase=models.TextField(_('Security Phrase'), null=True)
    security_response=models.TextField(
        _('Security Response'), null=True)
    url = models.URLField(_('URL Blog'), blank=True, null=True)
    is_visible = models.BooleanField(_('Is visible?'),
        choices=ACCEPT_CHOICES, default=False)
    statute = models.CharField(_('Accept statutes?'), max_length=1,
        choices=ACCEPTONE_CHOICES, default='Y', null=True)
    doc_image = models.ImageField(_('Document Image'),
        help_text=_('Remember to include both sides of your Document'),
        upload_to='docs/',  null=True )

    def __unicode__(self):
        if self.lastname == None:
            return self.firstname
        else:
            return "%s, %s"%(self.lastname, self.firstname)

    def _get_fullname(self):
        """Return the member's full name."""
        return '%s %s' % (self.firstname, self.lastname)
    fullname = property(_get_fullname)

    def _get_address(self):
        """Return member main address"""
        address = Address.objects.filter(member=self)[0:1].get()
        return address
    address = property(_get_address)

    def _get_province(self):
        """Return province of main address"""
        province = self.address.province
        if province:
            return province
        return ""
    province = property(_get_province)

    def _get_status(self):
        """Return member status"""
        try:
            status = Status.objects.filter(member=self).order_by('-id')[0:1].get()
        except:
            status = None
        return status.status
    status = property(_get_status)

    def _get_payments(self):
        """Return member payments"""
        try:
            result = Payment.objects.filter(member=self).order_by('-id')
        except:
            result = None
        return result
    payments = property(_get_payments)

    def search_by_name(self, name):
        try:
            lastname, firstname = name.split(",")
        except:
            firstname = ''
            lastname = name
        try:
            member = Member.objects.filter(
                firstname=firstname.lstrip(),
                lastname=lastname.lstrip() )
        except:
            member = None
        return member


class Status(models.Model):
    """History"""
    member = models.ForeignKey(Member)
    date = models.DateTimeField(_('Date'), default=datetime.now)
    status = models.CharField(
        _('Status'), max_length=2, choices=STATUS_CHOICES, null=True)
    comment = models.TextField(_('Comment'), null=True, blank=True)

    def is_last(self):
        last = Status.objects.filter(member=self.member).order_by('-id')[0]
        if self.id == last.id:
            return True
        return False

    def __unicode__(self):
        return self.status

class Payment(models.Model):
    """Payments"""
    member = models.ForeignKey(Member)
    date = models.DateTimeField(_('Date'), default=datetime.now)
    type = models.CharField(
        _('Type'), max_length=2, choices=PAYMENT_CHOICES, null=True)
    method = models.CharField(
        _('Method'), max_length=2, choices=METHOD_CHOICES, null=True)
    amount = models.DecimalField(
        _('Amount'), max_digits=10, decimal_places=2)
    comment = models.TextField(
        _('Comment'), null=True, blank=True)
    cc = models.CharField(
        _('Current Account'), max_length=20, null=True, blank=True)
    ok = models.BooleanField(
        _('OK?'), default=False)

    def __unicode__(self):
        return "%s"%self.amount


class Address(models.Model):
    member = models.ForeignKey(Member, unique=True)
    #old = models.TextField(
    #    #TODO: only for init importation!
    #    _('Old'),
    #    core=True,
    #    null=True )
    via = models.CharField(_('Via'), max_length=4, choices=VIA_CHOICES,
        null=True)
    address = models.CharField(_('Address'), max_length=128, null=True)
    number = models.IntegerField(_('Number'), null=True, blank=True )
    bis = models.CharField(_('Bis'), max_length=1, null=True,
        blank=True )
    km = models.DecimalField(_('Km'), decimal_places=2, max_digits=6,
        null=True, blank=True )
    hm = models.DecimalField(_('Hm'),decimal_places=2, max_digits=6,
        null=True, blank=True )
    stair = models.CharField(_('Stair'), max_length=4, null=True,
        blank=True )
    flat = models.CharField(_('Flat'), max_length=16,  null=True,
        blank=True )
    door = models.CharField(_('Door'), max_length=16, null=True,
        blank=True )
    province = models.CharField(_('Province'), max_length=3,
        choices=PROVINCE_CHOICES, null=True)
    town = models.CharField(_('Town/City'),
        max_length=128,  #TODO: to use Territory!
        null=True)
    near_of = models.CharField(_('Reference/Near of'), max_length=128,
        null=True, blank=True )
    zip = models.CharField(_('Zip Code'), max_length=5, null=True)
    lat = models.DecimalField( decimal_places=2, max_digits=9,
        null=True, blank=True )
    lon = models.DecimalField( decimal_places=2, max_digits=9,
        null=True, blank=True )
    accuracy = models.IntegerField(null=True, blank=True)
    default = models.BooleanField(_('Is default?'), default=False )

    def __unicode__(self):
        if self.via and self.address and self.number:
            return "%s %s, %s"%(self.get_via_display(), self.address, self.number)
        return ""


class Contact(models.Model):
    member = models.ForeignKey(Member, verbose_name=_('Member'), unique=True)
    type = models.CharField(_('Type'), max_length=1,
        choices=CONTACT_CHOICES )
    account = models.CharField(_('Account'), max_length=64 )
    default = models.BooleanField(_('Is default?'), default=False )

    def __unicode__(self):
        return self.account


class ChangePasswordManager(models.Manager):
    def new_key(self, user):
        from django.core.mail import send_mail

        salt = sha.new(str(random.random())).hexdigest()[:5]
        password_key = sha.new(salt+user.username).hexdigest()
        key_object = self.filter(user=user)
        if key_object:
            item = key_object.get()
            item.delete()
        self.create(user=user, password_key=password_key)

        current_domain = Site.objects.get_current().domain
        subject = _("Change password at %s" % current_domain)
        message_template = loader.get_template('lost_email.txt')
        message_context = Context({ 'site_url': 'https://%s/' % current_domain,
                                    'password_key': password_key,
                                    'expiration_days': settings.CHANGE_PASSWORD_DAYS })
        message = message_template.render(message_context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

# Change Password stuff
class ChangePassword(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=_('User'),)
    password_key = models.CharField(_('Password key'), max_length=40)
    date = models.DateTimeField(_('Date'), default=datetime.now)

    objects = ChangePasswordManager()

    class Admin:
        list_display = ('__unicode__', 'password_key_expired')
        search_fields = ('user__username', 'user__first_name')

    def __unicode__(self):
        return _("Change password for %s" % self.user.username)

    def delete_password_key(self):
        self.delete()

    def password_key_expired(self):
        expiration_date = timedelta(days=settings.CHANGE_PASSWORD_DAYS)
        result = self.date + expiration_date <= datetime.now()
        return result
    password_key_expired.boolean = True

