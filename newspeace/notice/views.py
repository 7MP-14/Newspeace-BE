from django.shortcuts import render
from .serializers import *
from rest_framework.generics import *
from board.models import Board


class NoticeListAPIView(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer
    
    
class NoticeRetrieveAPIView(RetrieveAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeRetrieveSerializer
    
    def get_serializer_context(self):
        return {
            'request' : None,
            'format' : self.format_kwarg,
            'view' : self
        }
    
    
class NoticeCreateAPIView(CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeRetrieveSerializer
    
    
class NoticeDestroyAPIView(DestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeDestroySerializer