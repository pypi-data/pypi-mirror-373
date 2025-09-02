from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate
from pytest_factoryboy import register
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.geography.tests.signals import (
    app_pre_migration as app_pre_migration_geography,
)
from wbhuman_resources.tests.signals import app_pre_migration as app_pre_migration_hr
from wbintegrator_office365.factories import (
    CallEventFactory,
    CallUserFactory,
    EventFactory,
    EventLogFactory,
    SubscriptionFactory,
    TenantUserFactory,
)

register(EventFactory)
register(EventLogFactory)
register(SubscriptionFactory)
register(TenantUserFactory)
register(CallUserFactory)
register(CallEventFactory)
register(UserFactory)

pre_migrate.connect(app_pre_migration_hr, sender=apps.get_app_config("wbintegrator_office365"))
pre_migrate.connect(app_pre_migration_geography, sender=apps.get_app_config("wbintegrator_office365"))
