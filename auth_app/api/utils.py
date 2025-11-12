from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django_rq import job
from email.mime.image import MIMEImage
import os
# def send_activation_email(user):
#     print(user)
#     subject = 'Confirm your email'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to = [user.email]
#     uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#     token = default_token_generator.make_token(user)
#     activation_link = f"http://localhost:8000{reverse('activate', kwargs={'uidb64': uidb64, 'token': token})}"
#     text_content = f'Please activate your account using this token: {token}'
#     html_content = f"""
#     <html>
#     <body style="font-family: 'Helvetica', Arial, sans-serif; color: #333; line-height: 1.6;">
#         <img src="https://127.0.0.1:5500/assets/icons/logo_icon.svg" alt="Videoflix Logo" style="width:200px; margin-bottom:20px;" />
#         <h2>Dear {user.email},</h2>
#         <p>Thank you for registering with Videoflix. To complete your registration and verify your email address, please click the link below:</p>
    
#         <a href="{activation_link}" 
#         style="background-color: #1E90FF; color: white; padding: 10px 20px; 
#                 text-decoration: none; border-radius: 100px; margin-top: 32px; margin-bottom: 32px">
#         Activate Account
#         </a>

#         <p>If you did not create an account with us, please disregard this email</p> 
#         <p>Best regards,</p>
#         <p>Your Videoflix Team</p>
#     </body>
#     </html>
#     """

#     msg = EmailMultiAlternatives(subject, text_content, from_email, to)
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()

def send_activation_email(user):
    subject = 'Confirm your email'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    # UID und Token für Aktivierungslink
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"http://localhost:8000{reverse('activate', kwargs={'uidb64': uidb64, 'token': token})}"

    text_content = f'Please activate your account using this token: {token}'

    # HTML mit CID-Bild
    html_content = f"""
    <html>
      <body style="font-family: Helvetica, Arial, sans-serif; color: #333; line-height:1.6;">
        <div style="text-align:center; margin-bottom: 20px;">
          <img src="cid:logo_image" alt="Videoflix Logo" style="width:200px;" />
        </div>
        <h2>Dear {user.email},</h2>
        <p>Thank you for registering with Videoflix. To complete your registration and verify your email address, please click the link below:</p>
        <p style="text-align:center; margin:32px 0;">
          <a href="{activation_link}" 
             style="background-color:#1E90FF; color:white; padding:12px 24px; text-decoration:none; border-radius:30px; display:inline-block;">
            Activate Account
          </a>
        </p>
        <p>If you did not create an account with us, please disregard this email.</p>
        <p>Best regards,<br>Your Videoflix Team</p>
      </body>
    </html>
    """

    # E-Mail erstellen
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")

    # Bild aus dem Projekt einfügen (z.B. PNG statt SVG für bessere Kompatibilität)
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo_icon.png')  # Pfad zum Bild
    with open(logo_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<logo_image>')  # Muss genau mit cid:logo_image im HTML übereinstimmen
        img.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
        msg.attach(img)

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
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # Link zum Frontend oder direkt zum API-Endpunkt
    reset_link = f"http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    
    subject = "Reset your Videoflix password"
    text_content = f"Please reset your password using the following link: {reset_link}"
    
    html_content = f"""
    <html>
      <body style="font-family: Helvetica, Arial, sans-serif; color: #333;">
 
        <h2>Hello,</h2>
        <p>We recently recieved a request to reset your password. If you made this request, please click on the following link to reset your password:</p>
       
          <a href="{reset_link}" style="background-color:#1E90FF; color:white; padding:12px 24px;
             text-decoration:none; border-radius:30px; display:inline-block;">
            Reset Password
          </a>
       
        <p>Please note that for security reasons, this link is only valid for 24 hours</p>
        <p>If you did not request a password reset, please ignore this mail.</p>
        <p>Best regards,<br>Your Videoflix Team</p>
        <div style="margin-bottom: 20px;">
          <img src="https://yourdomain.com/static/images/logo_icon.png" 
               alt="Videoflix Logo" style="width:150px;" />
        </div>
      </body>
    </html>
    """
    
    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@job
def send_password_reset_email_task(user_id):
    try:
        user = User.objects.get(pk=user_id)
        send_password_reset_email(user)
    except User.DoesNotExist:
        pass