from django.contrib import admin
from django.utils.html import format_html
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin
from jalali_date import datetime2jalali
from .models import BankCard, Tag, Deposit, Withdrawal


@admin.register(BankCard)
class BankCardAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['bank_name', 'card_number', 'balance', 'jalali_created_at']
    list_filter = ['bank_name', 'created_at']
    search_fields = ['bank_name', 'card_number']
    readonly_fields = ['balance', 'created_at', 'updated_at']
    
    def jalali_created_at(self, obj):
        return datetime2jalali(obj.created_at).strftime('%Y/%m/%d %H:%M')
    jalali_created_at.short_description = 'تاریخ ایجاد'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'created_at']
    search_fields = ['name']
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; background-color: {}; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color, obj.color, obj.name
        )
    color_display.short_description = 'رنگ تگ'


@admin.register(Deposit)
class DepositAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['amount', 'bank_card', 'purpose', 'depositor', 'jalali_deposit_date', 'tag']
    list_filter = ['tag', 'bank_card', 'deposit_date']
    search_fields = ['purpose', 'depositor', 'bank_card__bank_name', 'bank_card__card_number']
    date_hierarchy = 'deposit_date'
    
    fieldsets = (
        ('اطلاعات واریز', {
            'fields': ('amount', 'bank_card', 'purpose', 'depositor')
        }),
        ('تاریخ و تگ', {
            'fields': ('deposit_date', 'tag')
        }),
    )
    
    def jalali_deposit_date(self, obj):
        return datetime2jalali(obj.deposit_date).strftime('%Y/%m/%d %H:%M')
    jalali_deposit_date.short_description = 'تاریخ واریز'


@admin.register(Withdrawal)
class WithdrawalAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['amount', 'bank_card', 'purpose', 'jalali_withdrawal_date', 'tag']
    list_filter = ['tag', 'bank_card', 'withdrawal_date']
    search_fields = ['purpose', 'bank_card__bank_name', 'bank_card__card_number']
    date_hierarchy = 'withdrawal_date'
    
    fieldsets = (
        ('اطلاعات برداشت', {
            'fields': ('amount', 'bank_card', 'purpose')
        }),
        ('تاریخ و تگ', {
            'fields': ('withdrawal_date', 'tag')
        }),
    )
    
    def jalali_withdrawal_date(self, obj):
        return datetime2jalali(obj.withdrawal_date).strftime('%Y/%m/%d %H:%M')
    jalali_withdrawal_date.short_description = 'تاریخ برداشت'
