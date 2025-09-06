from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404

from .models import User, ToDoList
from .serializers import (
    LoginSerializer, UserSerializer, ToDoListSerializer,
    PhoneRegisterSerializer, VerifyOTPSerializer
)
from .make_token import get_tokens_for_user


class LoginUser(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.validated_data.get("username"))
        token = get_tokens_for_user(user)
        return Response(data=token)


class RegisterUser(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ToDoListView(generics.ListCreateAPIView):
    serializer_class = ToDoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return ToDoList.objects.all()
        return ToDoList.objects.filter(user=user, bajarilgan=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ToDoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ToDoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return ToDoList.objects.all()
        return ToDoList.objects.filter(user=user, bajarilgan=False)


class PhoneRegisterView(APIView):
    @swagger_auto_schema(request_body=PhoneRegisterSerializer)
    def post(self, request):
        serializer = PhoneRegisterSerializer(data=request.data, context={})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        otp_code = serializer.context["otp_code"]  # test uchun
        return Response({
            "detail": "Ro‘yxatdan o‘tildi. SMS kodi yuborildi.",
            "otp_code": otp_code  # testda ko‘rsatamiz
        }, status=201)



class VerifyOTPView(APIView):
    @swagger_auto_schema(request_body=VerifyOTPSerializer)
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token = get_tokens_for_user(user)
        return Response({"detail": "Telefon tasdiqlandi", **token}, status=200)
