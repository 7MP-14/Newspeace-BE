from rest_framework import serializers
from board.models import Board


class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'
        
        
class NoticeDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id']