from django import forms

class CallbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше имя',
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

class ContactForm(forms.Form):
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
            'placeholder': 'Ваше сообщение...',
            'class': 'form-textarea',
            'rows': 4
        })
    )