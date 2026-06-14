from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('balance/', views.BalanceView.as_view(), name='balance'),
    
    # Transactions
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),
    path('transfer/', views.TransferView.as_view(), name='transfer'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='transactions'),
    
    # Search
    path('search/', views.UserSearchView.as_view(), name='search'),
]