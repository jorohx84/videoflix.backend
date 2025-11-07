from django.core.mail import send_mail
from django.conf import settings

def send_activation_email(user_email, activation_token):
    subject = 'Activate your account'
    message = f'Please activate your account using this token: {activation_token}'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
