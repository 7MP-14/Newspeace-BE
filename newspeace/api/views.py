from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import CustomReadOnly

from .serializers import *

User = get_user_model()
#회원가입
class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#로그인
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data  # 수정: 딕셔너리를 변수에 저장

        return Response({
            "token": validated_data.get('token'),  # 수정: 'token' 키에 대한 값을 가져오도록 수정
            "user_id": validated_data.get('user_id')  # 수정: 'user_id' 키에 대한 값을 가져오도록 수정
        }, status=status.HTTP_200_OK)

#프로필 불러오기, 수정
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    
    # def get_object(self):
    #     return self.request.user  # 현재 로그인한 사용자의 프로필만 가져오도록 수정

    def perform_update(self, serializer):
        # UserSerializer의 update 메서드를 호출하여 프로필 업데이트 수행
        serializer.update(serializer.instance, serializer.validated_data)

        # 추가: 키워드 업데이트 로직
        keywords_data = self.request.data.get('keywords', [])
        instance = serializer.instance

        for keyword_data in keywords_data:
            keyword_text = keyword_data.get('keyword_text')
            keyword_id = keyword_data.get('id')  # 추가: 키워드의 ID 가져오기
            if keyword_text:
                keyword, created = Keyword.objects.get_or_create(keyword_text=keyword_text)
                if created or not instance.keywords.filter(keyword_text__iexact=keyword_text).exists():
                    instance.keywords.add(keyword)
        instance.save()   

