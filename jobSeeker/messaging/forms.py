from django import forms
from .models import Conversation, Message

class StartConversationForm(forms.ModelForm):
    """
    Form for recruiters to start a new conversation with a job seeker
    """
    class Meta:
        model = Conversation
        fields = ['subject']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter conversation subject (e.g., "Interview for Software Engineer Position")',
                'maxlength': '200'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = True
        self.fields['subject'].label = 'Subject'

class MessageForm(forms.ModelForm):
    """
    Form for sending messages within a conversation
    """
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message here...',
                'rows': 3,
                'maxlength': '2000'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['content'].label = 'Message'
