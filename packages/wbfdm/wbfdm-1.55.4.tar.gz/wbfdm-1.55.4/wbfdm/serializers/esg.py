from wbcore import serializers

from wbfdm.enums import (
    ESGControveryFlag,
    ESGControverySeverity,
    ESGControveryStatus,
    ESGControveryType,
)


class InstrumentControversySerializer(serializers.Serializer):
    id = serializers.PrimaryKeyCharField()
    headline = serializers.TextField()
    narrative = serializers.TextField()
    source = serializers.CharField()
    status = serializers.ChoiceField(choices=ESGControveryStatus.choices)
    type = serializers.ChoiceField(choices=ESGControveryType.choices)
    assessment = serializers.ChoiceField(choices=ESGControverySeverity.choices)
    response = serializers.TextField()
    review = serializers.DateField()
    initiated = serializers.DateField()
    flag = serializers.ChoiceField(choices=ESGControveryFlag.choices)

    class Meta:
        fields = (
            "id",
            "headline",
            "narrative",
            "source",
            "status",
            "type",
            "assessment",
            "response",
            "review",
            "initiated",
            "flag",
        )
