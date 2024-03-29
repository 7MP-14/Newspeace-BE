from django.db import DJANGO_VERSION_PICKLE_KEY
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import CustomReadOnly
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from .serializers import *
from django.middleware.csrf import get_token

from .utils import get_code_from_df_krx
import json

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
            "user_id": validated_data.get('user_id'),  # 수정: 'user_id' 키에 대한 값을 가져오도록 수정
            "is_admin": validated_data.get('is_admin')
        }, status=status.HTTP_200_OK)

#프로필 불러오기, 수정
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

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

# 유저 탈퇴
class UserProfileDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDeleteSerializer
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        password = request.data.get('password')
        if not password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({"error": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        
# 프로필 유저 키워드 삭제
class KeywordDeleteView(generics.UpdateAPIView):
    serializer_class = KeywordDeleteSerializer
    permission_classes = [AllowAny]  # 필요한 권한을 여기에 추가

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, pk=user_id)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 키워드 삭제 로직 추가
        keyword_ids = serializer.validated_data.get('keyword_ids',[])
        if keyword_ids:
            instance.keywords.remove(*instance.keywords.filter(id__in=keyword_ids))

        return Response({"message": "키워드 삭제 완료!"}, status=status.HTTP_200_OK)

# 이메일 인증 코드를 세션에 저장
@csrf_exempt
def send_verification_email(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
            user_id = payload.get('user_id')
            verification_code = payload.get('verification_code')
            
            # 세션에 데이터 저장
            request.session['user_id'] = user_id
            request.session['verification_code'] = verification_code
            request.session.save()
            session_key=request.session.session_key
            # print("얌:",session_key)
            
            # 세션에 저장된 전체 데이터 출력
            # print("user_id:", request.session.get('user_id'))
            # print("verification_code:", request.session.get('verification_code'))
            # print("Entire Session Data:", request.session.items())
            return JsonResponse({'status': 'success', 'message': '이메일이 성공적으로 전송되었습니다. 이메일을 확인하세요.', 'key' : session_key})

        except json.JSONDecodeError:
            pass  # JSON 디코딩 오류 처리

    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)


# 사용자가 인증 코드를 입력하면 세션과 비교해서 동일한지 확인
@csrf_exempt
def verify_email(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
            user_id = payload.get('user_id')
            verification_code = payload.get('verification_code')
            session_key=payload.get('key')
            
            stored_user_id = Session.objects.get(session_key=session_key).get_decoded().get('user_id')
            stored_verification_code = Session.objects.get(session_key=session_key).get_decoded().get('verification_code')
            
            # 세션에서 데이터 조회
            # stored_user_id = request.session.get('user_id')
            # stored_verification_code = request.session.get('verification_code')

            # if stored_user_id and stored_verification_code:
            #     user = get_object_or_404(User, id=user_id)
            #     user.is_email_verified = True
            #     user.save()
            
            print("Stored User ID:", stored_user_id)
            print("Stored Verification Code:", stored_verification_code)
            
            # 이메일과 인증 코드를 비교
            if user_id == stored_user_id and verification_code == stored_verification_code:
                # User의 is_email_verified를 True로 변경
                user = get_object_or_404(User, id=user_id)
                user.is_email_verified = True
                user.save()
                          
                # 세션에서 데이터 삭제 (선택적)
                # del request.session['user_id']
                # del request.session['verification_code']
                return JsonResponse({'verify_email': True, 'message': '이메일 인증이 성공적으로 완료되었습니다.'})

        except json.JSONDecodeError:
            pass  # JSON 디코딩 오류 처리
    
    return JsonResponse({'verify_email': False, 'message': '이메일 인증에 실패했습니다.'}, status=400)