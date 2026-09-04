import sys
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail, get_connection


class Command(BaseCommand):
    help = 'Tests and diagnoses live email sending configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            default='ketanwagh714@gmail.com',
            help='Recipient email address to test delivery'
        )

    def handle(self, *args, **options):
        recipient = options['to']
        self.stdout.write(self.style.NOTICE(f'[EMAIL TEST] Starting email diagnostics to {recipient}...'))
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
        self.stdout.write(f"  EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  EMAIL_HOST_PASSWORD: {'*** SET (' + str(len(settings.EMAIL_HOST_PASSWORD)) + ' chars)' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

        # Method 1: Django Backend
        self.stdout.write(self.style.NOTICE('\n[1] Testing via Django send_mail()...'))
        try:
            res = send_mail(
                subject='Aesthetic Store - Diagnostic Test 1',
                message='This is a diagnostic test via Django send_mail.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False
            )
            self.stdout.write(self.style.SUCCESS(f'  [SUCCESS] Django send_mail delivered {res} message(s)!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAILED] Django send_mail error: {e}'))

        # Method 2: Direct SSL Port 465
        self.stdout.write(self.style.NOTICE('\n[2] Testing Direct SSL on Port 465...'))
        try:
            user = settings.EMAIL_HOST_USER
            pwd = settings.EMAIL_HOST_PASSWORD
            if not user or not pwd:
                self.stdout.write(self.style.WARNING('  [SKIPPED] Missing EMAIL_HOST_USER or EMAIL_HOST_PASSWORD'))
                return

            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Aesthetic Store - Direct SSL Port 465 Test'
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = recipient
            msg.attach(MIMEText('This is a direct SSL 465 test message.', 'plain', 'utf-8'))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=12) as server:
                server.login(user, pwd)
                server.sendmail(user, [recipient], msg.as_string())
            self.stdout.write(self.style.SUCCESS('  [SUCCESS] Direct SSL Port 465 delivered message!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAILED] Direct SSL Port 465 error: {e}'))
