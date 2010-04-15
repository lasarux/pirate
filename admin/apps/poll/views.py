from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from apps.members.models import Member
from apps.poll.models import Poll, Option, Ballot

def votation(request, poll_slug, template='poll/votation.html'):
    """Complete info of member (dashboard)"""
    context = RequestContext(request)
    member_object = Member.objects.filter(user=request.user)
    if member_object:
        member = member_object.get()
    else:
        member = None
    if request.method == 'POST':
        option_id = int(request.POST['option'])
        option = Option.objects.get(id=option_id)
        ballot = Ballot(member=member, option=option)
        ballot.save()
        return HttpResponseRedirect('/admin/accounts/profile/')
    poll = Poll.objects.get(slug = poll_slug)
    options = Option.objects.filter(poll=poll).order_by('id')
    return render_to_response(template, 
                              {'member': member,
                               'poll': poll,
                               'options': options},
                              context_instance=context)
