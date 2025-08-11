import os

if os.environ.get('RENDER'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splitsmart.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splitsmart.settings.development')
