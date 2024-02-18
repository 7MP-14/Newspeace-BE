from django.shortcuts import render
from .serializers import *
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from board.models import Board
from django.db.models import Count, F
from rest_framework import status
from rest_framework.response import Response


# 공지사항 게시판 목록, 게시글 세부
class NoticeListAPIView(ListAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer
    

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

    def perform_create(self, serializer):
        # 데이터 추가할 때 number 필드를 초기값으로 설정
        # Board 테이블의 데이터 개수를 가져옴
        board_count = Board.objects.aggregate(Count('id'))['id__count']
        
        # number 필드에 데이터 개수 + 1 저장
        serializer.save(number=board_count + 1)


# 게시글 수정
class NoticeRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeListSerializer

    
# 게시글 삭제
class NoticeDestroyAPIView(DestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = NoticeDestroySerializer

    def destroy(self, request, *args, **kwargs):
        # 삭제할 때 id가 큰 데이터들의 number 1씩 빼기
        instance = self.get_object()
        # Step 1: self보다 큰 id를 가진 데이터를 가져옴
        greater_than_self = Board.objects.filter(id__gt=instance.id)
        # Step 2: 가져온 각 데이터의 number를 하나씩 감소
        for data in greater_than_self:
            data.number = F('number') - 1
            data.save()
        # Step 3: 해당 인스턴스를 삭제
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)