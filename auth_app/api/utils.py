from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
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

def send_activation_email(user, activation_token):
    print(user)
    subject = 'Confirm your email'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]
   
    text_content = f'Please activate your account using this token: {activation_token}'
    html_content = f"""
    <html>
      <body>
        <h2>Dear {user.email},</h2>
        <p>Thank you for registering with Videoflix. to complete your registration and verify your email adress, please click the link below:</p>
       
        <button>Activate account</button>
    
        <a href="https://example.com/activate/{activation_token}" 
           style="background-color: #1E90FF; color: white; padding: 10px 20px; 
                  text-decoration: none; border-radius: 5px;">
           Konto aktivieren
        </a>
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