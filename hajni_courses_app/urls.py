from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('user/', include("django.contrib.auth.urls")),
    path('bejelentkezes', views.login_user, name='login'),
    path('regisztracio', views.sign_up, name='signup'),
    path('felhasznalo-aktivalas/<str:uidb64>/<str:token>', views.activate_account, name='activate_account'),
    path('jelszovaltoztatas', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('szemelyes-adatok', views.personal_data, name='personal_data'),
    path('profil-torlese', views.DeleteProfileView.as_view(), name='delete_profile'),
    path('nyugdijas-kepzesek', views.PensionerCoursesListPage.as_view(), name='pensioner_courses'),
    path('altalanos-kepzesek', views.GeneralCoursesListPage.as_view(), name='general_courses'),
    path('kepzes/<slug:slug>', views.CoursePage.as_view(), name='course'),
    path('kepzes/<slug:slug>/jelentkezes', views.apply, name='apply'),
    path('adatnyilatkozat', views.PrivacyNoticePage.as_view(), name='privacy_notice'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
