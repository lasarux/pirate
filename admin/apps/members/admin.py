from django.contrib import admin
from apps.members.models import Member, Status, Address, Contact, Payment


class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'date', 'status', 'comment')

class StatusInline(admin.TabularInline):
    model = Status
    extra = 1
    
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'date', 'type', 'method',
                    'amount', 'cc', 'comment', 'ok')
                    
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

class AddressAdmin(admin.ModelAdmin):
    list_display = ('member', 'via', 'address', 'town', 'zip')

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1

class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'account', 'default', 'member')
    
class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'doc', 'status')
    search_fields = ('firstname', 'lastname')
    inlines = [StatusInline, AddressInline, ContactInline, PaymentInline]

    class Meta:
        permissions = (
            ("can_admin", "Can admin data from others"),
            ("can_vote", "Can vote in polls"),
        )

admin.site.register(Member, MemberAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Contact, ContactAdmin)
