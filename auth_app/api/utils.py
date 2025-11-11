from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
# def send_activation_email(user_email, activation_token):
#     subject = 'Confirm your email'
#     message = f'Please activate your account using this token: {activation_token}'
#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,
#         [user_email],
#         fail_silently=False,
#     )

def send_activation_email(user):
    print(user)
    subject = 'Confirm your email'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"http://localhost:8000{reverse('activate', kwargs={'uidb64': uidb64, 'token': token})}"
    text_content = f'Please activate your account using this token: {token}'
    html_content = f"""
    <html>
    <body style="font-family: 'Helvetica', Arial, sans-serif; color: #333; line-height: 1.6;">
        <img src="https://127.0.0.1:5500/assets/icons/logo_icon.svg" alt="Videoflix Logo" style="width:200px; margin-bottom:20px;" />
        <h2>Dear {user.email},</h2>
        <p>Thank you for registering with Videoflix. To complete your registration and verify your email address, please click the link below:</p>
    
        <a href="{activation_link}" 
        style="background-color: #1E90FF; color: white; padding: 10px 20px; 
                text-decoration: none; border-radius: 100px; margin-top: 32px; margin-bottom: 32px">
        Activate Account
        </a>

        <p>If you did not create an account with us, please disregard this email</p> 
        <p>Best regards,</p>
        <p>Your Videoflix Team</p>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

User = get_user_model()
def activate_user(uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        print("Found user:", user.email)
    except Exception as e:
        print("Decode/Get user failed:", e)
        return None

    print("Token:", token)
    print("Check token:", default_token_generator.check_token(user, token))
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