import math
from datetime import date, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q
from wbcore.contrib.directory.models import Person
from wbcore.contrib.notifications.dispatch import send_notification

from wbintegrator_office365.importer import MicrosoftGraphAPI
from wbintegrator_office365.models.event import CallEvent
from wbintegrator_office365.models.subscription import Subscription


@shared_task
def send_call_summary(to_emails: list, profile_ids: list, offset: int = 1):
    for to_email in to_emails:
        if (recipient := get_user_model().objects.filter(email=to_email).first()) and (
            profiles := Person.objects.filter(id__in=profile_ids)
        ):
            _day = date.today() - timedelta(days=offset)

            message = "<html><head><style> #summery_table tr:nth-child(even){background-color: #f2f2f2;}</style></head><body>"

            for profile in profiles:
                call_events = CallEvent.objects.filter(
                    participants__tenant_user__profile__computed_str__icontains=profile.computed_str,
                    start__date=_day,
                    end__date=_day,
                ).order_by("start")

                message += f"<p> \
                                <span><b> {profile.computed_str} </b></span><br/> \
                                <span>Date: <b>{_day}</b> </span><br/> \
                                <span>Total number of calls: <b>{call_events.count()}</b> </span> \
                            </p>"
                if call_events.count():
                    message += "<table id='summery_table' style='border-collapse: collapse;'> \
                                <tr style='color: white; background-color: #1868ae;'> \
                                    <th style='border: 1px solid #ddd;padding: 10px 7px;' >Start</th> \
                                    <th style='border: 1px solid #ddd;padding: 10px 7px;' >End</th> \
                                    <th style='border: 1px solid #ddd;padding: 10px 7px;' >Duration (min)</th> \
                                    <th style='border: 1px solid #ddd;padding: 10px 7px;' >Organized by</th> \
                                    <th style='border: 1px solid #ddd;padding: 10px 7px;' >Participants</th> \
                                </tr>"
                    for call in call_events:
                        participants = ""
                        count = 0
                        total_participants = call.participants.exclude(tenant_user__profile=profile).count()
                        for participant in call.participants.exclude(tenant_user__profile=profile):
                            count += 1
                            participants += f"{participant.__str__()}"
                            if count < total_participants:
                                participants += ", "

                        delta_in_minutes = divmod((call.end - call.start).total_seconds(), 60)
                        _duration = f"{math.floor(delta_in_minutes[0])}:{math.floor(delta_in_minutes[1])}"
                        message += f"<tr> \
                                    <td style='border: 1px solid #ddd;padding: 2px;' >{call.start.astimezone().strftime('%Y-%m-%d %H:%M:%S')}</td> \
                                    <td style='border: 1px solid #ddd;padding: 2px;' >{call.end.astimezone().strftime('%Y-%m-%d %H:%M:%S')}</td> \
                                    <td style='border: 1px solid #ddd;padding: 0px;' text-align:center;><b>{_duration}</b></td> \
                                    <td style='border: 1px solid #ddd;padding: 2px;' ><b>{call.organizer.__str__()}</b></td> \
                                    <td style='border: 1px solid #ddd;padding: 2px;' >{participants}</td> \
                                </tr>"
                    message += "</table><br/>"

            message += "</body></html>"

        send_notification(
            code="wbintegrator_office365.callevent.call_summary",
            title=f"Call summary - {_day}",
            body=message,
            user=recipient,
        )


@shared_task
def notify_no_active_call_record_subscription(to_email):
    recipient = get_user_model().objects.filter(email=to_email)
    ms_subscriptions = [elt.get("id") for elt in MicrosoftGraphAPI().subscriptions()]
    qs_subscriptions = Subscription.objects.filter(
        Q(is_enable=True) & Q(subscription_id__isnull=False) & Q(type_resource=Subscription.TypeResource.CALLRECORD)
    )
    enable_subcriptions = qs_subscriptions.filter(subscription_id__in=ms_subscriptions)
    if recipient.exists() and (
        len(ms_subscriptions) == 0 or (qs_subscriptions.count() > 0 and enable_subcriptions.count() == 0)
    ):
        _day = date.today()
        send_notification(
            code="wbintegrator_office365.callevent.notify",
            title=f"No active Call Record subscriptions in Microsoft - {_day}",
            body=f"""<p>There are currently no active Call record subscriptions in Microsoft, so we are no longer receiving calls, Please check</p>
            <ul>
                <li>Number of subscriptions on Microsoft: <b>{len(ms_subscriptions)}</b></li>
                <li>Number of Call subscriptions: <b>{qs_subscriptions.count()}</b></li>
                <li>Number of enabled calling subscriptions: <b>{enable_subcriptions.count()}</b></li>

            </ul>
            """,
            user=recipient.first(),
        )


@shared_task
def periodic_resubscribe_task():
    for subscription in Subscription.objects.filter(
        is_enable=True, type_resource=Subscription.TypeResource.CALLRECORD, subscription_id__isnull=False
    ):
        subscription.resubscribe()
