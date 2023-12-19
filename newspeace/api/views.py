from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .serializers import UserSerializer

User = get_user_model()

class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 인증 여부와 관계 없이 접근 허용

    def create(self, request, *args, **kwargs):
        # 사용자 생성 전에 request.data에서 필요한 데이터만 추출
        user_data = {
            'email': request.data.get('email'),
            'name': request.data.get('name'),
            'phone_number': request.data.get('phone_number'),
            'password': request.data.get('password'),
        }

        serializer = self.get_serializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 토큰 생성 및 응답에 추가
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)

        headers = self.get_success_headers(serializer.data)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)
