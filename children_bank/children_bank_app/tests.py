# Django shellを使って確認
from django.contrib.auth.models import User, Group

# ユーザーを取得
user = User.objects.get(username='test')

# グループを取得
family_group = Group.objects.get(name='yamada_10')
children_group = Group.objects.get(name='Children')

# グループにユーザーが属しているか確認
print(user.groups.filter(name='yamada_10').exists())  # True のはず
print(user.groups.filter(name='Children').exists())  # True のはず
