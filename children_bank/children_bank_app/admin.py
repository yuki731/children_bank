from django.contrib import admin
from .models import PocketMoney

# PocketMoneyモデルのAdminクラスを作成（オプション）
class PocketMoneyAdmin(admin.ModelAdmin):
    list_display = ('child', 'group', 'amount', 'date', 'transaction_type', 'memo')  # 一覧表示で見たいフィールドを指定
    search_fields = ('child__username', 'transaction_type')  # 検索フィールドを指定
    list_filter = ('transaction_type', 'date')  # フィルタリングオプションを指定

# PocketMoneyモデルを管理サイトに登録
admin.site.register(PocketMoney, PocketMoneyAdmin)
