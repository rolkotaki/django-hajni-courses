from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from .models import CustomUser
from hajni_courses_app.utils.constants import PHONE_NUMBER_VALIDATOR


PHONE_NUMBER_PLACEHOLDER = 'Pl.: +36201234567'


class LoginForm(forms.Form):
    """
    Login form class.
    """
    username = forms.CharField(required=True, max_length=150, label=_('Felhasználónév'),
                               widget=forms.TextInput(attrs={'autofocus': True}),
                               error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    password = forms.CharField(max_length=50, widget=forms.PasswordInput, label=_('Jelszó'),
                               error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})


class SignUpForm(UserCreationForm):
    """
    SignUp form class.
    """
    # Workaround to get these labels and messages in Hungarian. Strange, because for other messages it worked,
    # for example the length of the password. Until finding a nicer solution, leaving this as a workaround.
    error_messages = {
        "password_mismatch": _("A két jelszó nem egyezik!"),
    }
    username = UsernameField(label=_("Felhasználónév"), error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    password1 = forms.CharField(
        label=_("Jelszó"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'}
    )
    password2 = forms.CharField(
        label=_("Jelszó megerősítése"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'}
    )
    last_name = forms.CharField(required=True, max_length=150, label=_('Családnév'),
                                widget=forms.TextInput(attrs={'autofocus': True}),
                                error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    first_name = forms.CharField(required=True, max_length=150, label=_('Keresztnév'),
                                 error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(attrs={'class': 'validate', }),
                             error_messages={
                                 'required': 'Ennek a mezőnek a megadása kötelező.',
                                 'invalid': 'Adjon meg egy érvényes email címet!',
                             })
    phone_number = forms.CharField(required=False, max_length=20, label=_('Telefonszám'),
                                   widget=forms.TextInput(attrs={'placeholder': PHONE_NUMBER_PLACEHOLDER}),
                                   validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])
    privacy_policy = forms.BooleanField(required=True,
                                        error_messages={'required': 'Az Adatkezelési tájékoztató elfogadása kötelező.'})

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'phone_number', 'username', 'password1', 'password2']


class PersonalDataForm(forms.Form):
    """
    Personal Data form class.
    """
    last_name = forms.CharField(required=True, max_length=150, label=_('Családnév'),
                                widget=forms.TextInput(attrs={'autofocus': True}),
                                error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    first_name = forms.CharField(required=True, max_length=150, label=_('Keresztnév'),
                                 error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    email = forms.EmailField(required=True, max_length=254, widget=forms.EmailInput(attrs={'class': 'validate', }),
                             error_messages={
                                 'required': 'Ennek a mezőnek a megadása kötelező.',
                                 'invalid': 'Adjon meg egy érvényes email címet!',
                             })
    phone_number = forms.CharField(required=False, max_length=20, label=_('Telefonszám'),
                                   widget=forms.TextInput(attrs={'placeholder': PHONE_NUMBER_PLACEHOLDER}),
                                   validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])

    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'phone_number']


class ApplyForm(forms.Form):
    """
    Application form class.
    """
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'id': 'age', 'name': 'age', 'autofocus': True,
                                                             'class': 'user_form_text_input'}),
                             label=_('Kor'), required=True, validators=[MinValueValidator(1)],
                             error_messages={
                                 'required': 'Ennek a mezőnek a megadása kötelező.',
                                 'min_value': 'Adjon meg egy pozitív egész számot!',
                             })
    address = forms.CharField(widget=forms.TextInput(attrs={'id': 'address', 'name': 'address',
                                                            'class': 'user_form_text_input'}),
                              label=_('Cím (település)'), required=True,
                              error_messages={'required': 'Ennek a mezőnek a megadása kötelező.'})
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'id': 'phone_number', 'name': 'phone_number',
                                                                 'placeholder': PHONE_NUMBER_PLACEHOLDER,
                                                                 'class': 'user_form_text_input'}),
                                   required=False,
                                   label=_('Telefonszám'),
                                   validators=[RegexValidator(regex=PHONE_NUMBER_VALIDATOR,
                                                              message=_('Adjon meg egy érvényes telefonszámot!'))])
    experience = forms.CharField(widget=forms.Textarea(attrs={'rows': '7', 'maxlength': '500',
                                                              'placeholder': _('Kérjük írja le számítógépes ismereteit ...'),
                                                              'id': 'experience', 'name': 'experience',
                                                              'class': 'text_input'}),
                                 required=False,
                                 label=_('Számítógépes tapasztalat'))
