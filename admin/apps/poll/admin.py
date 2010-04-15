from django.contrib import admin
from apps.poll.models import *

for model in (I18N, Poll, Option, Ballot, Delegate, Delegation):
    admin.site.register(model)
