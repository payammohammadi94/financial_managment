from django.shortcuts import render
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from jalali_date import datetime2jalali
from .models import BankCard, Tag, Deposit, Withdrawal


def financial_dashboard(request):
    """صفحه اصلی مدیریت مالی"""
    context = {
        'total_cards': BankCard.objects.count(),
        'total_balance': BankCard.objects.aggregate(total=Sum('balance'))['total'] or 0,
        'total_deposits': Deposit.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdrawals': Withdrawal.objects.aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'financial/dashboard.html', context)


def transactions_list(request):
    """لیست تراکنش‌ها با قابلیت فیلتر"""
    deposits = Deposit.objects.all()
    withdrawals = Withdrawal.objects.all()
    
    # فیلتر بر اساس تگ
    tag_filter = request.GET.get('tag')
    if tag_filter:
        deposits = deposits.filter(tag_id=tag_filter)
        withdrawals = withdrawals.filter(tag_id=tag_filter)
    
    # فیلتر بر اساس کارت بانکی
    card_filter = request.GET.get('card')
    if card_filter:
        deposits = deposits.filter(bank_card_id=card_filter)
        withdrawals = withdrawals.filter(bank_card_id=card_filter)
    
    # فیلتر بر اساس بازه زمانی
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            deposits = deposits.filter(deposit_date__gte=start_datetime)
            withdrawals = withdrawals.filter(withdrawal_date__gte=start_datetime)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            deposits = deposits.filter(deposit_date__lte=end_datetime)
            withdrawals = withdrawals.filter(withdrawal_date__lte=end_datetime)
        except ValueError:
            pass
    
    # ترکیب واریزها و برداشت‌ها
    transactions = []
    
    for deposit in deposits:
        transactions.append({
            'type': 'deposit',
            'amount': deposit.amount,
            'purpose': deposit.purpose,
            'date': deposit.deposit_date,
            'jalali_date': deposit.get_jalali_deposit_date(),
            'bank_card': deposit.bank_card,
            'tag': deposit.tag,
            'depositor': deposit.depositor,
            'withdrawer': None,
        })
    
    for withdrawal in withdrawals:
        transactions.append({
            'type': 'withdrawal',
            'amount': withdrawal.amount,
            'purpose': withdrawal.purpose,
            'date': withdrawal.withdrawal_date,
            'jalali_date': withdrawal.get_jalali_withdrawal_date(),
            'bank_card': withdrawal.bank_card,
            'tag': withdrawal.tag,
            'depositor': None,
            'withdrawer': 'خودم',
        })
    
    # مرتب‌سازی بر اساس تاریخ
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    # صفحه‌بندی
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # فیلترها
    tags = Tag.objects.all()
    cards = BankCard.objects.all()
    
    context = {
        'page_obj': page_obj,
        'transactions': page_obj,
        'tags': tags,
        'cards': cards,
        'selected_tag': tag_filter,
        'selected_card': card_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'financial/transactions.html', context)


def tag_summary(request):
    """خلاصه مبالغ بر اساس تگ‌ها"""
    # محاسبه مجموع واریزها بر اساس تگ
    deposit_summary = Deposit.objects.values('tag__name', 'tag__color').annotate(
        total_amount=Sum('amount')
    ).order_by('-total_amount')
    
    # محاسبه مجموع برداشت‌ها بر اساس تگ
    withdrawal_summary = Withdrawal.objects.values('tag__name', 'tag__color').annotate(
        total_amount=Sum('amount')
    ).order_by('-total_amount')
    
    # ترکیب نتایج
    tag_totals = {}
    
    for item in deposit_summary:
        tag_name = item['tag__name'] or 'بدون تگ'
        tag_color = item['tag__color'] or '#6c757d'
        if tag_name not in tag_totals:
            tag_totals[tag_name] = {
                'name': tag_name,
                'color': tag_color,
                'deposits': 0,
                'withdrawals': 0,
                'net': 0
            }
        tag_totals[tag_name]['deposits'] = item['total_amount']
    
    for item in withdrawal_summary:
        tag_name = item['tag__name'] or 'بدون تگ'
        tag_color = item['tag__color'] or '#6c757d'
        if tag_name not in tag_totals:
            tag_totals[tag_name] = {
                'name': tag_name,
                'color': tag_color,
                'deposits': 0,
                'withdrawals': 0,
                'net': 0
            }
        tag_totals[tag_name]['withdrawals'] = item['total_amount']
    
    # محاسبه خالص
    for tag_data in tag_totals.values():
        tag_data['net'] = tag_data['deposits'] - tag_data['withdrawals']
    
    # مرتب‌سازی بر اساس مجموع کل
    sorted_tags = sorted(tag_totals.values(), key=lambda x: x['deposits'] + x['withdrawals'], reverse=True)
    
    context = {
        'tag_summary': sorted_tags,
        'total_deposits': sum(item['deposits'] for item in tag_totals.values()),
        'total_withdrawals': sum(item['withdrawals'] for item in tag_totals.values()),
    }
    
    return render(request, 'financial/tag_summary.html', context)


def bank_cards_list(request):
    """لیست کارت‌های بانکی"""
    cards = BankCard.objects.all()
    
    context = {
        'cards': cards,
        'total_balance': sum(card.balance for card in cards),
    }
    
    return render(request, 'financial/bank_cards.html', context)
