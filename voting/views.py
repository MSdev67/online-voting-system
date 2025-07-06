# voting/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from .models import Voter, Candidate, Vote, Election
from .forms import VoterRegistrationForm, OTPVerificationForm, LoginForm
from .utils import send_otp
import logging
from django.utils import timezone
from .models import Election

logger = logging.getLogger(__name__)

def home(request):
    current_election = Election.objects.filter(
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).first()
    return render(request, 'voting/home.html', {
        'current_election': current_election
    })


def voter_login(request):
    if request.user.is_authenticated:
        return redirect('vote')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                voter = Voter.objects.get(
                    voter_id=form.cleaned_data['voter_id'],
                    aadhar_number=form.cleaned_data['aadhar_number'],
                    phone_number=form.cleaned_data['phone_number']
                )
                request.session['voter_id'] = voter.voter_id
                request.session['voter_pk'] = voter.pk
                
                otp = send_otp(voter.phone_number)
                request.session['otp'] = otp
                
                messages.info(request, "OTP sent to your registered phone number")
                return redirect('otp_verify')
            except Voter.DoesNotExist:
                messages.error(request, "Invalid credentials or voter not registered")
    else:
        form = LoginForm()
    return render(request, 'voting/login.html', {'form': form})

def otp_verify(request):
    if 'voter_pk' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            stored_otp = request.session.get('otp')
            entered_otp = form.cleaned_data['otp']
            
            if stored_otp == entered_otp or settings.DEBUG:
                try:
                    voter = Voter.objects.get(pk=request.session['voter_pk'])
                    user = voter.user
                    voter.is_verified = True
                    voter.save()
                    login(request, user)
                    
                    for key in ['voter_id', 'voter_pk', 'otp']:
                        if key in request.session:
                            del request.session[key]
                    
                    messages.success(request, "OTP verified successfully!")
                    return redirect('vote')
                except Voter.DoesNotExist:
                    messages.error(request, "Voter not found")
            else:
                messages.error(request, "Invalid OTP")
    else:
        form = OTPVerificationForm()
    return render(request, 'voting/otp_verify.html', {'form': form})

@login_required
def vote(request):
    try:
        voter = Voter.objects.get(user=request.user)
        current_election = Election.get_current_election()
        
        if not current_election:
            messages.error(request, "No active election at this time")
            return redirect('home')
        
        if not voter.is_verified:
            messages.error(request, "Please verify your identity first")
            return redirect('login')
        
        if voter.has_voted:
            messages.warning(request, "You have already voted in this election!")
            return redirect('results')
        
        if request.method == 'POST':
            candidate_id = request.POST.get('candidate')
            if candidate_id:
                try:
                    candidate = Candidate.objects.get(id=candidate_id, election=current_election)
                    Vote.objects.create(
                        voter=voter,
                        candidate=candidate,
                        election=current_election
                    )
                    voter.has_voted = True
                    voter.save()
                    messages.success(request, "Your vote has been recorded!")
                    return redirect('results')
                except Candidate.DoesNotExist:
                    messages.error(request, "Invalid candidate selected")
        
        candidates = Candidate.objects.filter(election=current_election)
        return render(request, 'voting/vote.html', {
            'candidates': candidates,
            'election': current_election
        })
        
    except Voter.DoesNotExist:
        messages.error(request, "Voter profile not found")
        return redirect('home')

@login_required
def results(request):
    try:
        voter = Voter.objects.get(user=request.user)
        current_election = Election.get_current_election()
        
        if not current_election:
            messages.error(request, "No active election")
            return redirect('home')
            
        vote_stats = Vote.objects.filter(election=current_election) \
                       .values('candidate') \
                       .annotate(vote_count=Count('candidate')) \
                       .order_by('-vote_count')
        
        total_votes = Vote.objects.filter(election=current_election).count()
        
        if vote_stats.exists():
            winner = vote_stats.first()
            winner_candidate = Candidate.objects.get(id=winner['candidate'])
            
            return render(request, 'voting/results.html', {
                'winner': winner_candidate,
                'total_votes': total_votes,
                'vote_percentage': (winner['vote_count'] / total_votes) * 100 if total_votes > 0 else 0,
                'election': current_election
            })
            
        return render(request, 'voting/results.html', {
            'message': "No votes have been cast yet",
            'election': current_election
        })
        
    except Voter.DoesNotExist:
        messages.error(request, "Voter profile not found")
        return redirect('home')

def register(request):
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            if Voter.objects.filter(voter_id=form.cleaned_data['voter_id']).exists():
                form.add_error('voter_id', "This Voter ID is already registered")
            elif Voter.objects.filter(aadhar_number=form.cleaned_data['aadhar_number']).exists():
                form.add_error('aadhar_number', "This Aadhar number is already registered")
            else:
                try:
                    user = User.objects.create_user(
                        username=form.cleaned_data['voter_id'],
                        password=form.cleaned_data['password1']
                    )
                    voter = Voter.objects.create(
                        user=user,
                        voter_id=form.cleaned_data['voter_id'],
                        aadhar_number=form.cleaned_data['aadhar_number'],
                        phone_number=form.cleaned_data['phone_number']
                    )
                    messages.success(request, "Registration successful! Please login.")
                    return redirect('login')
                except Exception as e:
                    messages.error(request, f"Registration failed: {str(e)}")
    else:
        form = VoterRegistrationForm()
    return render(request, 'voting/register.html', {'form': form})

def custom_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def profile(request):
    """Display user profile information"""
    try:
        voter = Voter.objects.get(user=request.user)
        voting_history = Vote.objects.filter(voter=voter).select_related('candidate', 'election').order_by('-timestamp')
        
        return render(request, 'voting/profile.html', {
            'voter': voter,
            'voting_history': voting_history
        })
    except Voter.DoesNotExist:
        messages.error(request, "Voter profile not found")
        return redirect('home')