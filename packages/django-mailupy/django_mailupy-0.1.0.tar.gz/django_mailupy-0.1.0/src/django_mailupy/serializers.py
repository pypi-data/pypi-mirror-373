try:
    from rest_framework import serializers
    from .models import MailupyCredential
    from django.contrib.auth.hashers import make_password


    class MailupyCredentialSerializer(serializers.ModelSerializer):
        
        class Meta:
            model = MailupyCredential
            fields = "__all__"

except ImportError:
    MailupyCredentialSerializer = None
