from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.contrib.auth.decorators import user_passes_test


# Board 전체 목록 보기
def list(request):
    board_list = Board.objects.all()
    return render(request, 'board/list.html', {'board_all':board_list}) # HttpRequest()로 list.html 템플릿 페이지를 Response의 body에 응답


# Board 상세 보기
def detail(request, id):
    board = get_object_or_404(Board, id=id)   # Does Not Exist이면 404 응답 코드
    return render(request, 'board/detail.html', {'board':board})


# 사용자가 관리자인지를 확인하는 함수
def is_admin(user):
    return user.is_admin


# Form 기반으로 Board Data 추가 작업
@user_passes_test(is_admin)  # 해당 데코레이터를 사용하여 관리자만 접근할 수 있도록 함
def write(request):
    # request가 POST 방식이면 게시글 추가작업, GET방식이면 게시글 추가 Form HTML 띄움
    if request.method == 'POST':
        form = BoardModelForm(request.POST)             # 빈 Form에 입력받은 입력값 채워넣음
        if form.is_valid():                             # 유효성 검증
            print('cleaned_data', form.cleaned_data)    # 유효성 검증에 통과된 '필드명':입력값들이 dict 형태로 들어감
            # DB에 추가
            # board = Board.objects.create(**form.cleaned_data)  # DB에 저장하는 방법1
            # board = form.save()                                # DB에 저장하는 방법2 
            board = form.save(commit=False)                      # commit=False: commit 지연. DB에 save는 안하고 모델인스턴스에 넣어서 리턴만 해줌
            board.author_id = request.user.id                    # 현재 로그인 되어있는 User id 가져오기
            try:
                board.image = request.FILES['image']
            except:
                board.image = None
            board.save()                                         # 추가 작업
            return redirect(board)                       # 요청 끝나고 '/board/id/' detail 페이지 실행
    else:
        form = BoardModelForm()                          # board/forms.py의 장고 Form을 HTML로 변환
    return render(request, 'board/write.html', {'form':form})


# Data 삭제 작업
@user_passes_test(is_admin)  # 해당 데코레이터를 사용하여 관리자만 접근할 수 있도록 함
def delete(request, id):
    board = get_object_or_404(Board, id=id)
    # request가 POST 방식이면 게시글 삭제 작업, GET방식이면 delete.html 띄움
    if request.method == 'POST':
        board.delete()
        return redirect('board:list')
    else:
        return render(request, 'board/delete.html', {'board':board})