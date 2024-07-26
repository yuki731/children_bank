from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import PocketMoney
from .forms import ParentSignUpForm, CreateUserForm


class SignUpView(CreateView):
    model = User
    form_class = ParentSignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('parent_dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        family_name = form.cleaned_data.get('family_name')
        user.last_name = family_name
        user.save()
        

        # ファミリーネームでグループを作成または取得
        unique_group_name = f"{family_name}_{user.id}"
        family_group, created = Group.objects.get_or_create(name=unique_group_name)
        user.groups.add(family_group)

        # ユーザーを親のグループに追加
        parent_group, _ = Group.objects.get_or_create(name='Parents')
        user.groups.add(parent_group)

        return response
    
@login_required
def check_permissions_and_redirect(request):
    user = request.user
    
    # ユーザーが特定のグループに所属しているかどうかをチェック
    if user.groups.filter(name='Parents').exists():
        return redirect('parent_dashboard')  # 親ユーザー用のダッシュボード
    else:
        return redirect('child_dashboard')  # 子ユーザー用のダッシュボード

    
@login_required
def parent_dashboard_view(request):
    if not request.user.groups.filter(name='Parents').exists():
        return redirect('child_dashboard') 
    return render(request, 'parent_dashboard.html')

@login_required
def child_dashboard_view(request):
    return render(request, 'child_dashboard.html')

@login_required
def create_user_account(request):
    if not request.user.groups.filter(name='Parents').exists():
        return redirect('child_dashboard')
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # 現在ログインしている親ユーザーを取得
            parent_user = request.user
            last_name = parent_user.last_name  # 親ユーザーからファミリーネーム（last_name）を取得
            role = form.cleaned_data.get('role')

            group_name = None
            groups = parent_user.groups.all()
            for group in groups:
                if group.name != 'Parents':
                    group_name = group.name

            # 新しいユーザーにファミリーネーム（last_name）を設定
            user.last_name = last_name
            user.save()

            # ファミリーネームのグループを取得または作成
            family_group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(family_group)

            if role == 'parent':
                parent_group_name = "Parents"
                parent_group, created = Group.objects.get_or_create(name=parent_group_name)
                parent_user.groups.add(parent_group)
            elif role == 'child':
                child_group_name = "Children"
                child_group, created = Group.objects.get_or_create(name=child_group_name)
                user.groups.add(child_group)

                # PocketMoney インスタンスを作成
                pocket_money = PocketMoney(
                    child=user,
                    group=group_name,
                    amount=0.00,  # 初期金額を設定
                    date=timezone.now().date(),  # 現在の日付を設定
                    transaction_type=PocketMoney.DEPOSIT,  # 初期トランザクションタイプを設定
                    memo='Initial deposit'  # メモを設定
                )
                pocket_money.save()

            return redirect('parent_dashboard')
    else:
        form = CreateUserForm()

    return render(request, 'registration/create_user_account.html', {'form': form})

@login_required
def children_in_family_view(request):

    if not request.user.groups.filter(name='Parents').exists():
        return redirect('child_dashboard')
    
    parent_user = request.user

    family_group = None
    groups = parent_user.groups.all()
    for group in groups:
        if group.name != 'Parents':
            family_group = Group.objects.get(name=group.name)

    children_group = Group.objects.get(name='Children')
    
    users_in_family_group = User.objects.filter(groups=family_group)
    users_in_children_group = User.objects.filter(groups=children_group)
    family_members = users_in_family_group.filter(id__in=users_in_children_group.values('id'))

    return render(request, 'children_in_family.html', {'family_members': family_members})

@login_required
def child_pocket_money_view(request, child_id):
    child = get_object_or_404(User, id=child_id)
    pocket_money_records = PocketMoney.objects.filter(child=child)
    return render(request, 'child_pocket_money.html', {'child': child, 'pocket_money_records': pocket_money_records})
