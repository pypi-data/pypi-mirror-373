import phonenumbers
from celery import shared_task
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import MultipleObjectsReturned
from django.db import models, transaction
from django.db.models import Case, CharField, F, Q, When
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from wbcore.contrib.directory.models import EmailContact, Person, TelephoneContact
from wbcore.contrib.notifications.utils import create_notification_type
from wbcore.models import WBModel

from wbintegrator_office365.importer import MicrosoftGraphAPI

from .tenant import TenantUser


class Event(WBModel):
    class Type(models.TextChoices):
        CALLRECORD = "CALLRECORD", "Call Record"
        CALENDAR = "CALENDAR", "Calendar"

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        permissions = [("administrate_event", "Can Administrate call and calendar events")]

    auto_inc_id = models.IntegerField(default=0)
    nb_received = models.IntegerField(default=0)

    uuid_event = models.CharField(
        max_length=1000,
        verbose_name="Event UID",
        help_text="UUID obtained from Microsoft",
        null=True,
        blank=True,
        unique=True,
    )
    id_event = models.CharField(
        max_length=1000,
        verbose_name="Event ID",
        help_text="Event ID obtained from Microsoft",
        null=True,
        blank=True,
        unique=True,
    )
    type = models.CharField(
        max_length=32, choices=Type.choices, null=True, blank=True, verbose_name="Type", default=""
    )
    subscription_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Subscription ID", default=""
    )
    change_type = models.CharField(max_length=255, null=True, blank=True, verbose_name="Change Type", default="")
    resource = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Resource", default="")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    changed = models.DateTimeField(auto_now=True, verbose_name="Changed")
    is_handled = models.BooleanField(default=True)
    data = models.JSONField(default=dict, null=True, blank=True)

    tenant_user = models.ForeignKey(
        "wbintegrator_office365.TenantUser",
        related_name="tenant_events",
        null=True,
        blank=True,
        on_delete=models.deletion.SET_NULL,
        verbose_name="Tenant User",
    )

    def save(self, *args, **kwargs):
        events = Event.objects.filter(id=self.id)
        object_list = Event.objects.order_by("auto_inc_id")
        if len(events) == 0:
            self.nb_received = 1
            if len(object_list) == 0:  # if there are no objects
                self.auto_inc_id = 1
            else:
                self.auto_inc_id = object_list.last().auto_inc_id + 1
        else:
            self.nb_received = events.first().nb_received + 1
            self.auto_inc_id = events.first().auto_inc_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"

    @classmethod
    def is_administrator(cls, user):
        user_groups = user.groups
        user_permission = user.user_permissions
        return (
            user_groups.filter(permissions__codename="administrate_event").exists()
            or user_permission.filter(codename="administrate_event").exists()
            or user.is_superuser
        )

    @classmethod
    def get_endpoint_basename(self):
        return "wbintegrator_office365:event"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbintegrator_office365:eventrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{id_str}} - {{uuid_event}}"

    def fetch_call(self):
        if data := MicrosoftGraphAPI().call(self.uuid_event):
            # call user organiser
            is_user = False
            is_guest = False
            is_phone = False
            organizer_id = None
            organizer_display_name = None
            organizer_organization_id = None
            if data.get("organizer.user.id") or (
                data.get("organizer.user.id") == "" and data.get("organizer.user.tenantId")
            ):
                is_user = True
                organizer_id = data.get("organizer.user.id")
                organizer_display_name = data.get("organizer.user.display_name")
                organizer_organization_id = data.get("organizer.user.tenantId")
            elif data.get("organizer.guest.id") or (
                data.get("organizer.guest.id") == "" and data.get("organizer.guest.tenantId")
            ):
                is_guest = True
                organizer_id = data.get("organizer.guest.id")
                organizer_display_name = data.get("organizer.guest.display_name")
                organizer_organization_id = data.get("organizer.guest.tenantId")
            elif data.get("organizer.phone.id") or (
                data.get("organizer.phone.id") == "" and data.get("organizer.phone.tenantId")
            ):
                is_phone = True
                organizer_id = data.get("organizer.phone.id")
                organizer_display_name = data.get("organizer.phone.display_name")
                organizer_organization_id = data.get("organizer.phone.tenantId")

            call_user_organizer = create_or_update_call_user(
                tenant_id=organizer_id,
                display_name=organizer_display_name,
                tenant_organization_id=organizer_organization_id,
                is_user=is_user,
                is_guest=is_guest,
                is_phone=is_phone,
                acs_user=data.get("organizer.acs_user"),
                splool_user=data.get("organizer.splool_user"),
                encrypted=data.get("organizer.encrypted"),
                on_premises=data.get("organizer.on_premises"),
                acs_application_instance=data.get("organizer.acs_application_instance"),
                spool_application_instance=data.get("organizer.spool_application_instance"),
                application_instance=data.get("organizer.application_instance"),
                application=data.get("organizer.application"),
                device=data.get("organizer.device"),
            )

            # CALL EVENT
            try:
                call, created = CallEvent.objects.update_or_create(
                    event=self,
                    defaults={
                        "version": data.get("version"),
                        "type": data.get("type"),
                        "modalities": data.get("modalities"),
                        "last_modified": data.get("last_modified"),
                        "start": data.get("start"),
                        "end": data.get("end"),
                        "join_web_url": data.get("join_web_url"),
                        "organizer": call_user_organizer,
                        "data": data,
                    },
                )
            except MultipleObjectsReturned:
                call = CallEvent.objects.filter(event=self).order_by("-pk")[0]
                CallEvent.objects.filter(event=self).exclude(id=call.id).delete()
                CallEvent.objects.filter(event=self).update(
                    version=data.get("version"),
                    type=data.get("type"),
                    modalities=data.get("modalities"),
                    last_modified=data.get("last_modified"),
                    start=data.get("start"),
                    end=data.get("end"),
                    join_web_url=data.get("join_web_url"),
                    organizer=call_user_organizer,
                    data=data,
                )

            # call user for all participants
            for participant in data.get("participants"):
                is_user = False
                is_guest = False
                is_phone = False
                participant_id = None
                participant_display_name = None
                participant_organization_id = None
                if participant.get("user"):
                    is_user = True
                    participant_id = participant.get("user").get("id")
                    participant_display_name = participant.get("user").get("displayName")
                    participant_organization_id = participant.get("user").get("tenantId")
                elif participant.get("guest"):
                    is_guest = True
                    participant_id = participant.get("guest").get("id")
                    participant_display_name = participant.get("guest").get("displayName")
                    participant_organization_id = participant.get("guest").get("tenantId")
                elif participant.get("phone"):
                    is_phone = True
                    participant_id = participant.get("phone").get("id")
                    participant_display_name = participant.get("phone").get("displayName")
                    participant_organization_id = participant.get("phone").get("tenantId")

                call_user = create_or_update_call_user(
                    tenant_id=participant_id,
                    display_name=participant_display_name,
                    tenant_organization_id=participant_organization_id,
                    is_user=is_user,
                    is_guest=is_guest,
                    is_phone=is_phone,
                    acs_user=participant.get("acsUser"),
                    splool_user=participant.get("spoolUser"),
                    encrypted=participant.get("encrypted"),
                    on_premises=participant.get("on_premises"),
                    acs_application_instance=participant.get("acsApplicationInstance"),
                    spool_application_instance=participant.get("spoolApplicationInstance"),
                    application_instance=participant.get("applicationInstance"),
                    application=participant.get("application"),
                    device=participant.get("device"),
                )
                call.participants.add(call_user)


class EventLog(WBModel):
    class Meta:
        verbose_name = "Event Log"
        verbose_name_plural = "Event Logs"

    last_event = models.ForeignKey(
        "Event",
        related_name="event_logs",
        verbose_name="Last Event",
        on_delete=models.deletion.CASCADE,
    )
    id_event = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Event ID")
    order_received = models.IntegerField(default=0)
    change_type = models.CharField(max_length=255, null=True, blank=True, verbose_name="Change Type", default="")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    changed = models.DateTimeField(auto_now=True, verbose_name="Changed")
    resource = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Resource", default="")
    is_handled = models.BooleanField(default=True)
    data = models.JSONField(default=dict, null=True, blank=True)

    @classmethod
    def get_endpoint_basename(self):
        return "wbintegrator_office365:eventlog"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbintegrator_office365:eventlogrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{last_event}} ({{order_received}})"


class CallUser(WBModel):
    acs_user = models.CharField(max_length=256, default="", null=True, blank=True)
    splool_user = models.CharField(max_length=256, default="", null=True, blank=True)
    encrypted = models.CharField(max_length=256, default="", null=True, blank=True)
    on_premises = models.CharField(max_length=256, default="", null=True, blank=True)
    acs_application_instance = models.CharField(max_length=256, default="", null=True, blank=True)
    spool_application_instance = models.CharField(max_length=256, default="", null=True, blank=True)
    application_instance = models.CharField(max_length=256, default="", null=True, blank=True)
    application = models.CharField(max_length=256, default="", null=True, blank=True)
    device = models.CharField(max_length=256, default="", null=True, blank=True)
    is_guest = models.BooleanField(default=False)
    is_phone = models.BooleanField(default=False)
    tenant_user = models.ForeignKey(
        "wbintegrator_office365.TenantUser",
        related_name="call_users",
        null=True,
        blank=True,
        on_delete=models.deletion.SET_NULL,
    )

    def __str__(self):
        if self.tenant_user:
            if self.tenant_user.profile:
                return f"{self.tenant_user.profile.computed_str}"
            elif self.tenant_user.mail or self.tenant_user.display_name:
                mail = self.tenant_user.mail if self.tenant_user.mail else self.tenant_user.id
                return f"{self.tenant_user.display_name}({mail})"
            else:
                return f"{self.tenant_user.tenant_id}"
        return f"{self.id}"

    @classmethod
    def annotated_queryset(cls, qs):
        return qs.annotate(
            tenant_user_str=Case(
                When(tenant_user__isnull=True, then=F("id_str")),
                default=F("tenant_user__profile_str"),
                output_field=CharField(),
            ),
        )

    @classmethod
    def get_endpoint_basename(cls):
        return "wbintegrator_office365:calluser"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbintegrator_office365:calluserrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{tenant_user_str}}"


class CallEvent(WBModel):
    class Meta:
        verbose_name = "Call Event"
        verbose_name_plural = "Calls Events"

        notification_types = [
            create_notification_type(
                "wbintegrator_office365.callevent.call_summary",
                "Call Summary",
                "Call Summary",
                False,
                False,
                True,
                is_lock=True,
            ),
            create_notification_type(
                "wbintegrator_office365.callevent.notify",
                "Call Event Notification",
                "Sends a notification when something happens with a Call Event triggered from Office 365",
                True,
                True,
                False,
            ),
        ]

    event = models.OneToOneField(to="wbintegrator_office365.Event", related_name="calls", on_delete=models.CASCADE)
    version = models.CharField(max_length=256, null=True, blank=True, verbose_name="Version", default="")
    type = models.CharField(max_length=256, null=True, blank=True, verbose_name="Type", default="")
    modalities = ArrayField(
        models.CharField(max_length=256), blank=True, null=True, verbose_name="Modalities", default=list
    )
    last_modified = models.DateTimeField(null=True, blank=True, verbose_name="Last Modified")
    start = models.DateTimeField(null=True, blank=True, verbose_name="Start")
    end = models.DateTimeField(null=True, blank=True, verbose_name="End")
    join_web_url = models.CharField(max_length=256, null=True, blank=True, verbose_name="Join Web Url", default="")
    organizer = models.ForeignKey(
        CallUser, verbose_name="Organizer", null=True, blank=True, on_delete=models.deletion.SET_NULL
    )
    participants = models.ManyToManyField(
        CallUser, blank=True, related_name="participates", verbose_name="Call participants"
    )
    activity = models.OneToOneField(
        "wbcrm.Activity",
        related_name="call_event",
        null=True,
        blank=True,
        on_delete=models.deletion.SET_NULL,
        verbose_name="Activity",
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    is_internal_call = models.BooleanField(null=True, blank=True, verbose_name="Is internal call")
    data = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"{self.event.id} ({self.start} - {self.end})"

    def check_call_is_internal_call(self, caller_id=None):
        is_internal = True
        callers = self.participants.all()

        if caller_id:
            is_internal = self.is_internal_call if self.is_internal_call is not None else is_internal
            callers = callers.filter(id=caller_id)

        for caller in callers:
            if (tenant_user := caller.tenant_user) and (person := tenant_user.profile) and person.is_internal:
                is_internal &= True
            else:
                is_internal &= False

        self.is_internal_call = is_internal
        self.save()

    @classmethod
    def get_endpoint_basename(cls):
        return "wbintegrator_office365:callevent"

    @classmethod
    def get_representation_endpoint(cls):
        return "wbintegrator_office365:calleventrepresentation-list"

    @classmethod
    def get_representation_value_key(cls):
        return "id"

    @classmethod
    def get_representation_label_key(cls):
        return "{{event.id}} ({{start}} - {{end}})"


# search person by phone if not found
def get_person_by_phone(phone):
    persons = Person.objects.none()
    phone_numbers = None
    try:
        parser_number = phonenumbers.parse(phone, "CH")
        phone_numbers = (
            phonenumbers.format_number(parser_number, phonenumbers.PhoneNumberFormat.E164)
            if parser_number
            else "".join(phone.split())
        )
        if phone and phone_numbers:
            phone2 = "".join(phone.replace("+41", "").split())
            entries = (
                TelephoneContact.objects.filter(
                    Q(number__contains=phone) | Q(number__contains=phone2) | Q(number__contains=phone_numbers)
                )
                .values("entry")
                .distinct()
            )
            persons = Person.objects.filter(id__in=entries)
    except Exception as e:
        print(e, phone)  # noqa: T201
    return persons, phone_numbers


def fetch_tenantusers():
    datum = MicrosoftGraphAPI().users()
    count_added = 0
    if datum:
        for data in datum:
            # username = user.get("email")
            # if user.get("display_name") and user.get("id"):
            #     username = re.sub(' +', ' ', user.get("display_name").lower()).replace(",", "").replace(" ", "-").strip()
            tenant_id = data.get("id")
            display_name = data.get("display_name")
            mail = data.get("mail") if data.get("mail") else data.get("user_principal_name")
            phone = (
                next(iter(data.get("business_phones") or []), None)
                if data.get("business_phones")
                else data.get("mobile_phone")
            )
            # print(display_name,"/", mail,"/", phone,"/", data.get("given_name"),"/", data.get("surname"))
            # 1) search person by email
            entries = EmailContact.objects.filter(address=mail).values("entry").distinct()
            persons = Person.objects.filter(id__in=entries)
            phone_numbers = None
            # 2) search person by phone if not found
            if persons.count() == 0 and phone:
                persons, phone_numbers = get_person_by_phone(phone)
            # 3) search person by surname and given_name if not found
            if persons.count() == 0 and data.get("surname") and data.get("given_name"):
                persons = Person.objects.filter(
                    first_name__icontains=data.get("given_name"), last_name__icontains=data.get("surname")
                ).distinct()
            # get the first person found otherwise it will be None
            person = None
            if persons.count() > 0:
                person = persons.first()
            else:
                first_name, last_name = (
                    display_name.split(" ") if len(display_name.split(" ")) == 2 else ["AnonymousUser", tenant_id]
                )
                qs_person = Person.objects.filter(first_name=first_name, last_name=last_name)
                if qs_person.count() > 0:
                    person = qs_person.first()
                # person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
                # if mail:
                #     EmailContact.objects.get_or_create(
                #         primary=True,
                #         entry=person,
                #         address=mail,
                #     )
                # if phone_numbers:
                #     TelephoneContact.objects.get_or_create(
                #         entry=person,
                #         number=phone_numbers
                #     )

            # update or create tenant user
            tenantuser, created = TenantUser.objects.update_or_create(
                tenant_id=tenant_id,
                defaults={"display_name": display_name, "mail": mail, "phone": phone, "profile": person},
            )
            if created:
                count_added += 1
    return datum, count_added


def create_or_update_call_user(
    tenant_id=None,
    display_name=None,
    tenant_organization_id=None,
    is_user=False,
    is_guest=False,
    is_phone=False,
    acs_user=None,
    splool_user=None,
    encrypted=None,
    on_premises=None,
    acs_application_instance=None,
    spool_application_instance=None,
    application_instance=None,
    application=None,
    device=None,
):
    tenant_user = None
    # get or create Person
    if tenant_id:
        # search person by tenant id
        qs_tenant_user = TenantUser.objects.filter(tenant_id=tenant_id)
        if qs_tenant_user.count() == 0:
            first_name, last_name = ["AnonymousUser", tenant_id]
            phone_numbers = None
            persons = Person.objects.none()
            person = None
            # search person by display name  (also for phone anonymous) # the phone number obtained is "anonymous"
            if is_user or is_guest or (is_phone and tenant_id == "anonymous"):
                # first_name, last_name = display_name.split(" ") if len(display_name.split(" ")) == 2 and display_name != "Guest User" and display_name != "External user" else first_name, last_name
                # Sometimes we obtained "Guest User" or "External user" for certains external user
                if display_name:
                    if (
                        len(display_name.strip(" ").split(" ")) == 2
                        and display_name.lower() != "guest user"
                        and display_name.lower() != "external user"
                    ):
                        first_name, last_name = display_name.strip(" ").split(" ")
                    else:
                        first_name = display_name

                persons = Person.objects.filter(
                    first_name__icontains=first_name, last_name__icontains=last_name
                ).distinct()
            # search person by phone
            elif is_phone and tenant_id != "anonymous":
                persons, phone_numbers = get_person_by_phone(tenant_id)

            if persons.count():
                person = persons.first()
            else:
                qs_person = Person.objects.filter(first_name=first_name, last_name=last_name)
                if qs_person.count() > 0:
                    person = qs_person.first()
                # person, created = Person.objects.get_or_create(first_name=first_name, last_name=last_name)
                # if phone_numbers:
                #     TelephoneContact.objects.get_or_create(
                #         entry=person,
                #         number=phone_numbers
                #     )
                #     phone_numbers = tenant_id

            tenant_user, created = TenantUser.objects.get_or_create(
                tenant_id=tenant_id, defaults={"phone": phone_numbers, "display_name": display_name, "profile": person}
            )
        else:
            tenant_user = TenantUser.objects.get(tenant_id=tenant_id)

        if tenant_organization_id:
            tenant_user.tenant_organization_id = tenant_organization_id
            tenant_user.save()
    else:
        tenant_user, _ = TenantUser.objects.get_or_create(
            tenant_id=tenant_id, display_name=display_name, tenant_organization_id=tenant_organization_id
        )

    call_user, created = CallUser.objects.update_or_create(
        acs_user=acs_user,
        splool_user=splool_user,
        encrypted=encrypted,
        on_premises=on_premises,
        acs_application_instance=acs_application_instance,
        spool_application_instance=spool_application_instance,
        application_instance=application_instance,
        application=application,
        device=device,
        tenant_user=tenant_user,
        is_phone=is_phone,
        is_guest=is_guest,
    )
    return call_user


@shared_task
def handle_event_from_webhook(id_event, notification):
    with transaction.atomic():
        from wbintegrator_office365.models.subscription import Subscription

        if (
            (subscription_id := notification.get("subscription_id"))
            and (_subscription := Subscription.objects.filter(subscription_id=subscription_id).first())
            and _subscription.type_resource == Subscription.TypeResource.CALLRECORD
        ):
            event, _ = Event.objects.update_or_create(
                uuid_event=id_event,
                defaults={
                    "type": _subscription.type_resource,
                    "subscription_id": subscription_id,
                    "change_type": notification.get("change_type"),
                    "data": notification,
                    "resource": notification.get("resource"),
                    "is_handled": True,
                    "tenant_user": _subscription.tenant_user,
                },
            )
            event.fetch_call()


@receiver(m2m_changed, sender=CallEvent.participants.through)
def post_save_participant_event(sender, instance, action, reverse, pk_set, *args, **kwargs):
    if action == "post_add" and not reverse:
        for participant_id in pk_set:
            instance.check_call_is_internal_call(participant_id)
    elif action == "post_remove" and not reverse:
        instance.check_call_is_internal_call()
