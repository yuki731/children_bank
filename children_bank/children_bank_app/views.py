from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from .models import PocketMoney, JobCard, JobReport
from .forms import ParentSignUpForm, CreateUserForm, JobCardForm

class SignUpView(CreateView):
    model = User
    form_class = ParentSignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

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
    """
    ユーザーのグループに応じて適切なダッシュボードにリダイレクトするビュー。
    親ユーザーは親ダッシュボードに、子供ユーザーは子供ダッシュボードにリダイレクトされます。
    """
    user = request.user
    
    # ユーザーが特定のグループに所属しているかどうかをチェック
    if user.groups.filter(name='Parents').exists():
        return redirect('parent_dashboard')  # 親ユーザー用のダッシュボード
    else:
        return redirect('child_dashboard')  # 子ユーザー用のダッシュボード

### Parent page

@login_required
def parent_dashboard_view(request):
    """
    親ユーザー用のダッシュボードを表示するビュー。
    親ユーザーでない場合は子供ダッシュボードにリダイレクトされます。
    """
    if not request.user.groups.filter(name='Parents').exists():
        return redirect('child_dashboard') 
    return render(request, 'parent_dashboard.html')

@login_required
def create_user_account(request):
    """
    親ユーザーが子供または他の親ユーザーのアカウントを作成するビュー。
    子供アカウントが作成されると、初期のPocketMoneyインスタンスも作成されます。
    """
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
    """
    現在ログインしている親ユーザーが所属するファミリーグループの子供をリストするビュー。
    親ユーザーでない場合は子供ダッシュボードにリダイレクトされます。
    """
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
    """
    特定の子供ユーザーのPocketMoneyレコードとJobCardレコードを表示するビュー。
    PocketMoneyレコードの合計金額も計算して表示します。
    """
    child = get_object_or_404(User, id=child_id)
    pocket_money_records = PocketMoney.objects.filter(child=child)
    total_amount = pocket_money_records.aggregate(total=Sum('amount'))['total']
    
    job_cards = JobCard.objects.filter(child=child)
    job_reports = JobReport.objects.filter(reported_by=child)

    return render(request, 'child_pocket_money.html', {
        'child': child,
        'pocket_money_records': pocket_money_records,
        'total_amount': total_amount,
        'job_cards': job_cards,
        'job_reports': job_reports,
    })

@login_required
def delete_job_card(request, job_card_id):
    """
    特定のJobCardレコードを削除するビュー。
    """
    job_card = get_object_or_404(JobCard, id=job_card_id)
    job_card.delete()
    return redirect('child_pocket_money', child_id=job_card.child.id)

@login_required
def create_job_card(request):
    if not request.user.groups.filter(name='Parents').exists():
        return redirect('child_dashboard')  # 親以外のユーザーがアクセスした場合のリダイレクト
    
    if request.method == 'POST':
        form = JobCardForm(request.POST, request.FILES, parent_user=request.user)
        if form.is_valid():
            # フォームから選択された子供たちを取得
            children = form.cleaned_data['children']
            job_name = form.cleaned_data['job_name']
            money = form.cleaned_data['money']
            job_image = form.cleaned_data['job_image']

            # 親ユーザーの家族グループを取得
            family_group = request.user.groups.exclude(name='Parents').first()

            # 各子供について JobCard インスタンスを作成
            for child in children:
                JobCard.objects.create(
                    child=child,
                    group=family_group.name,
                    job_name=job_name,
                    money=money,
                    job_image=job_image
                )
            
            return redirect('parent_dashboard')  # 登録後のリダイレクト先
    else:
        form = JobCardForm(parent_user=request.user)
    
    return render(request, 'create_job_card.html', {'form': form})

### Child page

@login_required
def child_dashboard_view(request):
    """
    子供ユーザー用のダッシュボードを表示するビュー。
    親ユーザーである場合は親ダッシュボードにリダイレクトされます。
    """
    if request.user.groups.filter(name='Parents').exists():
        return redirect('parent_dashboard') 
    child = request.user
    pocket_money_records = PocketMoney.objects.filter(child=child)
    total_amount = pocket_money_records.aggregate(total=Sum('amount'))['total']
    return render(request, 'child_dashboard.html', {'total_amount': total_amount})

@login_required
def task_view(request):
    child = request.user
    job_cards = JobCard.objects.filter(child=child)
    return render(request, 'task_view.html', {'job_cards': job_cards})

@login_required
def report_job_view(request, job_id):
    job = get_object_or_404(JobCard, id=job_id)
    user = request.user

    family_group = None
    groups = user.groups.all()
    for group in groups:
        if group.name != 'Parents':
            family_group = Group.objects.get(name=group.name)
    
    if request.method == 'POST':
        # TaskReportに報告されたジョブ情報を保存
        JobReport.objects.create(
            job_name=job.job_name,
            money=job.money,
            group=family_group,
            reported_by=request.user,
        )
        messages.success(request, f'Job {job.job_name} has been reported to your parent for approval.')
        return redirect('child_dashboard')  # リダイレクト先を指定
    return render(request, 'report_job.html', {'job': job})


