from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('', views.financial_dashboard, name='dashboard'),
    path('transactions/', views.transactions_list, name='transactions'),
    path('tag-summary/', views.tag_summary, name='tag_summary'),
    path('bank-cards/', views.bank_cards_list, name='bank_cards'),
]

