import uuid
from django.db import models

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=80, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.id})"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    STATUS_CHOICES = [
        ('complete', 'Complete'),
        ('incomplete', 'Incomplete'),
        ('error', 'Error'),
    ]

    id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='complete')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}... [{self.status}]"
