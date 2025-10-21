from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from .models import Conversation, Message, MessageNotification
from .forms import StartConversationForm, MessageForm
from job_postings.models import JobApplication, Job
from user_accounts.models import UserProfile

@login_required
def inbox(request):
    """
    Display all conversations for the current user
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Get all active conversations where user is either recruiter or job seeker
    active_conversations = Conversation.objects.filter(
        Q(recruiter=request.user) | Q(job_seeker=request.user),
        is_active=True
    ).select_related('recruiter', 'job_seeker', 'job').prefetch_related('messages')

    # Get closed conversations for reference
    closed_conversations = Conversation.objects.filter(
        Q(recruiter=request.user) | Q(job_seeker=request.user),
        is_active=False
    ).select_related('recruiter', 'job_seeker', 'job').prefetch_related('messages')
    
    # Add unread count and other participant for active conversations
    for conversation in active_conversations:
        conversation.unread_count = Message.objects.filter(
            conversation=conversation,
            sender__isnull=False
        ).exclude(sender=request.user).filter(is_read=False).count()
        conversation.other_participant = conversation.get_other_participant(request.user)
    
    # Add other participant for closed conversations
    for conversation in closed_conversations:
        conversation.other_participant = conversation.get_other_participant(request.user)
    
    template_data = {
        'conversations': active_conversations,
        'closed_conversations': closed_conversations,
        'user_type': user_profile.user_type,
    }
    
    return render(request, 'messaging/inbox.html', {'template_data': template_data})

@login_required
def conversation_detail(request, conversation_id):
    """
    Display a specific conversation and allow sending messages
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Check if conversation is active
        if not conversation.is_active:
            messages.warning(request, 'This conversation has been closed and is no longer accessible.')
            return redirect('messaging.inbox')
        
        # Check if user is part of this conversation
        if request.user not in [conversation.recruiter, conversation.job_seeker]:
            messages.error(request, 'You do not have permission to view this conversation.')
            return redirect('messaging.inbox')
            
    except Conversation.DoesNotExist:
        messages.error(request, 'The requested conversation does not exist.')
        return redirect('messaging.inbox')
    
    # Mark all messages in this conversation as read for the current user
    Message.objects.filter(
        conversation=conversation
    ).exclude(sender=request.user).update(is_read=True)
    
    # Get all messages in this conversation
    conversation_messages = conversation.messages.all().select_related('sender')
    
    # Handle new message
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation's updated_at timestamp
            conversation.save()
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Message sent successfully',
                    'message_id': message.id,
                    'sender': message.sender.username,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            messages.success(request, 'Message sent successfully!')
            return redirect('messaging.conversation_detail', conversation_id=conversation_id)
    else:
        form = MessageForm()
    
    template_data = {
        'conversation': conversation,
        'messages': conversation_messages,
        'form': form,
        'other_participant': conversation.get_other_participant(request.user),
    }
    
    return render(request, 'messaging/conversation_detail.html', {'template_data': template_data})

@login_required
def start_conversation(request, user_id, job_id=None):
    """
    Allow recruiters to start a conversation with a job seeker
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Only recruiters can start conversations
    if user_profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can start conversations.')
        return redirect('messaging.inbox')
    
    job_seeker = get_object_or_404(User, id=user_id)
    job_seeker_profile = get_object_or_404(UserProfile, user=job_seeker)
    
    # Only job seekers can be contacted
    if job_seeker_profile.user_type != 'job_seeker':
        messages.error(request, 'You can only contact job seekers.')
        return redirect('messaging.inbox')
    
    job = None
    application = None
    
    if job_id:
        job = get_object_or_404(Job, id=job_id, posted_by=request.user)
        # Check if there's an application for this job by this job seeker
        try:
            application = JobApplication.objects.get(job=job, applicant=job_seeker)
        except JobApplication.DoesNotExist:
            pass
    
    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        recruiter=request.user,
        job_seeker=job_seeker,
        job=job,
        is_active=True
    ).first()
    
    if existing_conversation:
        messages.info(request, 'You already have an active conversation with this candidate.')
        return redirect('messaging.conversation_detail', conversation_id=existing_conversation.id)
    
    if request.method == 'POST':
        form = StartConversationForm(request.POST)
        if form.is_valid():
            # Use get_or_create to safely handle duplicate conversations
            conversation, created = Conversation.objects.get_or_create(
                recruiter=request.user,
                job_seeker=job_seeker,
                job=job,
                defaults={
                    'subject': form.cleaned_data['subject'],
                    'application': application,
                    'is_active': True
                }
            )
            
            if created:
                messages.success(request, f'Conversation started with {job_seeker.get_full_name() or job_seeker.username}!')
            else:
                messages.info(request, 'You already have an active conversation with this candidate.')
            
            return redirect('messaging.conversation_detail', conversation_id=conversation.id)
    else:
        form = StartConversationForm()
    
    template_data = {
        'form': form,
        'job_seeker': job_seeker,
        'job': job,
        'application': application,
    }
    
    return render(request, 'messaging/start_conversation.html', {'template_data': template_data})

@login_required
def send_message_ajax(request, conversation_id):
    """
    AJAX endpoint for sending messages
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    conversation = get_object_or_404(Conversation, id=conversation_id, is_active=True)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.recruiter, conversation.job_seeker]:
        return JsonResponse({'success': False, 'error': 'You do not have permission to send messages in this conversation.'})
    
    form = MessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        message.sender = request.user
        message.save()
        
        # Update conversation's updated_at timestamp
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': message.id,
            'sender': message.sender.username,
            'sender_full_name': message.sender.get_full_name() or message.sender.username,
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
            'created_at_display': message.created_at.strftime('%b %d, %Y at %I:%M %p')
        })
    else:
        return JsonResponse({'success': False, 'error': 'Invalid message content'})

@login_required
def get_unread_count(request):
    """
    AJAX endpoint to get unread message count for the current user
    """
    unread_count = Message.objects.filter(
        conversation__in=Conversation.objects.filter(
            Q(recruiter=request.user) | Q(job_seeker=request.user),
            is_active=True
        )
    ).exclude(sender=request.user).filter(is_read=False).count()
    
    return JsonResponse({'unread_count': unread_count})

@login_required
def close_conversation(request, conversation_id):
    """
    Allow users to close/deactivate a conversation
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, is_active=True)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.recruiter, conversation.job_seeker]:
        messages.error(request, 'You do not have permission to close this conversation.')
        return redirect('messaging.inbox')
    
    if request.method == 'POST':
        conversation.is_active = False
        conversation.save()
        messages.success(request, 'Conversation closed successfully.')
        return redirect('messaging.inbox')
    
    template_data = {
        'conversation': conversation,
        'other_participant': conversation.get_other_participant(request.user),
    }
    
    return render(request, 'messaging/close_conversation.html', {'template_data': template_data})