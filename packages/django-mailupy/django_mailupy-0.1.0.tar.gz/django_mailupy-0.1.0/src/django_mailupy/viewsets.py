try:
    from rest_framework import viewsets
    from .models import MailupyCredential
    from .serializers import MailupyCredentialSerializer
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from .client import DjangoMailupy
    from django.utils.translation import gettext_lazy as _
    from rest_framework import status
    from mailupy import MailupyException

    class MailupyCredentialViewSet(viewsets.ModelViewSet):
        queryset = MailupyCredential.objects.all()
        serializer_class = MailupyCredentialSerializer

        @action(detail=False, methods=['get'])
        def test_connection(self, request):
            try:
                client = DjangoMailupy(client_id="foo", client_secret="bar")
                client.get_lists()
                return Response({"status": _("Connection successful")}, status=status.HTTP_200_OK)
            except MailupyException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

except ImportError:
    MailupyCredentialViewSet = None
