from django.shortcuts import render
from .serializers import *
from rest_framework.generics import *
from board.models import Board


# 공지사항 게시판 목록, 게시글 세부
class NoticeListAPIView(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer
    
    # def get_serializer_context(self):
    #     return {
    #         'request' : None,
    #         'format' : self.format_kwarg,
    #         'view' : self
    #     }
    
    
# class NoticeRetrieveAPIView(RetrieveAPIView):
#     queryset = Board.objects.all()
#     serializer_class = NoticeRetrieveSerializer
    
    
# 게시글 추가
class NoticeCreateAPIView(CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    
    
# 게시글 삭제
class NoticeDestroyAPIView(DestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeDestroySerializer