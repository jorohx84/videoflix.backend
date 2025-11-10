from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

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

User = get_user_model()
def activate_user(uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return user
    return None

def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

    subject = "Passwort zurücksetzen"
    message = (
        f"Hallo {user.username},\n\n"
        f"Klicke auf den folgenden Link, um dein Passwort zurückzusetzen:\n{reset_link}\n\n"
        f"Wenn du das nicht angefordert hast, ignoriere bitte diese E-Mail."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def send_password_reset_email_task(user_id):
    try:
        user = User.objects.get(pk=user_id)
        send_password_reset_email(user)
    except User.DoesNotExist:
        pass