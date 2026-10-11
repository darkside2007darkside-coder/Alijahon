import secrets

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Model, CharField, ImageField, DecimalField, TextField, SmallIntegerField, ForeignKey, \
    DateTimeField, CASCADE, PositiveIntegerField, TextChoices, SlugField
from django.db.models.deletion import PROTECT, SET_NULL
from django.utils.text import slugify


# --------------------------- USER ---------------------------
class CustomerUserManager(UserManager):
    def _create_user_object(self, phone_number, email, password, **extra_fields):
        if not phone_number:
            raise ValueError("The given phone_number must be set")
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, phone_number, email, password, **extra_fields):
        user = self._create_user_object(phone_number, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)


    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)

class User(AbstractUser):

    class RoleType(TextChoices):
        OPERATOR = "operator" , "Operator"
        ADMIN = "admin" , "Admin"
        USER = "user" , "User"

    phone_number = CharField(max_length=255, unique=True)
    USERNAME_FIELD = 'phone_number'
    role = CharField(max_length=255, choices=RoleType.choices, default=RoleType.USER)
    first_name = CharField(max_length=255, blank=True, null=True)
    last_name = CharField(max_length=255, blank=True, null=True)
    region = ForeignKey("apps.Region", on_delete=SET_NULL, related_name="users", blank=True, null=True)
    district = ForeignKey("apps.District", on_delete=SET_NULL, related_name="users", blank=True, null=True)
    telegram_id = CharField(max_length=255, blank=True, null=True)
    description = TextField(blank=True, null=True)
    api_key = CharField(max_length=64,unique=True,blank=True,null=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)


    username = None
    objects = CustomerUserManager()




class Region(Model):
    title = CharField(max_length=255)

    def __str__(self):
        return self.title


class District(Model):
    title = CharField(max_length=255)
    region = ForeignKey(Region, on_delete=CASCADE, related_name="districts")

    def __str__(self):
        return self.title


# --------------------------- PRODUCTS ---------------------------
class Category(Model):
    title = CharField(max_length=255)
    image = CharField(max_length=500)
    slug = SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        counter = 1
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{counter}"
            counter += 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(Model):
    title = CharField(max_length=255)
    price = DecimalField(max_digits=12, decimal_places=0)
    description = TextField()
    quantity = SmallIntegerField()
    category = ForeignKey('apps.Category', on_delete=CASCADE, related_name="products")
    created_at = DateTimeField(auto_now_add=True)
    slug = SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        counter = 1
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{counter}"
            counter += 1
        return super().save(*args, **kwargs)

    @property
    def thumbnail_image(self):
        return self.product_images.order_by('order').first()

    def __str__(self):
        return self.title


class ProductImage(Model):
    image = ImageField(upload_to="categories/")
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name="product_images")
    order = PositiveIntegerField(default=1)


# --------------------------- ORDER ---------------------------

class Order(Model):
    class StatusType(TextChoices):
        YANGI = "yangi", "Yangi"
        QADOQLASH = "qadoqlash", "Qadoqlash"
        YETKAZILMOQDA = "yetkazilmoqda", "Yetkazilmoqda"
        YETKAZILDI = "yetkazildi", "Yetkazildi"
        KEYIN_OLADI = "keyin oladi", "Keyin oladi"
        HOLD = "hold", "Hold"
        QAYTIB_KELDI = "qaytib keldi", "Qaytib keldi"
        BEKOR_QILINDI = "bekor qilindi", "Bekor qilindi"
        ARXIV = "arxiv", "Arxiv"

    username = CharField(max_length=255, )
    phone_number = CharField(max_length=255)
    quantity = PositiveIntegerField()
    status = CharField(max_length=255, choices=StatusType.choices, default=StatusType.YANGI)
    update_description = TextField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    # цена доставки
    unit_price = DecimalField(max_digits=12,decimal_places=0, blank=True, null=True)
    discount = DecimalField(max_digits=12,decimal_places=0,default=0, blank=True, null=True)

    product = ForeignKey('apps.Product', on_delete=PROTECT, related_name="orders")
    user = ForeignKey('apps.User', on_delete=SET_NULL, related_name="orders", blank=True, null=True)
    oqim = ForeignKey("apps.Oqim",on_delete=SET_NULL,related_name="orders",null=True,blank=True)

    region = ForeignKey("apps.Region", on_delete=SET_NULL, null=True, blank=True, related_name="orders")
    district = ForeignKey("apps.District", on_delete=SET_NULL, null=True, blank=True, related_name="orders")
    address = TextField(blank=True, null=True)



class Oqim(Model):
    title = CharField(max_length=255)
    discount = DecimalField(max_digits=12, decimal_places=0)
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name="oqims")
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name="oqims")

