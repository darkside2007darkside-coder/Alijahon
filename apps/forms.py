import re
from django.core.exceptions import ValidationError

from django.forms import Form, CharField, PasswordInput, IntegerField, TextInput
from django.forms.models import ModelForm
from django.contrib.auth import get_user_model, authenticate

from apps.models import Order, Oqim

User = get_user_model()

# ============ USER ============
class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'region', 'district', 'telegram_id', 'description'


class UserChangePasswordForm(Form):
    new_password = CharField(min_length=6, widget=PasswordInput)
    confirm_password = CharField(min_length=6, widget=PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        new_password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Parollar mos kelmaydi.")

        return cleaned_data


# ============ Login ============
class LoginForm(Form):
    phone_number = CharField(max_length=255)
    password = CharField(max_length=128, widget=PasswordInput)

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        return re.sub(r'\D', '', phone_number)

    def clean(self):
        cleaned_data = super().clean()

        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data.get("password")

        if not phone_number or not password:
            return cleaned_data

        user = authenticate(
            username=phone_number,
            password=password
        )

        if user is None:
            raise ValidationError("Invalid phone number or password")

        self.session_user = user
        return super().clean()

class RegisterModelForm(ModelForm):
    conf_password = CharField(max_length=10)
    class Meta:
        model = User
        fields = "phone_number", "password", "conf_password"

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        return re.sub(r'\D', '', phone_number)



    def clean(self):
        cleaned_data = super().clean()

        password = self.cleaned_data.get("password")
        conf_password = self.cleaned_data.get("conf_password")
        if password and conf_password:
            if len(password) < 6:
                raise ValidationError("Parol 6-ta dan kam bumasligi kerak")

            if password != conf_password:
                raise ValidationError("Parol xato terilgan")

        return cleaned_data


    # def clean_conf_password(self):
    #     password = self.data.get("password")
    #     confirm_password = self.data.get("conf_password")
    #     if password != confirm_password:
    #         raise ValidationError("Passwords is invalid")


# ============ ORDER ============


class OrderFormView(ModelForm):
    class Meta:
        model = Order
        fields = "username", "phone_number", "quantity"

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        return re.sub(r'\D', '', phone_number)

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get("username")
        phone_number = self.cleaned_data.get("phone_number")

        if username.isdigit():
            raise ValidationError("Ismiz xato kiritilgan")

        if phone_number and len(phone_number) != 12:
            raise ValidationError("Telefon raqam totug'ri terilgan")

        return cleaned_data


# ============ OPERATOR ============
class OperatorOrderForm(Form):
    quantity = IntegerField()


class OperatorOrderMiniUpdate_FormView(ModelForm): # в странице оператора рядом с звонком стоит карандащ
    class Meta:
        model = Order
        fields = "status", "update_description"

from django import forms
from .models import Order, District


class OperatorOrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "username",
            "phone_number",
            "quantity",
            "region",
            "district",
            "address",
            "status",
            "update_description",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "op-field-input",
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "op-field-input",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "op-field-input",
                "min": 1,
            }),
            "region": forms.Select(attrs={
                "class": "op-field-select",
                "id": "id_region",
            }),
            "district": forms.Select(attrs={
                "class": "op-field-select",
                "id": "id_district",
            }),
            "address": forms.Textarea(attrs={
                "class": "op-field-textarea",
                "rows": 3,
            }),
            "status": forms.RadioSelect(),
            "update_description": forms.Textarea(attrs={
                "class": "op-field-textarea",
                "rows": 6,
                "maxlength": 500,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        region_id = None

        if self.is_bound:
            region_id = self.data.get("region")
        elif self.instance and self.instance.region_id:
            region_id = self.instance.region_id

        if region_id:
            self.fields["district"].queryset = District.objects.filter(
                region_id=region_id
            )
        else:
            self.fields["district"].queryset = District.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        region = cleaned_data.get("region")
        district = cleaned_data.get("district")

        if region and district and district.region_id != region.id:
            raise forms.ValidationError(
                "Tanlangan tuman ushbu viloyatga tegishli emas."
            )

        return cleaned_data


# ============ OQIM ============
class OqimFormView(ModelForm):
    class Meta:
        model = Oqim
        fields = "title", "discount"

