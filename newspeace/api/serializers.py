from rest_framework import serializers
from accounts.models import *
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

User = get_user_model()
#회원가입, 프로필
class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('id', 'keyword_text', 'ratio','code')
    extra_kwargs = {
        'keyword_text': {'write_only': True},
    }

class UserSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())], # 이메일에 대한 중복 검증
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # 비밀번호에 대한 검증
    )
    password2 = serializers.CharField( # 비밀번호 확인을 위한 필드
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'emailNotice', 'smsNotice', 'keywords', 'is_email_verified','password', 'password2')

    
    def validate(self, data): # password과 password2의 일치 여부 확인
        # password와 password2의 일치 여부 확인은 create 시에만 수행
        if self.context['request'].method == 'POST':
            password = data.get('password')
            password2 = data.get('password2')
            if password != password2:
                raise serializers.ValidationError({"password": "Password fields didn't match."})
        # if data['password'] != data['password2']:
        #     raise serializers.ValidationError(
        #         {"password": "Password fields didn't match."})
        
        return data


    def create(self, validated_data):
        # CREATE 요청에 대해 create 메서드를 오버라이딩하여, 유저를 생성하고 토큰도 생성하게 해준다.
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
        )

        user.set_password(validated_data['password'])
        user.save()
        token, created = Token.objects.get_or_create(user=user)

        return user
    
    def update(self, instance, validated_data):
        # 프로필 업데이트 시, 키워드를 추가할 수 있도록 로직 추가
        keywords_data = validated_data.pop('keywords', [])
        # instance = super().update(instance, validated_data)

        # 기존 키워드 모두 삭제
        # instance.keywords.clear()
        
        for keyword_data in keywords_data:
            keyword_text = keyword_data.get('keyword_text')
            if keyword_text:
                try:
                    keyword, created = Keyword.objects.get_or_create(keyword_text=keyword_text)
                    # 새로운 키워드를 추가
                    instance.keywords.add(keyword)
                except Keyword.DoesNotExist:
                    # Keyword 객체를 찾을 수 없을 때의 처리
                    pass
                except Exception as e:
                    # 다른 예외 처리
                    print(e)

        # 비밀번호 변경 처리
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()

        return instance
    
# 유저의 특정 키워드 삭제
class KeywordDeleteSerializer(serializers.Serializer):
    keyword_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

#로그인
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    # write_only=True 옵션을 통해 클라이언트->서버의 역직렬화는 가능하지만, 서버->클라이언트 방향의 직렬화는 불가능하도록 해준다.
    
    def validate(self, data):
        user = authenticate(**data)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return {
                'token': token.key,
                'user_id': user.id,  # 사용자 ID를 추가
                'is_admin': user.is_admin
            }
        raise serializers.ValidationError( # 가입된 유저가 없을 경우
            {"error": "Unable to log in with provided credentials."}
        )
    
