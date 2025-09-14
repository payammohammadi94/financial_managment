from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from jalali_date import datetime2jalali


class BankCard(models.Model):
    """مدل کارت بانکی"""
    bank_name = models.CharField(max_length=100, verbose_name="نام بانک")
    card_number = models.CharField(max_length=20, unique=True, verbose_name="شماره کارت")
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="موجودی کارت"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "کارت بانکی"
        verbose_name_plural = "کارت‌های بانکی"
        ordering = ['bank_name', 'card_number']

    def __str__(self):
        return f"{self.bank_name} - {self.card_number}"

    def get_jalali_created_at(self):
        return datetime2jalali(self.created_at).strftime('%Y/%m/%d %H:%M')


class Tag(models.Model):
    """مدل تگ"""
    name = models.CharField(max_length=50, unique=True, verbose_name="نام تگ")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="رنگ تگ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "تگ"
        verbose_name_plural = "تگ‌ها"
        ordering = ['name']

    def __str__(self):
        return self.name


class Deposit(models.Model):
    """مدل واریز پول"""
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="مبلغ"
    )
    bank_card = models.ForeignKey(
        BankCard, 
        on_delete=models.CASCADE, 
        verbose_name="کارت بانکی"
    )
    purpose = models.CharField(max_length=200, verbose_name="بابت چه کاری")
    depositor = models.CharField(max_length=100, verbose_name="واریز کننده")
    deposit_date = models.DateTimeField(default=timezone.now, verbose_name="تاریخ واریز")
    tag = models.ForeignKey(
        Tag, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="تگ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "واریز"
        verbose_name_plural = "واریزها"
        ordering = ['-deposit_date']

    def __str__(self):
        return f"واریز {self.amount} تومان - {self.purpose}"

    def get_jalali_deposit_date(self):
        return datetime2jalali(self.deposit_date).strftime('%Y/%m/%d %H:%M')

    def save(self, *args, **kwargs):
        # اگر این یک واریز جدید است، موجودی کارت را افزایش می‌دهیم
        if not self.pk:
            self.bank_card.balance += self.amount
            self.bank_card.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # هنگام حذف واریز، موجودی کارت را کاهش می‌دهیم
        self.bank_card.balance -= self.amount
        self.bank_card.save()
        super().delete(*args, **kwargs)


class Withdrawal(models.Model):
    """مدل برداشت پول"""
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="مبلغ"
    )
    purpose = models.CharField(max_length=200, verbose_name="بابت چه کاری")
    withdrawal_date = models.DateTimeField(default=timezone.now, verbose_name="تاریخ برداشت")
    bank_card = models.ForeignKey(
        BankCard, 
        on_delete=models.CASCADE, 
        verbose_name="کارت بانکی"
    )
    tag = models.ForeignKey(
        Tag, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="تگ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "برداشت"
        verbose_name_plural = "برداشت‌ها"
        ordering = ['-withdrawal_date']

    def __str__(self):
        return f"برداشت {self.amount} تومان - {self.purpose}"

    def get_jalali_withdrawal_date(self):
        return datetime2jalali(self.withdrawal_date).strftime('%Y/%m/%d %H:%M')

    def save(self, *args, **kwargs):
        # اگر این یک برداشت جدید است، موجودی کارت را کاهش می‌دهیم
        if not self.pk:
            if self.bank_card.balance >= self.amount:
                self.bank_card.balance -= self.amount
                self.bank_card.save()
            else:
                raise ValueError("موجودی کارت کافی نیست")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # هنگام حذف برداشت، موجودی کارت را افزایش می‌دهیم
        self.bank_card.balance += self.amount
        self.bank_card.save()
        super().delete(*args, **kwargs)
