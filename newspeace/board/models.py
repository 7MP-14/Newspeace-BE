from django.db import models
from django.urls import reverse
from accounts.models import User  # accounts 앱에 있는 모델 import

class Board(models.Model):   # 테이블 명은 '앱이름_모델명소문자' 로 만들어짐. 
    title = models.CharField(max_length=250)            # 제목
    body = models.TextField()                           # 본문
    image= models.ImageField(blank=True, upload_to='board/') # 이미지
    created = models.DateField(auto_now_add=True)   # 작성한 날짜
    author = models.ForeignKey(User, on_delete=models.PROTECT, default=0)  # PROTECT: 관리자 계정이 삭제되지 않도록
    
    def __str__(self):  # admin이나 shell에서 모델 인스턴스 출력이 어떻게 보일지
        return self.title
    
    def get_absolute_url(self):     # redirect(모델인스턴스) 하면 실행되는 메소드
        return reverse('board:detail', args=[self.id])
    
    def save(self, *args, **kwargs):
        # 작성자가 관리자인지 확인
        if not self.author.is_admin:
            raise PermissionError("관리자만이 게시글을 추가할 수 있습니다.")
        
        super().save(*args, **kwargs)   # 관리자가 맞다면, DB에 추가