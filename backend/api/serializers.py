from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile, Schedule, Event
# from base.models import User


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    """
    A class that will serialize register fields object into JSON
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
        )
    password2 = serializers.CharField(
        write_only=True, required=True
        )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'message': 'Passwords does not match'}
            )
        return attrs
    # class Meta:
    #     model = User
    #     fields = ('username', 'password', 'email')
    #     extra_kwargs = {'password': {'write_only': True}}

    # def create(self, validated_data):
    #     user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
    #     return user

    def create(self, validate_data):
        user = User.objects.create(
            username=validate_data['username'],
            email=validate_data['email']
        )
        user.set_password(validate_data['password'])
        user.save()
        return user


# Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

#  Login Serializer
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, data):
        user = User.objects.filter(
            email=data['email'],
        )
        print(user)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show the related user as a string (username)
    
    class Meta:
        model = Profile
        fields = ['user', 'full_name', 'location']
        read_only_fields = ['user']  # The user field should be read-only, as it's automatically set

    # Override the update method to handle partial updates
    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance

    # Optional: You can add a create method if needed, although profiles are typically created automatically via signals.
    def create(self, validated_data):
        profile = Profile.objects.create(**validated_data)
        return profile


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['allDay', 'startAt', 'endAt']


class EventSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # Display the owner as the username
    schedule = ScheduleSerializer()  # Use the nested ScheduleSerializer for schedule field
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'owner', 'title', 'event_type', 'event_type_display', 'status', 'status_display',
            'schedule', 'location', 'reminders', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'event_type_display', 'status_display']

    # Override create method to handle nested schedule creation
    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule')
        schedule = Schedule.objects.create(**schedule_data)
        event = Event.objects.create(schedule=schedule, owner=self.context['request'].user, **validated_data)
        return event

    # Override update method to handle nested schedule update
    def update(self, instance, validated_data):
        schedule_data = validated_data.pop('schedule', None)

        # Update event fields
        instance.title = validated_data.get('title', instance.title)
        instance.event_type = validated_data.get('event_type', instance.event_type)
        instance.status = validated_data.get('status', instance.status)
        instance.location = validated_data.get('location', instance.location)
        instance.reminders = validated_data.get('reminders', instance.reminders)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()

        # Update the schedule if schedule data is provided
        if schedule_data:
            instance.schedule.all_day = schedule_data.get('all_day', instance.schedule.all_day)
            instance.schedule.start_at = schedule_data.get('start_at', instance.schedule.start_at)
            instance.schedule.end_at = schedule_data.get('end_at', instance.schedule.end_at)
            instance.schedule.repeat = schedule_data.get('repeat', instance.schedule.repeat)
            instance.schedule.save()
        return instance



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class MyTokenObtainPairSerializerFull(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data =  super().validate(attrs)
        user = self.user
        data['id'] = user.id
        data['username'] = user.username
        data['email'] = user.email
        data['full_name'] = user.profile.full_name
        data['location'] = user.profile.location

        return data
