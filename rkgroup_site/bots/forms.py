from django import forms

class ConsultationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше имя',
            'class': 'form-input',
            'required': 'required'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ваш email',
            'class': 'form-input',
            'required': 'required'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (___) ___-__-__',
            'class': 'form-input',
            'required': 'required'
        })
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Кратко опишите, что вас интересует...',
            'class': 'form-textarea',
            'rows': 4
        })
    )
    bot_name = forms.CharField(required=False, widget=forms.HiddenInput())