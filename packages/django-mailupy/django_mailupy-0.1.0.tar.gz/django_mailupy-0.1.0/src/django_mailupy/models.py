from django.db import models
from django.utils.translation import gettext_lazy as _


class MailupyCredentialManager(models.Manager):

    def get(self):
        obj, _ = self.get_or_create(id=1)
        return obj


class MailupyCredential(models.Model):
    username = models.CharField(_("MailUp Username"), max_length=150)
    mailup_password = models.CharField(_("MailUp Password"), max_length=128)
    objects = MailupyCredentialManager()

    class Meta:
        verbose_name = _("MailUp Credential")
        verbose_name_plural = _("MailUp Credentials")

    def __str__(self):
        return f"MailUp: {self.username}"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)




