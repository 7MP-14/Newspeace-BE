from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Keyword
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

RATIO_FILTER = 50

# 구독 키워드 설정 부정률 이상 도달 시 이메일 알림 보내기
# keyword 테이블의 ratio 참조 
@receiver(post_save, sender=Keyword)
def keyword_post_save(sender, instance, **kwargs):
    # 여기에 데이터베이스 변경시 실행할 작업을 추가
    
    # print(instance.keyword_text, '가 수정되었습니다.')

    # 키워드의 부정 비율이 기준 부정 비율 이상이면 수행
    if instance.ratio >= RATIO_FILTER:
        keyword_name = instance.keyword_text
        subject = f"뉴스피스에서 구독한 키워드 '{keyword_name}' 알림입니다."      # 이메일 제목
        from_email = "Newspeace <hjyeon1014@gmail.com>"                 # 발신할 이메일 주소
        
        # 해당 Keyword와 연결된 모든 User에게 이메일을 보냄
        for user in instance.user_set.all():
            if user.emailNotice == 1 and user.is_email_verified == 1:
                
                # HTML 형식을 사용해서 메일 보내는 코드
                # 메일 본문 (HTML 형식)
                html_message = f"""
                    <a href="http://www.newspeace.co.kr/"><img src="https://i.ibb.co/9VTP7V0/Newspeace2-12.png"></a>
                    <p>{user.name}님이 구독한 키워드 '<b>{keyword_name}</b>'의 부정 비율이 <b>{instance.ratio}%</b> 입니다.</p>
                    <p>자세한 내용은 <a href='www.newspeace.co.kr'>www.newspeace.co.kr</a>을 참고해주세요.</p>
                    <br>
                    <p>본 메일은 회원님께서 Newspeace 이메일 알림 동의를 하였기에 발송되었습니다.</p>
                    <p>메일 수신을 원치 않으시면 마이페이지 메뉴에서 알림 여부를 수정해주시기 바랍니다.</p>
                    <p>감사합니다.</p>
                    <p>- Newspeace -</p>
                """
                to_email = [user.email] # 수신자 이메일 주소
                email = EmailMultiAlternatives(subject=subject, body="This is a text message", to=to_email, from_email=from_email)  # EmailMultiAlternatives 객체 생성
                email.attach_alternative(html_message, "text/html") # HTML 형식 메일 추가
                email.send()    # 이메일 전송
                        
                # HTML 형식을 사용하지 않을때 기본 메일 보내는 코드
                # message = f"{user.name}님이 구독한 키워드 '{keyword_name}'의 부정 비율이 {instance.ratio}% 입니다.\n\n 자세한 내용은 www.newspeace.co.kr 을 참고해주세요."  # 본문 내용
                # to_email = [user.email]                                 # 수신할 이메일 주소
                # EmailMessage(subject=subject, body=message, to=to_email, from_email=from_email).send()
                print(f"{user.email}님에게 이메일을 보냅니다.")
            
        print(f"{keyword_name}키워드의 부정 비율이 {RATIO_FILTER}%를 넘었습니다.")