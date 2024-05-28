from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import CustomUser
from hajni_courses_app.utils.constants import PHONE_NUMBER_VALIDATOR


class LoginForm(forms.Form):
    """
    Login form class.
    """
    username = forms.CharField(required=True, max_length=150, label=_('Felhasználónév'),
                               widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, label=_('Jelszó'))


class SignUpForm(UserCreationForm):
    """
    SignUp form class.
    """
    last_name = forms.CharField(required=True, max_length=150, label=_('Családnév'))
    first_name = forms.CharField(required=True, max_length=150, label=_('Keresztnév'),
                                 widget=forms.TextInput(attrs={'autofocus': True}))
    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(attrs={'class': 'validate', }))
    phone_number = forms.CharField(required=False, max_length=20, label=_('Telefonszám'),
                                   validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'phone_number', 'username', 'password1', 'password2']


class PersonalDataForm(forms.Form):
    """
    Personal Data form class.
    """
    last_name = forms.CharField(required=True, max_length=150, label=_('Családnév'))
    first_name = forms.CharField(required=True, max_length=150, label=_('Keresztnév'),
                                 widget=forms.TextInput(attrs={'autofocus': True}))
    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(attrs={'class': 'validate', }))
    phone_number = forms.CharField(required=False, max_length=20, label=_('Telefonszám'),
                                   validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'phone_number']


class ApplyForm(forms.Form):
    """
    Application form class.
    """
    last_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'last_name', 'name': 'last_name'}),
                                label=_('Családnév'), required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'id': 'first_name', 'name': 'first_name'}),
                                 label=_('Keresztnév'), required=True)
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'age', 'name': 'age', 'autofocus': True}),
                             label=_('Kor'), required=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'id': 'address', 'name': 'address'}),
                              label=_('Cím (település)'), required=False)
    email = forms.CharField(widget=forms.EmailInput(attrs={'id': 'email', 'name': 'email'}),
                            label=_('E-mail'), required=True)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'id': 'phone_number', 'name': 'phone_number'}),
                                   required=False,
                                   label=_('Telefonszám'),
                                   validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])
    experience = forms.CharField(widget=forms.Textarea(attrs={'rows': '7', 'maxlength': '500',
                                                              'placeholder': _('Kérjük írja le számítógépes ismereteit ...'),
                                                              'id': 'experience', 'name': 'experience',
                                                              'class': 'text_input'}),
                                 required=True,
                                 label=_('Számítógépes tapasztalat'))
