# -*- coding: utf-8 -*-
from django import forms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.views import login
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from apps.members.models import *
from apps.members.forms import *
from apps.general.models import INEMunicipality, INEProvince
from apps.poll.models import Poll, Ballot

from apps.registration.views import register
from apps.registration.forms import RegistrationFormTermsOfService

from datetime import datetime

# custom query function: http://www.djangosnippets.org/snippets/207/
def csql(query,qkeys):
    """convert rows from query to dictionary"""
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # build dict for template:
    fdicts = []
    for row in rows:
        i = 0
        cur_row = {}
        for key in qkeys:
            cur_row[key] = row[i]
            i = i + 1
        fdicts.append(cur_row)
    return fdicts


def spanish_callback(field, **kwargs):
    """Define Spanish date format valid"""
    if isinstance(field, models.DateField):
        kwargs['input_formats'] = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        return field.formfield(**kwargs)
    else:
        return field.formfield(**kwargs)

@login_required
def doc_jpg(request, url_null='/site_media/images/null.jpg'):
    """Get doc image from user"""
    member_object = Member.objects.filter(user=request.user)
    if not member_object:
        return HttpResponseRedirect(url_null)
    member = member_object.get()
    image_filename = member.doc_image.path
    return image_response(request, image_filename)

def image_response(request, image_filename, url_null='/site_media/images/null.jpg'):
    """Securing images"""
    from PIL import Image
    from StringIO import StringIO
    try:
        image = Image.open('%s'%image_filename)
        imdata=StringIO()
        image.save(imdata, format='JPEG')
        response = HttpResponse(imdata.getvalue(), mimetype='image/jpeg')
        return response
    except:
        return HttpResponseRedirect(url_null)

def check(request, username, password):
    """Check pair username/password"""
    # Only accept petitions from itself
    if request.META['REMOTE_ADDR'] in ('127.0.0.1', '91.121.68.9') :
        user = authenticate(username=username, password=password)
    else:
        user = None
    if user is not None:
        if user.is_active:
            response = "T" #true
        else:
            response = "X" #disabled
    else:
        response = "F" #false
    return HttpResponse(response)

def invitation(request, success_url='/admin/invitation/complete/'):
    """Send an invitation to a friend"""
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            current_domain = Site.objects.get_current().domain
            subject = u"Invitación para que conozca el Partido Pirata de %s" % form.data['name']
            message_template = loader.get_template('invitation_email.txt')
            message_context = Context({ 'site_url': current_domain,
                                        'name': form.data['name'] })
            message = message_template.render(message_context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [form.data['email_invitation']])
            return HttpResponseRedirect(success_url)
    else:
        form = InvitationForm()
    return render_to_response('invitation.html',
                              { 'form': form },
                              context_instance=RequestContext(request))

def start(request, template='start.html'):
    """Main entrance to admin with register and invitation forms"""
    if request.POST:
        return login(request)
    else:
        form_register = register(request, 
                                 form_class=RegistrationFormTermsOfService,
                                 start=True)
        form_invitation = InvitationForm(request.POST)
        request.session.set_test_cookie() #Following django's way ;-)
        return render_to_response(template,
                                  {'form_register': form_register,
                                   'form_invitation': form_invitation},
                                   context_instance = RequestContext(request))

def join(request):
    """Afiliation"""
    #step 1
    member_object = Member.objects.filter(user=request.user)
    if not member_object:
        result = profile_edit(request, step=True)
        return result
    else:
        member = member_object.get()
    #step 2
    addresses = Address.objects.filter(member=member)
    if not addresses:
        result = address_edit(request, step=True)
        return result
    #step 3
    payments = Payment.objects.filter(member=member).order_by('-id')
    if not payments:
        result = payment_edit(request, step=True)
    else:
        return HttpResponseRedirect('/admin/accounts/profile/')
    return result

@login_required
def dashboard(request, template='member/dashboard.html'):
    """Complete info of member (dashboard)"""
    context = RequestContext(request)
    member_object = Member.objects.filter(user=request.user)
    if member_object:
        member = member_object.get()
    else:
        member = None
    addresses = Address.objects.filter(member=member).order_by('id')
    payments = Payment.objects.filter(member=member).order_by('-id')
    contacts = Contact.objects.filter(member=member).order_by('id')
    status = Status.objects.filter(member=member).order_by('-id')
    
    polls = Poll.objects.filter(date_start__lt=datetime.now(),
                                date_end__gte=datetime.now()).order_by('id')
    ballots = Ballot.objects.filter(member=member).order_by('id')
    polls_pending = list(polls)
    for i in ballots:
        if i.option.poll in polls:
	    if i.option.poll in polls_pending:
                polls_pending.remove(i.option.poll)

    #Get pre-members
    qkeys = ['id', 'date', 'firstname', 'lastname']
    query = """
        SELECT m.id, s.date, m.firstname, m.lastname
        FROM members_status as s, members_member as m
        WHERE s.id in (select max(id) from members_status group by member_id)
        AND status in ('PA')
        AND s.member_id=m.id
        ORDER BY m.id desc;
        """
    new_members = csql(query, qkeys)

    return render_to_response(template,
                              {'member': member,
                               'addresses': addresses,
                               'payments': payments,
                               'contacts': contacts,
                               'status': status,
                               'new_members': new_members,
                               'polls_pending': polls_pending},
                               context_instance=context)

@permission_required('member.can_admin')
def revision(request, member_id, template = 'member/dashboard.html'):
    """Access to members data by an admin"""
    context = RequestContext(request)
    member = Member.objects.get(id=member_id)
    addresses = Address.objects.filter(member=member).order_by('id')
    contacts = Contact.objects.filter(member=member).order_by('id')
    status = Status.objects.filter(member=member).order_by('-id')
    payments = Payment.objects.filter(member=member).order_by('-id')
    return render_to_response(template,
                              {'member': member,
                               'addresses': addresses,
                               'payments': payments,
                               'contacts': contacts,
                               'status': status,
                               'revision': True },
                               context_instance=context)

@permission_required('member.can_admin')
def revision_history(request, member_id):
    """Edit status"""
    member = Member.objects.get(id=member_id)
    status = Status.objects.filter(member=member).order_by('-id')
    form = StatusForm(data=request.POST or None, instance=None)

    if form.is_valid():
        status = form.save(commit=False)
        status.member = member
        status.save()
        return HttpResponseRedirect('/admin/accounts/profile/')

    return render_to_response('member/history_edit.html',
                              { 'form': form,
                                'member': member,
                                'status': status } )

@permission_required('member.can_admin')
def revision_doc_jpg(request, member_id):
    """Get doc image from user (admin edition)"""
    member = Member.objects.get(id=member_id)
    image_filename = member.doc_image.path
    return image_response(request, image_filename)

@login_required
def profile_edit(request, step=False):
    """Edit profile data"""
    context = RequestContext(request)
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None
    status = Status.objects.filter(member=member).order_by('-id')
    if request.POST:
        form = MemberForm(request.POST, request.FILES, instance=member)
    else:
        form = MemberForm(instance=member)
    
    if step:
        # Give more information
        title = _('Identity. Step 1/3')
    else:
        title = None
    
    if form.is_valid():
        #Save member data
        pre = form.save(commit=False)
        pre.user = request.user
        pre.save()
        # is the user entering data for first time?
        if step:
            return HttpResponseRedirect('/admin/members/join/')
        else:
            return HttpResponseRedirect('/admin/accounts/profile/')
    return render_to_response('member/profile_edit.html',
                              { 'form': form,
                                'member': member,
                                'title': title,
                                'step': step,
                                'status': status },
                  context_instance = context)

@login_required
def address_edit(request, step=False):
    """Edit address data"""
    context = RequestContext(request)
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None
    status = Status.objects.filter(member=member).order_by('-id')
    try:
        address = Address.objects.filter(member=member)[0]
    except:
        address = None
    form = AddressForm(request.POST or None, instance=address)

    if step:
        # Give more information
        title = _('Address. Step 2/3')
    else:
        title = None

    if form.is_valid():
        pre = form.save(commit=False)
        pre.member = member
        pre.save()
        if step:
            return HttpResponseRedirect('/admin/members/join/')
        else:
            return HttpResponseRedirect('/admin/accounts/profile/')

    return render_to_response('member/address_edit.html',
                              { 'form': form,
                                'member': member,
                                'title': title,
                                'step': step,
                                'status': status },
                  context_instance = context )

@login_required
def payment_edit(request, step=False):
    """Edit payment data"""
    member = Member.objects.get(user=request.user)
    status = Status.objects.filter(member=member).order_by('-id')
    try:
        payment = Payment.objects.filter(member=member)[0]
    except: #put a list with exceptions explicity
        payment = None
    form = PaymentForm(request.POST or None, instance=payment)

    if step:
        # Give more information when steps
        title = _('Instalment. Step 3/3')
    else:
        title  = None

    if form.is_valid():
        pre = form.save(commit=False)
        pre.member = member
        pre.type = 'CU'
        pre.save()
        if step:
            #Save status with pre-status choiced
            status = Status(member=member, status="PA")
            status.save()
        return HttpResponseRedirect('/admin/accounts/profile/')

    return render_to_response('member/payment_edit.html',
                              { 'form': form,
                                'member': member,
                                'title': title,
                                'step': step,
                                'status': status } )

@login_required
def contact_edit(request, id="1"):
    """Edit contact data"""
    id = int(id)
    member = Member.objects.get(user=request.user)
    contacts = Contact.objects.filter(member=member).order_by("id")
    
    if contacts and id <= len(contacts):
        contact = contacts[id-1]
    else:
        contact = None
    form = ContactForm(request.POST or None, instance=contact)

    if form.is_valid():
        pre = form.save(commit=False)
        pre.member = member
        pre.save()
        return HttpResponseRedirect('/admin/accounts/profile/')
        
    return render_to_response('member/contact_edit.html',
                              { 'form': form,
                                'member': member } )

@login_required
def contact_new(request):
    """Add new contact"""
    member = Member.objects.get(user=request.user)
    form = ContactForm(request.POST or None)
    
    if form.is_valid():
        pre = form.save(commit=False)
        pre.member = member
        pre.save()
        return HttpResponseRedirect('/admin/accounts/profile/')
        
    return render_to_response('member/contact_edit.html',
                              { 'form': form,
                                'member': member } )

@login_required
def contact_delete(request, id):
    """Delete contact"""
    id = int(id)
    if id == 1:
        return HttpResponseRedirect('/admin/accounts/profile/')
    member = Member.objects.get(user=request.user)
    contacts = Contact.objects.filter(member=member)
    if contacts and id > len(contacts):
        return HttpResponseRedirect('/admin/accounts/profile/')
    contact = contacts[id-1]
    contact.delete()
    return HttpResponseRedirect('/admin/accounts/profile/')

def lost(request, template='lost.html', success_url='/admin/members/lost/sent'):
    """First step to get new password"""
    if request.method == 'POST':
        form = LostForm(request.POST)
        if form.is_valid():
            username = form.data['username']
            user_object = User.objects.filter(username=username)
            if user_object:
                user = user_object.get()
                #send a mail with the password_key url
                form.save(user)
                return HttpResponseRedirect(success_url)
    else:
        form = LostForm()
    return render_to_response(template,
                              context_instance=RequestContext(request))

def password_sent(request, template='lost_sent.html'):
    """Change password done"""
    return render_to_response(template,
                              context_instance=RequestContext(request))

def password(request, password_key, success_url='/admin/members/lost/done'):
    """Validate new passwords"""
    password_key = password_key.lower() # Normalize before trying anything with it.
    account = get_object_or_404(ChangePassword, password_key=password_key)
    if not account.password_key_expired():
        if request.method == 'POST':
            form = PasswordForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                if username == account.user.username and email == account.user.email:
                    password = form.cleaned_data['password']
                    account.user.set_password(password)
                    account.user.save()
                    account.delete()
                    return HttpResponseRedirect(success_url)
        else:
            form = PasswordForm()
    else:
        form = PasswordForm()
    return render_to_response('lost_edit.html',
                              {'form': form},
                              context_instance=RequestContext(request))

def password_done(request, template='lost_done.html'):
    """Change password done"""
    return render_to_response(template,
                              context_instance=RequestContext(request))

@permission_required('member.can_admin')
def list_general(request, template='list.html'):
    from apps.members.choices import PROVINCE_CHOICES, STATUS_CHOICES
    if request.method == 'POST':
        # form data control
        if request.POST['province'] == 'ALL':
            PROVINCE = ""
            addresses = Address.objects.all()
        else:
            PROVINCE = request.POST['province']
            addresses = Address.objects.filter(province=PROVINCE)
        if request.POST['status'] == 'ALL':
            STATUS = ("PA", "AF", "PS", "SI", "IN")
        else:
            STATUS = request.POST['status']
    else:
        PROVINCE = ""
        STATUS = ("PA", "AF", "PS", "SI", "IN")
        addresses = Address.objects.all()

    members = Member.objects.order_by('lastname');

    _members = filter(lambda x: x.member.status != None and
        x.member.status.status in STATUS, addresses)
    members = [x.member for x in _members]

    for i in members:
        town = i.address.town
        province = i.address.get_province_display
        prov = INEProvince.objects.filter(name=province)
        if town and prov:
            mun = INEMunicipality.objects.filter(name__icontains=town, province=prov[0])

    data = {'members': members,
            'provinces': PROVINCE_CHOICES, 'PROVINCE': PROVINCE,
            'status': STATUS_CHOICES, 'STATUS': STATUS}
    return render_to_response(template, data,
                              context_instance=RequestContext(request))
