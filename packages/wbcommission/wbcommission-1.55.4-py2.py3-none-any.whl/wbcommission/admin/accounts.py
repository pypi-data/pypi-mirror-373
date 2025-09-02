from django.contrib import admin
from wbcrm.admin.accounts import AccountModelAdmin as BaseAccountModelAdmin
from wbcrm.models.accounts import Account

from wbcommission.models.rebate import manage_rebate_as_task

from .commission import CommissionTabularInline

admin.site.unregister(Account)


@admin.register(Account)
class AccountModelAdmin(BaseAccountModelAdmin):
    def make_rebates(self, request, queryset):
        for account in queryset:
            manage_rebate_as_task.delay(account.id)

    def get_assets_under_management(self, request, queryset):
        for account in queryset:
            account.get_assets_under_management()

    actions = list(BaseAccountModelAdmin.actions) + [make_rebates, get_assets_under_management]
    inlines = BaseAccountModelAdmin.inlines + [CommissionTabularInline]
