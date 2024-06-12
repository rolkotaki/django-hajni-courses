from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from hajni_courses.logger import logger
from hajni_courses_app.utils.AccountActivationTokenGenerator import account_activation_token
from hajni_courses_app.utils.constants import PAGINATION_PAGES, COURSES_PER_PAGE
from .forms import SignUpForm, LoginForm, PersonalDataForm, ApplyForm
from .models import CustomUser, Course


class HomePage(TemplateView):
    """
    View class for the Home page.
    """
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        """
        Overriding the get_context_data method to add the superuser email.
        """
        context = super().get_context_data(**kwargs)
        superusers_emails = CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True)
        context["superusers_emails"] = '; '.join(superusers_emails)
        return context

    def post(self, request, *args, **kwargs):
        """
        Post method to send the callback request email to the owner.
        """
        if request.POST.get('call_me', None):
            if request.user.phone_number != "":
                CustomUser.send_callback_request(request.user)
                messages.success(request, _('Visszahívási kérelmedet elküldtük.'))
            else:
                messages.error(request, _("Önnek nincs megadva telefonszám, így nem kérhet visszahívást."))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


def sign_up(request):
    """
    View method for signup.
    """
    if request.method == 'GET':
        form = SignUpForm()
        return render(request, "signup.html", {'form': form})

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # sending the email to confirm the registration
            user.send_activation_link(get_current_site(request).domain,
                                      'https' if request.is_secure() else 'http')
            logger.info('New user signed up: {}, {}'.format(user.pk, user.username))
            messages.success(request, _("A fiókodat sikeresen létrehoztuk, kérlek fejezd be a regisztrációt az "
                                        "emailben küldött aktivációs linkre kattintással."))
            return render(request, "signup.html", {'form': form})
        return render(request, "signup.html", {'form': form})


def activate_account(request, uidb64, token):
    """
    View method to activate a user account.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        logger.warning('Unsuccessful token validation: uidb64 {}; token {}'.format(uidb64, token))
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, _("A fiókodat sikeresen aktiváltuk, most már be tudsz jelentkezni."))
    else:
        if user:
            logger.warning('Unsuccessful user activation: user {}'.format(user.pk))
        messages.error(request, _("Az aktivációs link nem érvényes vagy hiba történt a fiókod aktiválása során."))
    return redirect('login')


def login_user(request):
    """
    View method for login.
    """
    if request.method == 'GET':
        form = LoginForm()
        return render(request, "login.html", {'form': form})

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:  # it seems that the authenticate() returns None if the user is not active anyway
                    messages.error(request, _("A felhasználó nem aktív!"))
            else:
                messages.error(request, _("Helytelen felhasználónév vagy jelszó!"))
        return render(request, "login.html", {'form': form})


@login_required(login_url='login')
def personal_data(request):
    """
    View method for the personal data.
    """
    if request.method == 'GET':
        user_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone_number': request.user.phone_number
        }
        form = PersonalDataForm(initial=user_data)
        return render(request, "personal_data.html", {'form': form})

    if request.method == 'POST':
        form = PersonalDataForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.phone_number = form.cleaned_data['phone_number']
            if user.email != form.cleaned_data['email']:
                # if the email has changed, we send an activation mail to the user to confirm their new email address
                user.email = form.cleaned_data['email']
                user.is_active = False
                user.save()
                user.send_activation_link(get_current_site(request).domain,
                                          'https' if request.is_secure() else 'http')
                redirect('logout')
                messages.success(request, _("Az adataidat sikeresen frissítettük és küldtünk egy emailt, hogy meg tudd "
                                            "erősíteni az új email címedet."))
            else:
                user.save()
                messages.success(request, _("Az adataidat sikeresen frissítettük."))
            return redirect('personal_data')
        return render(request, "personal_data.html", {'form': form})


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View class for the password change. It inherits from the Django's PasswordChangeView,
    only the success url is changed.
    """
    success_url = '/'
    login_url = 'login'


class DeleteProfileView(LoginRequiredMixin, TemplateView):
    """
    View class for deleting the user profile.
    """
    template_name = "delete_profile.html"
    login_url = 'login'

    def post(self, request, *args, **kwargs):
        """
        Post method to delete the user profile.
        """
        if request.POST.get('delete_profile', None):
            if CustomUser.delete_user_profile(request):
                return redirect('home')
            else:
                messages.error(request, _("Hiba történt profilod törlése közben. Lépj kapcsolatba velünk."))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class PensionerCoursesListPage(TemplateView):
    """
    View class for the pensioner course list.
    """
    template_name = "pensioner_courses.html"

    def get_context_data(self, **kwargs):
        """
        Overriding the get_context_data method to add the list of active Courses.
        """
        context = super().get_context_data(**kwargs)
        courses = Course.objects.filter((Q(active=True) & Q(for_pensioners=True))).order_by('id')

        page_number = int(self.request.GET.get('page', 1))
        paginator = Paginator(courses, COURSES_PER_PAGE)
        page = paginator.get_page(page_number)
        context["page"] = page
        context["courses"] = page.object_list

        pages_before_after = int(PAGINATION_PAGES / 2)
        if paginator.num_pages <= PAGINATION_PAGES:
            pages = [i for i in range(1, paginator.num_pages + 1)]
        elif paginator.num_pages - page.number < pages_before_after:
            pages = [i for i in range(paginator.num_pages - PAGINATION_PAGES + 1, paginator.num_pages + 1)]
        elif page.number - pages_before_after <= 0:
            pages = [i for i in range(1, PAGINATION_PAGES + 1)]
        else:
            pages = [i for i in range(page.number - pages_before_after, page.number + pages_before_after + 1)]
        context["pages"] = pages

        return context


class GeneralCoursesListPage(TemplateView):
    """
    View class for the general course list.
    """
    template_name = "general_courses.html"

    def get_context_data(self, **kwargs):
        """
        Overriding the get_context_data method to add the list of active Courses.
        """
        context = super().get_context_data(**kwargs)
        courses = Course.objects.filter((Q(active=True) & Q(for_non_pensioners=True))).order_by('id')

        page_number = int(self.request.GET.get('page', 1))
        paginator = Paginator(courses, COURSES_PER_PAGE)
        page = paginator.get_page(page_number)
        context["page"] = page
        context["courses"] = page.object_list

        pages_before_after = int(PAGINATION_PAGES / 2)
        if paginator.num_pages <= PAGINATION_PAGES:
            pages = [i for i in range(1, paginator.num_pages + 1)]
        elif paginator.num_pages - page.number < pages_before_after:
            pages = [i for i in range(paginator.num_pages - PAGINATION_PAGES + 1, paginator.num_pages + 1)]
        elif page.number - pages_before_after <= 0:
            pages = [i for i in range(1, PAGINATION_PAGES + 1)]
        else:
            pages = [i for i in range(page.number - pages_before_after, page.number + pages_before_after + 1)]
        context["pages"] = pages

        return context


class CoursePage(TemplateView):
    """
    View class for the course.
    """
    template_name = "course.html"

    def get_context_data(self, **kwargs):
        """
        Overriding the get_context_data method to add the Course object.
        """
        context = super().get_context_data(**kwargs)
        context['previous_url'] = self.request.META.get('HTTP_REFERER', '/')
        context["course"] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context


@login_required(login_url='login')
def apply(request, slug):
    """
    View method for the application.
    """
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'GET':
        user_data = {
            # 'first_name': request.user.first_name,
            # 'last_name': request.user.last_name,
            # 'email': request.user.email,
            'phone_number': request.user.phone_number
        }
        form = ApplyForm(initial=user_data)
        return render(request, "apply.html", {'form': form, 'course': course})

    if request.method == 'POST':
        form = ApplyForm(request.POST)
        if form.is_valid():
            application_data = {'first_name': request.user.first_name,
                                'last_name': request.user.last_name,
                                'age': form.cleaned_data['age'],
                                'address': form.cleaned_data['address'],
                                'email': request.user.email,
                                'phone_number': form.cleaned_data['phone_number'],
                                'experience': form.cleaned_data['experience'],
                                'course': course.name
                                }
            course.send_application(application_data=application_data)
            messages.success(request, _("Jelentkezésed sikeres volt."))
            return redirect('apply', slug=course.slug)
        form = ApplyForm(request.POST)
        return render(request, "apply.html", {'form': form, 'course': course})
