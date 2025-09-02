from wbcore import serializers


class OfficerSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyCharField()
    position = serializers.CharField()
    name = serializers.CharField()
    age = serializers.IntegerField()
    sex = serializers.CharField()
    start = serializers.DateField()

    class Meta:
        fields = (
            "id",
            "position",
            "name",
            "age",
            "sex",
            "start",
        )
