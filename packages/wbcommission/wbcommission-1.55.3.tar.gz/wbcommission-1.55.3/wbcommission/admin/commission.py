from django.contrib import admin

from wbcommission.models import (
    Commission,
    CommissionExclusionRule,
    CommissionRole,
    CommissionRule,
    CommissionType,
)


@admin.register(CommissionType)
class CommissionTypeModelAdmin(admin.ModelAdmin):
    pass


class CommissionRuleTabularInline(admin.TabularInline):
    ordering = ("timespan__startswith", "assets_under_management_range__startswith")
    fields = (
        "timespan",
        "assets_under_management_range",
        "percent",
    )
    model = CommissionRule
    extra = 0


class CommissionRoleTabularInline(admin.TabularInline):
    model = CommissionRole
    autocomplete_fields = ["person"]
    fields = (
        "person",
        "commission",
    )
    extra = 0


class CommissionTabularInline(admin.TabularInline):
    extra = 0
    model = Commission
    fields = [
        "order",
        "crm_recipient",
        "account_role_type_recipient",
        "portfolio_role_recipient",
        "commission_type",
        "net_commission",
        "is_hidden",
        "exclusion_rule_account_role_type",
    ]
    readonly_fields = ["order"]
    ordering = ["order"]
    autocomplete_fields = ["account", "crm_recipient"]
    show_change_link = True


@admin.register(Commission)
class CommissionModelAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "crm_recipient",
        "portfolio_role_recipient",
        "account_role_type_recipient",
        "order",
        "net_commission",
        "commission_type",
        "is_hidden",
        "exclusion_rule_account_role_type",
    ]

    autocomplete_fields = ["account", "crm_recipient"]

    inlines = [CommissionRoleTabularInline, CommissionRuleTabularInline]


@admin.register(CommissionExclusionRule)
class CommissionExclusionRuleAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "commission_type",
        "account_role_type",
        "timespan",
        "overriding_percent",
        "overriding_net_or_gross_commission",
    ]
    autocomplete_fields = ["product", "account_role_type"]
