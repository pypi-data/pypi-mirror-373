from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from . import models, serializers


class TokenProxyView(CreateModelMixin, GenericViewSet):
    serializer_class = serializers.TokenProxySerializer
    queryset = models.HousingStatCreds.objects.all()
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    @action(detail=False, methods=["post"])
    def logout(self, request, pk=None):
        username = request.user.username

        user_creds = models.HousingStatCreds.objects.filter(owner=username)
        if not user_creds:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        user_creds.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
