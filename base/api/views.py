from rest_framework.decorators import api_view
from rest_framework.response import Response
from base import models
from base.api import serializers

@api_view(['GET'])
def getRoutes(request):

    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]

    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = models.Room.objects.all()
    serializer = serializers.RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = models.Room.objects.get(id=pk)
    serializer = serializers.RoomSerializer(room, many=False)
    return Response(serializer.data)