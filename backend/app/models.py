from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from uuid import uuid4
# Create your models here.



class MyAccountManager(BaseUserManager):
    def create_user(self,username, email, password=None):
        if not email:
            raise ValueError('email is required')
        if not username:
            raise ValueError('username is required')
        
        user = self.model(
            email= self.normalize_email(email),
            username= username
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username,email,password):
        user = self.create_user(
             email= self.normalize_email(email),
            username= username,
            password= password,
        
        )
        user.is_admin=True
        user.is_superuser=True
        user.is_staff= True
        user.save(using=self._db)
        return user












class Account(AbstractBaseUser):
    email       = models.EmailField(verbose_name='email', max_length=60, unique=True )
    username    = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login  = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin    = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True, null=True, default='default.jgp', upload_to='profile')

    
    objects = MyAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def  has_module_perms(self, app_label):
        return True


def deserialize_user(user):
    """Deserialize user instance to JSON."""
    return {
        'id': user.id, 'username': user.username, 'email': user.email,
        
    }


class Friend(models.Model):
    user = models.ForeignKey(Account, related_name='acct',on_delete=models.CASCADE)
    friends = models.ManyToManyField(Account, related_name='fri')

    def __str__(self):
        return self.user.username


class TrackableDateModel(models.Model):
    """Abstract model to Track the creation/updated date for a model."""

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-create_date']

def _generate_unique_uri():
    """Generates a unique uri for the chat session."""
    return str(uuid4()).replace('-', '')[:15]

class Room(TrackableDateModel):
    owner = models.ForeignKey(Account, on_delete=models.PROTECT)
    friend  = models.ForeignKey(Account,related_name="chat_friend", on_delete=models.PROTECT)
    uri = models.CharField(max_length=50,default=_generate_unique_uri)

    def __str__(self):
        return f"{self.owner.username} {self.id} "


class Message(models.Model):
    user = models.ForeignKey(Account, on_delete=models.PROTECT)
    room = models.ForeignKey(
        Room, related_name='messages', on_delete=models.PROTECT
    )
    message = models.TextField(max_length=2000)

    def to_json(self):
        """deserialize message to JSON."""
        return {'user': deserialize_user(self.user), 'message': self.message}


class RoomMember(TrackableDateModel):
    """Store all users in a chat session."""

    room = models.ForeignKey(
        Room, related_name='members', on_delete=models.PROTECT
    )
    user = models.ForeignKey(Account, on_delete=models.PROTECT)






@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_friends(sender,instance=None, created=False, **kwargs):
    if created:
        Friend.objects.create(user=instance)