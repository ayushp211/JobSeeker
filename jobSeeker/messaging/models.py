from django.db import models
from django.contrib.auth.models import User
from job_postings.models import Job, JobApplication

class Conversation(models.Model):
    """
    Represents a conversation between a recruiter and a job seeker.
    Conversations are initiated by recruiters when they want to contact candidates.
    """
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recruiter_conversations')
    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_seeker_conversations')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    subject = models.CharField(max_length=200, help_text="Subject line for the conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('recruiter', 'job_seeker', 'job')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation: {self.recruiter.username} ↔ {self.job_seeker.username} - {self.subject}"
    
    def get_other_participant(self, user):
        """Returns the other participant in the conversation"""
        if user == self.recruiter:
            return self.job_seeker
        return self.recruiter
    
    def get_latest_message(self):
        """Returns the most recent message in this conversation"""
        return self.messages.order_by('-created_at').first()

class Message(models.Model):
    """
    Individual messages within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} in conversation {self.conversation.id}"
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        self.save()

class MessageNotification(models.Model):
    """
    Track unread messages for users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_notifications')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='notifications')
    unread_count = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'conversation')
    
    def __str__(self):
        return f"{self.user.username} - {self.unread_count} unread in conversation {self.conversation.id}"