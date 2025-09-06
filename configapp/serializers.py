from rest_framework import serializers
from django.utils.timezone import now
from django.contrib.auth import authenticate
from .models import User, ToDoList, OTP


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"success": False, "detail": "Bunday foydalanuvchi topilmadi."})

        auth_user = authenticate(username=user.username, password=password)
        if auth_user is None:
            raise serializers.ValidationError({"success": False, "detail": "Username yoki parol noto‘g‘ri."})

        if not auth_user.is_active:
            raise serializers.ValidationError({"success": False, "detail": "Foydalanuvchi OTP tasdiqlanmagan."})

        attrs["user"] = auth_user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "phone_number", "email", "password", "is_admin", "is_user", "is_active"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PhoneRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            phone_number=validated_data["phone_number"],
            password=validated_data["password"],
            is_user=True,
            is_active=False,  # OTP tasdiqlanmaguncha
        )
        otp = OTP.objects.create(phone_number=user.phone_number)
        self.context["otp_code"] = otp.code  # test uchun
        return user


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone = attrs.get("phone_number")
        code = attrs.get("code")

        try:
            otp = OTP.objects.filter(phone_number=phone).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"detail": "OTP topilmadi."})

        if otp.code != code:
            raise serializers.ValidationError({"detail": "OTP noto‘g‘ri."})

        try:
            user = User.objects.get(phone_number=phone)
            user.is_active = True
            user.save()
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Foydalanuvchi topilmadi."})

        attrs["user"] = user
        return attrs


class ToDoListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ToDoList
        fields = ["id", "title", "bajarilgan", "done_time", "user"]

    def update(self, instance, validated_data):
        bajarilgan = validated_data.get("bajarilgan", instance.bajarilgan)
        if bajarilgan and not instance.done_time:
            instance.done_time = now()
        return super().update(instance, validated_data)
