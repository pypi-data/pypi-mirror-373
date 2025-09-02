from celery import chain, shared_task
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from wbcore.models import WBModel

from wbintegrator_office365.importer import MicrosoftGraphAPI


class Subscription(WBModel):
    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    class TypeResource(models.TextChoices):
        CALLRECORD = "CALLRECORD", "Call Record"
        CALENDAR = "CALENDAR", "Calendar"

    is_enable = models.BooleanField(default=True)
    subscription_id = models.CharField(max_length=255, null=True, blank=True)
    change_type = models.CharField(max_length=255, null=True, blank=True)
    notification_url = models.CharField(max_length=255, null=True, blank=True)
    resource = models.CharField(max_length=255, null=True, blank=True)
    type_resource = models.CharField(
        max_length=32,
        choices=TypeResource.choices,
        default=TypeResource.CALLRECORD,
        verbose_name="Type of the resource",
    )
    tenant_user = models.ForeignKey(
        "wbintegrator_office365.TenantUser",
        related_name="subscriptions",
        null=True,
        blank=True,
        on_delete=models.deletion.SET_NULL,
        verbose_name="Tenant User",
    )
    expiration_date = models.DateTimeField(null=True, blank=True, verbose_name="Expiration Date")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    application_id = models.CharField(null=True, blank=True, max_length=255)
    creator_id = models.CharField(null=True, blank=True, max_length=255)
    client_state = models.CharField(null=True, blank=True, max_length=255)
    latest_supported_tls_version = models.CharField(null=True, blank=True, max_length=255)
    notification_content_type = models.CharField(null=True, blank=True, max_length=255)
    odata_context = models.CharField(null=True, blank=True, max_length=255)
    encryption_certificate_id = models.CharField(null=True, blank=True, max_length=255)
    encryption_certificate = models.CharField(null=True, blank=True, max_length=255)
    include_resource_data = models.CharField(null=True, blank=True, max_length=255)
    notification_query_options = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return f"{self.subscription_id}: {self.expiration_date}"

    def resubscribe(self) -> None:
        if self.subscription_id and (data := MicrosoftGraphAPI()._renew_subscription(self.subscription_id)):
            Subscription.objects.filter(id=self.id).update(
                expiration_date=data.get("expiration"), notification_url=data.get("notification_url")
            )

    @classmethod
    def get_endpoint_basename(self):
        return "wbintegrator_office365:subscription"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbintegrator_office365:subscriptionrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{subscription_id}}: {{expiration_date}}"


@shared_task
def subscribe(instance_id, resource, minutes=4230, change_type="created, updated"):
    with transaction.atomic():
        data = MicrosoftGraphAPI()._subscribe(resource, minutes, change_type=change_type)
        if data.get("id"):
            instance = Subscription.objects.get(id=instance_id)
            if instance.type_resource == Subscription.TypeResource.CALLRECORD:
                instance.tenant_user = None
            instance.subscription_id = data.get("id")
            instance.change_type = data.get("change_type")
            instance.notification_url = data.get("notification_url")
            instance.resource = data.get("resource")
            instance.expiration_date = data.get("expiration")
            instance.application_id = data.get("application_id")
            instance.creator_id = data.get("creator_id")
            instance.client_state = data.get("client_state")
            instance.latest_supported_tls_version = data.get("latest_supported_tls_version")
            instance.notification_content_type = data.get("notification_content_type")
            instance.odata_context = data.get("odata_context")
            instance.encryption_certificate_id = data.get("encryption_certificate_id")
            instance.encryption_certificate = data.get("encryption_certificate")
            instance.include_resource_data = data.get("include_resource_data")
            instance.notification_query_options = data.get("notification_query_options")
            instance.save()


@shared_task
def unsubscribe(subscription_id):
    if subscription_id:
        MicrosoftGraphAPI()._unsubscribe(subscription_id)


@shared_task
def verification_subscriptions(instance_id: int):
    with transaction.atomic():
        ms_subscriptions = [elt.get("id") for elt in MicrosoftGraphAPI().subscriptions()]
        qs_subscriptions = Subscription.objects.filter(Q(id=instance_id) & Q(subscription_id__isnull=False))
        qs_subscriptions.filter(~Q(subscription_id__in=ms_subscriptions)).update(is_enable=False)


@shared_task
def resubscribe_as_task(instance_id: int):
    subscription = Subscription.objects.get(id=instance_id)
    subscription.resubscribe()


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance, created, **kwargs):
    if (created and instance.is_enable) or (instance.is_enable and not instance.subscription_id):
        # Subscription to Call Event
        if instance.type_resource == Subscription.TypeResource.CALLRECORD and not instance.expiration_date:
            transaction.on_commit(
                lambda: chain(
                    subscribe.si(instance.id, "/communications/callRecords"),
                    verification_subscriptions.si(instance.id),
                ).apply_async()
            )
    elif not instance.is_enable and instance.subscription_id:
        transaction.on_commit(
            lambda: chain(
                unsubscribe.si(instance.subscription_id), verification_subscriptions.si(instance.id)
            ).apply_async()
        )


@receiver(post_delete, sender=Subscription)
def post_delete_subscription(sender, instance, **kwargs):
    unsubscribe.delay(instance.subscription_id)
