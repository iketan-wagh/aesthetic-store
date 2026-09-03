"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Automated Cloud Startup Migrations & Seeding
try:
    from django.core.management import call_command
    from django.db import connection
    
    table_names = connection.introspection.table_names()
    if 'products_product' not in table_names or 'django_session' not in table_names:
        print("[AUTO-MIGRATE] Fresh cloud database detected. Applying migrations...")
        call_command('migrate', interactive=False)
        print("[AUTO-MIGRATE] Seeding store catalog and admin superuser...")
        call_command('seed_data')
        print("[AUTO-MIGRATE] Setup complete! Store is ready.")
except Exception as err:
    print(f"[AUTO-MIGRATE] Startup migration note: {err}")
