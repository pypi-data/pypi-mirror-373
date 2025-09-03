from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from .models import MailupyCredential


@admin.register(MailupyCredential)
class MailupyCredentialAdmin(admin.ModelAdmin):
    list_display = ("username",)
    readonly_fields = ()
    fieldsets = (
        (None, {
            'fields': ('username', 'mailup_password')
        }),
    )

    def has_add_permission(self, request):
        return not MailupyCredential.objects.exists()

    def changelist_view(self, request, extra_context=None):
        if MailupyCredential.objects.exists():
            obj = MailupyCredential.objects.get()
            return redirect(reverse('admin:django_mailupy_mailupycredential_change', args=[obj.id]))
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        if change:
            messages.success(request, _("Credenziali aggiornate con successo."))
        else:
            messages.success(request, _("Credenziali salvate con successo."))
        super().save_model(request, obj, form, change)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    