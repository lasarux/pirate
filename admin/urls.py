from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
import settings
import os

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^admin/', include('admin.apps.foo.urls.foo')),

    # Static media
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': '%s' % settings.media}),
    (r'^pub/(.*)$', 'django.views.static.serve', {'document_root': '%s' % settings.pub}),
    (r'^favicon.ico$', 'django.views.static.serve', {'document_root': '%s' % settings.media, 'path': "favicon.ico"}),
    # Uncomment this for admin:
    ('^admin/(.*)', admin.site.root),
    # i18n
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Homepage
    #(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'start.html'}),
    (r'^$', 'apps.members.views.start'),

    # Lost password
    (r'^members/lost/$', 'apps.members.views.lost'),
    (r'^members/lost/done/$','apps.members.views.password_done'),
    (r'^members/lost/sent/$','apps.members.views.password_sent'),
    (r'^members/lost/(?P<password_key>\w+)/$','apps.members.views.password'),

    # Members
    #(r'^users/$', 'django.views.generic.list_detail.object_list', dict(user_dict, template_name="users/user_list.html")),
    #(r'^users_markers/$', 'django.views.generic.list_detail.object_list', dict(user_dict, template_name="users/markers.xml")),
    (r'^members/profile/edit/$', 'apps.members.views.profile_edit'),
    (r'^members/address/edit/$', 'apps.members.views.address_edit'),
    (r'^members/payment/edit/$', 'apps.members.views.payment_edit'),
    (r'^members/contact/edit/$', 'apps.members.views.contact_edit'),
    (r'^members/doc.jpeg$', 'apps.members.views.doc_jpg'),
    (r'^members/join/$', 'apps.members.views.join'),
    (r'^members/contact/edit/(?P<id>\d+)/$', 'apps.members.views.contact_edit'),
    (r'^members/contact/new/$', 'apps.members.views.contact_new'),
    (r'^members/contact/delete/(?P<id>\d+)/$', 'apps.members.views.contact_delete'),

    (r'^accounts/', include('apps.registration.urls')),
    (r'^check/(?P<username>\w+)/(?P<password>\w+)/$', 'apps.members.views.check'),

    (r'^invitation/$', 'apps.members.views.invitation'),
    #(r'^invitation/complete/$', 'apps.members.views.invitation_complete'),
    url(r'^invitation/complete/$',
                           direct_to_template,
                           {'template': 'invitation_complete.html'},
                           name='invitation_complete'),

    ##(r'^accounts/login/$', 'apps.members.views.start'), #'django.contrib.auth.views.login'),
    ##(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'} ),
    #(r'^accounts/login/$', 'django.views.generic.simple.direct_to_template', {'template': 'accounts/login.html'}),
    ##(r'^accounts/profile/$', 'apps.members.views.dashboard'),
    (r'^revision/dashboard/(?P<member_id>\d+)/$', 'apps.members.views.revision'),
    (r'^revision/history/(?P<member_id>\d+)/$', 'apps.members.views.revision_history'),
    (r'^revision/(?P<member_id>\d+)/doc.jpeg$', 'apps.members.views.revision_doc_jpg'),

    (r'^list/$', 'apps.members.views.list_general'),

    # TODO: uncomment this when it's implemented!
#    (r'^list/status/(?P<status>\w+)/$', 'apps.members.views.list_status'),
#    (r'^list/province/(?P<province>\w+)/$', 'apps.members.views.list_province'),
#    (r'^list/(?P<status>\w+)/(?P<province>\w+)/$', 'apps.members.views.list_province'),
)
