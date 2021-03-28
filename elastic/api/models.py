from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=40, blank=False, null=False)

    class Meta:
        ordering = ('-id', 'name',)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='books')

    class Meta:
        ordering = ('-id', 'created',)

    def __str__(self):
        return self.title


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    books = models.ManyToManyField(Book, related_name='authors')

    def __str__(self):
        return self.first_name

    class Meta:
        ordering = ['first_name']


class User(AbstractBaseUser, PermissionsMixin):
    numeric = RegexValidator(r'^\+?1?\d{9,15}$', 'Only numeric characters are allowed.')
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(_('username'), max_length=150, unique=True,
                                help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                validators=[username_validator],
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                }, blank=True
                                )
    email = models.EmailField(_('email address'), blank=False, unique=True, db_index=True)
    image = models.FileField(upload_to='picture', null=True)
    address = models.CharField(max_length=120, default='', blank=True)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    phone = models.CharField(max_length=30, default='', validators=[numeric])
    date_of_birth = models.DateField(blank=True, null=True)
    password = models.CharField(_('password'), max_length=128)
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active status'), default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        ordering = ['-id']

    def __str__(self):
        return self.email
