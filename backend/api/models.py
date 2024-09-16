from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save


class User(AbstractUser):
    """
    A User class that inherit from AbstractUser class
    """
    username = models.CharField(max_length=100, default='null')
    email = models.EmailField(unique=True)
    # Override the default logging to be by email field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    location = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.full_name


class Schedule(models.Model):
    allDay = models.BooleanField(default=False)
    startAt = models.DateTimeField()
    endAt = models.DateTimeField()

    def __str__(self):
        return f"Schedule: {self.start_at} - {self.end_at}"


class Event(models.Model):
    STATUS_CHOICES = (
        ('ON', 'Online'),
        ('OF', 'Offline'),
    )
    TYPE_CHOICES = (
        ('PD', 'Personal Date'),
        ('ME', 'Meeting'),
        ('EV', 'Event'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    location = models.JSONField(null=True, blank=True)
    reminders = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
