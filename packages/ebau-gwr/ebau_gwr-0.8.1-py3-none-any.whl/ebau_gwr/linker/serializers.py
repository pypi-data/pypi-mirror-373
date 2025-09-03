from rest_framework_json_api import serializers

from . import models


class GWRLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GWRLink
        fields = (
            "id",
            "eproid",
            "local_id",
            "context",
        )
