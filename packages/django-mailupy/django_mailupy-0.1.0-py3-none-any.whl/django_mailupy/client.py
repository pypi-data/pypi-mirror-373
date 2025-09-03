from .models import MailupyCredential
from mailupy import Mailupy


class DjangoMailupy(Mailupy):
    """
    Wrapper trasparente per il client Mailupy.
    Recupera le credenziali dal DB e inizializza Mailupy.
    Tutti i metodi del client sono esposti.
    """

    def __init__(self, client_id=None, client_secret=None):
        credentials = MailupyCredential.objects.get()
        super().__init__(
            username=credentials.username,
            password=credentials.mailup_password,
            client_id=client_id,
            client_secret=client_secret
        )