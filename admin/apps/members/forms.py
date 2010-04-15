from django import forms
from django.utils.translation import ugettext as _
from models import Member, Status, ChangePassword, Address, Contact, \
    Payment

attrs_dict = { 'class': 'required' }

class MemberForm(forms.ModelForm):
    """Data member form"""
    class Meta:
        model = Member
        fields = ('gender', 'formsaddr',
                  'firstname', 'lastname', 'birthdate',
                  'country', 'doc_type', 'doc',
                  'doc_image', 'nationality', 'url',
                  'is_visible')


class MemberOnceForm(forms.ModelForm):
    """First time MemberForm"""
    class Meta:
        model = Member
        fields = ('gender', 'formsaddr',
                  'firstname', 'lastname', 'birthdate',
                  'country', 'doc_type', 'doc',
                  'doc_image', 'nationality', 'url',
                  'is_visible', 'statute')


class StatusForm(forms.ModelForm):  
    """Status form"""
    class Meta:  
        model = Status
        fields = ('status', 'comment')


class AddressForm(forms.ModelForm):  
    """Address form"""
    class Meta:  
        model = Address
        fields = ('old',
                  'via', 'address', 'province',
                  'town', 'near_of', 'number',
                  'bis', 'km', 'hm',
                  'stair', 'flat', 'door',
                  'zip', 'default')


class ContactForm(forms.ModelForm):  
    """Contact form"""
    class Meta:  
        model = Contact
        fields = ('type', 'account', 'default')

class PaymentForm(forms.ModelForm):  
    """Payment form"""
    class Meta:  
        model = Payment
        fields = ('method', 'amount', 'comment')


class InvitationForm(forms.Form):
    """Invite a friend form"""
    name = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs=attrs_dict),
        label=u'Introduzca su nombre' )
    email_invitation = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=200)),
        label=_('Email'))

    def clean_email(self):
        if self.cleaned_data['email']:
            return self.cleaned_data['email']
        raise forms.ValidationError(_('You must enter a valid email'))


#http://www.djangosnippets.org/snippets/191/
class PasswordForm(forms.Form):
    """Change pasword form"""
    username = forms.CharField(max_length=30, label=_("Username"))
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(widget=forms.PasswordInput(), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(), label=_("Repeat the password"))

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError(_('Passwords are not the same'))
        return self.data['password']

    def clean(self,*args, **kwargs):
        self.clean_password()
        return super(PasswordForm, self).clean(*args, **kwargs)


class LostForm(forms.Form):
    """Recovery passord form"""
    username = forms.CharField(max_length=30, label=_("Username"))

    def save(self, user):
        password_key = ChangePassword.objects.new_key(user)

