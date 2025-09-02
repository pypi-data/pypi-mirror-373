from django.contrib.auth import views as django_views
from django.urls import path

from cms_qe_auth.forms import PasswordResetFormWithEmailExistenceCheck

from . import views as cms_qe_auth_views

urlpatterns = [
    path('login/', django_views.LoginView.as_view(template_name='cms_qe/auth/login.html'), name='login'),
    path('logout/', django_views.LogoutView.as_view(template_name='cms_qe/auth/logged_out.html'), name='logout'),
    path('password_change/', django_views.PasswordChangeView.as_view(
        template_name='cms_qe/auth/password_change_form.html'), name='password_change'),
    path('password_change/done/', django_views.PasswordChangeDoneView.as_view(
        template_name='cms_qe/auth/password_change_done.html'), name='password_change_done'),
    path('password_reset/', django_views.PasswordResetView.as_view(
        template_name='cms_qe/auth/password_reset_form.html',
        email_template_name='cms_qe/auth/password_reset_email.txt',
        html_email_template_name='cms_qe/auth/password_reset_email.html',
        form_class=PasswordResetFormWithEmailExistenceCheck,
    ), name='password_reset'),
    path('password_reset/done/', django_views.PasswordResetDoneView.as_view(
        template_name='cms_qe/auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<slug:uidb64>/<slug:token>/', django_views.PasswordResetConfirmView.as_view(
        template_name='cms_qe/auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', django_views.PasswordResetCompleteView.as_view(
        template_name='cms_qe/auth/password_reset_complete.html'), name='password_reset_complete'),
    path('register/', cms_qe_auth_views.register, {'template_name': 'cms_qe/auth/register.html'}, name='register'),
    path('activate/<slug:uidb64>/<slug:token>/', cms_qe_auth_views.activate, {
        'template_name_complete': 'cms_qe/auth/email_confirmation_complete.html',
        'template_name_fail': 'cms_qe/auth/email_confirmation_fail.html',
    }, name='activate'),
]
