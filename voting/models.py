# voting/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Election(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def __str__(self):
        return self.name
    
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @classmethod
    def get_current_election(cls):
        return cls.objects.filter(
            start_time__lte=timezone.now(),
            end_time__gte=timezone.now()
        ).first()

class Party(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.ImageField(upload_to='party_symbols/')
    
    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidate_photos/')
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.party.name})"

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    voter_id = models.CharField(max_length=20, unique=True)
    aadhar_number = models.CharField(max_length=12, unique=True)
    phone_number = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.voter_id

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('voter', 'election')