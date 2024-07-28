from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import JobCard

class ParentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    family_name = forms.CharField(max_length=100, label='Family Name')  # family_name フィールドを追加
    first_name = forms.CharField(max_length=30, required=True)  # first_name フィールドを追加

    class Meta:
        model = User
        fields = ('username', 'first_name', 'family_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.last_name = self.cleaned_data['family_name']  # family_nameをlast_nameとして設定
        if commit:
            user.save()
        return user

class CreateUserForm(forms.ModelForm):
    FAMILY_ROLE_CHOICES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
    ]
    
    role = forms.ChoiceField(choices=FAMILY_ROLE_CHOICES, help_text='Select whether this user is a parent or a child')
    
    class Meta:
        model = User
        first_name = forms.CharField(max_length=30, required=True)
        fields = ('username', 'first_name', 'password', 'role')
        widgets = {
            'password': forms.PasswordInput()
        }

class JobCardForm(forms.ModelForm):
    children = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # 初期は空のクエリセット
        required=True,
        label="Children",
        widget=forms.CheckboxSelectMultiple()  # 複数選択用のチェックボックス
    )

    job_image = forms.ImageField(required=False)

    class Meta:
        model = JobCard
        fields = ['children', 'job_name', 'money', 'job_image']

    def __init__(self, *args, **kwargs):
        parent_user = kwargs.pop('parent_user', None)  # 親ユーザーを取得
        super().__init__(*args, **kwargs)

        if parent_user:
            # 親ユーザーが所属する家族グループを取得
            family_group = None
            for group in parent_user.groups.all():
                if group.name != 'Parents':
                    family_group = group
                    break

            if family_group:
                # 'Children' グループと家族グループの両方に所属するユーザーを取得
                children_group = User.objects.filter(groups__name='Children')
                users_in_family_group = User.objects.filter(groups=family_group)
                # 両方のグループに所属するユーザーをフィルタリング
                eligible_users = users_in_family_group.filter(id__in=children_group.values('id'))
                self.fields['children'].queryset = eligible_users