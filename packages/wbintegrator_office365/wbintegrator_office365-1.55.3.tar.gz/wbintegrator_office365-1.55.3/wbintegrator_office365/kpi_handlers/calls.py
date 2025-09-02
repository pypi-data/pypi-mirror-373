from typing import Type

from django.db.models import Q
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from wbcore import serializers
from wbcore.serializers.serializers import Serializer
from wbhuman_resources.models.kpi import KPI, KPIHandler
from wbhuman_resources.serializers import KPIModelSerializer

from wbintegrator_office365.models import CallEvent


class NumberOfCallKPIKPISerializer(KPIModelSerializer):
    call_area = serializers.ChoiceField(
        default="all",
        choices=[("only_internal", "Only Internal"), ("only_external", "Only External"), ("all", "All")],
    )
    person_participates = serializers.BooleanField(
        default=True,
        label="Participants of call/Meeting ",
        help_text="Calls/Meeting considered are related to the participants",
    )
    person_created = serializers.BooleanField(
        default=True,
        label="Organizer of call/Meeting ",
        help_text="Calls/Meeting considered are related to the organizer",
    )

    def update(self, instance, validated_data):
        call_area = validated_data.get(
            "call_area",
            instance.additional_data["serializer_data"].get("call_area", "all"),
        )

        person_participates = validated_data.get(
            "person_participates",
            instance.additional_data["serializer_data"].get("person_participates", True),
        )
        person_created = validated_data.get(
            "person_created",
            instance.additional_data["serializer_data"].get("person_created", True),
        )

        additional_data = instance.additional_data
        additional_data["serializer_data"]["call_area"] = call_area
        additional_data["serializer_data"]["person_participates"] = person_participates
        additional_data["serializer_data"]["person_created"] = person_created

        additional_data["list_data"] = instance.get_handler().get_list_data(additional_data["serializer_data"])
        validated_data["additional_data"] = additional_data

        return super().update(instance, validated_data)

    class Meta(KPIModelSerializer.Meta):
        fields = (
            *KPIModelSerializer.Meta.fields,
            "call_area",
            "person_participates",
            "person_created",
        )


class NumberOfCallKPI(KPIHandler):
    def get_name(self) -> str:
        return "Number of Calls/Meeting"

    def get_serializer(self) -> Type[Serializer]:
        return NumberOfCallKPIKPISerializer

    def annotate_parameters(self, queryset: QuerySet[KPI]) -> QuerySet[KPI]:
        return queryset.annotate(
            call_area=F("additional_data__serializer_data__call_area"),
            person_participates=F("additional_data__serializer_data__person_participates"),
            person_created=F("additional_data__serializer_data__person_created"),
            person_assigned=F("additional_data__serializer_data__person_assigned"),
        )

    def get_list_data(self, serializer_data: dict) -> list[str]:
        return [
            f"Call Area: {serializer_data['call_area']}",
            f"Person Participates: {serializer_data['person_participates']}",
            f"Person Created: {serializer_data['person_created']}",
        ]

    def get_display_grid(self) -> list[list[str]]:
        return [["call_area"] * 2, ["person_created", "person_participates"]]

    def evaluate(self, kpi: "KPI", evaluated_person=None, evaluation_date=None) -> int:
        persons = (
            [evaluated_person.id] if evaluated_person else kpi.evaluated_persons.all().values_list("id", flat=True)
        )
        serializer_data = kpi.additional_data.get("serializer_data")
        qs = CallEvent.objects.filter(
            start__gte=kpi.period.lower,
            end__lte=evaluation_date if evaluation_date else kpi.period.upper,
        )
        if (call_area := serializer_data.get("call_area")) and (call_area != "all"):
            if call_area == "only_internal":
                qs = qs.filter(is_internal_call=True)
            elif call_area == "only_external":
                qs = qs.filter(is_internal_call=False)

        condition = None
        if serializer_data.get("person_created") or serializer_data.get("person_created") is None:
            condition = Q(organizer__tenant_user__profile__in=persons)
        if serializer_data.get("person_participates") or serializer_data.get("person_participates") is None:
            condition = (
                (condition | Q(participants__tenant_user__profile__in=persons))
                if condition
                else Q(participants__tenant_user__profile__in=persons)
            )
        if condition:
            qs = qs.filter(condition)
        return qs.distinct().count()
