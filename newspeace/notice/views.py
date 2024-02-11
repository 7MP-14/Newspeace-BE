from django.shortcuts import render
from .serializers import *
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from board.models import Board


# 공지사항 게시판 목록, 게시글 세부
class NoticeListAPIView(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer
    
    def get(self, request, *args, **kwargs):
        # 데이터베이스에서 모든 레코드를 가져옵니다.
        all_boards = Board.objects.all()
        #  각 레코드의 id를 순차적으로 갱신합니다.
        for index, board in enumerate(all_boards, start=1):
            board.delete()
            board.id = index
            board.save()

        # 나머지 GET 메소드 로직을 계속 수행합니다.
        return super().get(request, *args, **kwargs) 
    

# 게시글 추가
class NoticeCreateAPIView(CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer
    
    def create(self, request, *args, **kwargs):
        print("Received data:", request.data)
        response = super().create(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = "true"
        return response


# 게시글 수정
class NoticeRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer

    
# 게시글 삭제
class NoticeDestroyAPIView(DestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeDestroySerializer