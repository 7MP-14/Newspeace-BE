from django import forms
from board.models import Board

# ModelForm
class BoardModelForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'body', 'image']