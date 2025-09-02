import random

import factory
import pytz


class TenantUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "wbintegrator_office365.TenantUser"

    tenant_id = factory.Sequence(lambda n: "user_tenant_%d" % n)
    display_name = factory.Faker("name")
    mail = factory.Faker("email")
    phone = factory.Faker("phone_number")
    profile = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
    tenant_organization_id = factory.Faker("pystr")


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "wbintegrator_office365.Subscription"

    subscription_id = factory.Sequence(lambda n: "subscription%d" % n)
    expiration_date = factory.Faker("date_time_between", start_date="+2d", end_date="+3d", tzinfo=pytz.utc)
    change_type = factory.Faker("pystr")
    notification_url = factory.Faker("url")
    resource = factory.Faker("uri")
    application_id = factory.Faker("pystr")
    creator_id = factory.Faker("pystr")
    client_state = factory.Faker("pystr")
    latest_supported_tls_version = factory.Faker("pystr")
    notification_content_type = factory.Faker("pystr")
    odata_context = factory.Faker("pystr")
    encryption_certificate_id = factory.Faker("pystr")
    encryption_certificate = factory.Faker("pystr")
    include_resource_data = factory.Faker("pystr")
    notification_query_options = factory.Faker("pystr")
    tenant_user = factory.SubFactory(TenantUserFactory)


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "wbintegrator_office365.Event"

    uuid_event = factory.Sequence(lambda n: "UID%d" % n)
    id_event = factory.Sequence(lambda n: "ID%d" % n)
    # type = "CALLRECORD"
    subscription_id = factory.Sequence(lambda n: "subscription%d" % n)
    # change_type = "CREATED"  #"UPDATED"
    resource = factory.Faker("uri")
    tenant_user = factory.SubFactory(TenantUserFactory)


class EventLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "wbintegrator_office365.EventLog"

    last_event = factory.SubFactory(EventFactory)
    id_event = factory.Sequence(lambda n: "event%d" % n)


class CallUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "wbintegrator_office365.CallUser"

    acs_user = factory.Faker("pystr")
    splool_user = factory.Faker("pystr")
    encrypted = factory.Faker("pystr")
    on_premises = factory.Faker("pystr")
    acs_application_instance = factory.Faker("pystr")
    spool_application_instance = factory.Faker("pystr")
    application_instance = factory.Faker("pystr")
    application = factory.Faker("pystr")
    device = factory.Faker("pystr")
    tenant_user = factory.SubFactory(TenantUserFactory)
    is_guest = factory.Faker("pybool")
    is_phone = factory.Faker("pybool")


class CallEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "wbintegrator_office365.CallEvent"
        django_get_or_create = ["activity"]

    event = factory.SubFactory(EventFactory)
    version = random.randint(1, 4)
    type = factory.Faker("pystr")
    start = factory.Faker("date_time_between", start_date="+2d", end_date="+3d", tzinfo=pytz.utc)
    end = factory.Faker("date_time_between", start_date="+2d", end_date="+3d", tzinfo=pytz.utc)
    last_modified = factory.Faker("date_time_between", start_date="+4d", end_date="+5d", tzinfo=pytz.utc)
    join_web_url = factory.Faker("url")
    organizer = factory.SubFactory(CallUserFactory)
    activity = factory.SubFactory("wbcrm.factories.ActivityFactory")
    is_internal_call = factory.Faker("pybool")

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for participant in extracted:
                self.participants.add(participant)
