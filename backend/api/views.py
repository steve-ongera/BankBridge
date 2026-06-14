from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import User, Transaction
from django.db import models
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    DepositSerializer, WithdrawSerializer, TransferSerializer,
    TransactionSerializer
)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User created successfully',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        user.email = request.data.get('email', user.email)
        user.phone = request.data.get('phone', user.phone)
        user.save()
        return Response(UserSerializer(user).data)

class DepositView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            try:
                new_balance = request.user.deposit(serializer.validated_data['amount'])
                return Response({
                    'message': 'Deposit successful',
                    'new_balance': new_balance
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            try:
                new_balance = request.user.withdraw(serializer.validated_data['amount'])
                return Response({
                    'message': 'Withdrawal successful',
                    'new_balance': new_balance
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransferView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            to_account = serializer.validated_data['to_account']
            amount = serializer.validated_data['amount']
            
            to_user = User.get_user_by_account(to_account)
            if not to_user:
                return Response({'error': 'Recipient account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if to_user == request.user:
                return Response({'error': 'Cannot transfer to yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                new_balance = request.user.transfer(to_user, amount)
                return Response({
                    'message': f'Transfer successful to {to_user.username}',
                    'new_balance': new_balance,
                    'to_account': to_account
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BalanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'balance': request.user.balance,
            'account_number': request.user.account_number
        })

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get transactions where user is sender or receiver
        transactions = Transaction.objects.filter(
            models.Q(from_user=request.user) | models.Q(to_user=request.user)
        )[:50]  # Last 50 transactions
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        
        users = User.objects.filter(
            models.Q(username__icontains=query) |
            models.Q(account_number__icontains=query) |
            models.Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
        
        return Response([{
            'id': user.id,
            'username': user.username,
            'account_number': user.account_number,
            'email': user.email
        } for user in users])