from django.conf import settings
from django.db import models
from wbcore.models import WBModel


class TenantUser(WBModel):
    class Meta:
        verbose_name = "Tenant User"
        verbose_name_plural = "Tenant Users"

    tenant_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="User tenant ID", default="")
    display_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Display Name", default="")
    tenant_organization_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Organization tenant ID"
    )
    mail = models.CharField(max_length=255, null=True, blank=True, default="")
    phone = models.CharField(max_length=255, null=True, blank=True, default="")
    profile = models.ForeignKey(
        "directory.Person",
        related_name="tenant_user",
        null=True,
        blank=True,
        on_delete=models.deletion.SET_NULL,
        verbose_name="User",
    )
    is_internal_organization = models.BooleanField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.tenant_organization_id and (org_id := getattr(settings, "WBINTEGRATOR_OFFICE365_TENANT_ID", None)):
            self.is_internal_organization = self.tenant_organization_id == org_id
        super().save(*args, **kwargs)

    def __str__(self):
        if self.profile:
            name_tenant = f"{self.profile.computed_str}"
        elif self.mail or self.display_name:
            mail = self.mail if self.mail else self.id
            name_tenant = f"{self.display_name}({mail})"
        elif self.tenant_id:
            name_tenant = f"{self.tenant_id}"
        elif self.tenant_organization_id:
            name_tenant = f"company-{self.tenant_organization_id}"
        else:
            name_tenant = f"{self.id}"
        status = "Internal" if self.is_internal_organization else "External"
        return f"{name_tenant} ({status})"

    @classmethod
    def get_endpoint_basename(cls):
        return "wbintegrator_office365:tenantuser"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbintegrator_office365:tenantuserrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{profile_str}}({{id_str}})"
