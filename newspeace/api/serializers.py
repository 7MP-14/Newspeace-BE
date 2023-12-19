from rest_framework import serializers
from accounts.models import *
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from accounts.models import *

User = get_user_model()

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('id', 'keyword_text', 'ratio')

class UserSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)  # 추가: 비밀번호 확인 필드
    # token = serializers.CharField(read_only=True)  # 추가: 토큰을 응답에 추가

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'emailNotice', 'smsNotice', 'keywords', 'password', 'password_confirm', 'token')

    def validate(self, data):
        # 비밀번호와 비밀번호 확인이 일치하는지 확인
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")
        
        return data

    def create(self, validated_data):
        # password_confirm 필드는 User 모델에 존재하지 않기 때문에 제거
        validated_data.pop('password_confirm', None)

        keywords_data = validated_data.pop('keywords', None)
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)

        if keywords_data:
            for keyword_data in keywords_data:
                keyword, created = Keyword.objects.get_or_create(**keyword_data)
                user.keywords.add(keyword)

        user.save()

        # 토큰 생성 및 저장
        Token.objects.get_or_create(user=user)

        return user