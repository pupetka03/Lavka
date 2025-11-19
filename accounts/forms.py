from django import forms
from .models import Publication, Comments




class CreatePublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ("title", "text" )



class CreateCommentsForms(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'emoji-picker-enabled',
            'placeholder': '😎 Napiš niečo fakt cool... 🎯',
            'rows': 3,
            'style': '''
                width: 100%;
                border: none;
                border-bottom: 3px solid #3b82f6;
                padding: 15px;
                font-size: 18px;
                background: transparent;
                outline: none;
                transition: all 0.3s ease;
                font-weight: 500;
            ''',
            'onfocus': '''
                this.style.borderBottomColor = "#ef4444";
                this.style.background = "rgba(59, 130, 246, 0.05)";
            ''',
            'onblur': '''
                this.style.borderBottomColor = "#3b82f6";
                this.style.background = "transparent";
            '''
        }),
        label='',
        required=True
    )

    class Meta:
        model = Comments
        fields = ('text',)
