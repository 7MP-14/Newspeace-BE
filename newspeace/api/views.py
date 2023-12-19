from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response

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
        token = serializer.validated_data # validate()의 리턴값인 token을 받아온다.
        return Response({"token": token.key}, status=status.HTTP_200_OK)

#프로필 불러오기
