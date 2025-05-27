from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import CustomUser

User = get_user_model()

# Create your models here.

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    image = models.ImageField(upload_to='project_images/', null=True, blank=True)

    def __str__(self):
        return self.title

class Criterion(models.Model):
    TYPE_CHOICES = [
        ('numeric', 'Числовий'),
        ('text', 'Текстовий'),
        ('color', 'Колір'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['project', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class RelationshipType(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='relationship_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['project', 'name']

    def __str__(self):
        return self.name

class Alternative(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='alternatives')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    relationship = models.ForeignKey(RelationshipType, on_delete=models.SET_NULL, null=True, blank=True)
    criteria_values = models.JSONField(default=dict, blank=True)  # Store criteria values as JSON

    def __str__(self):
        return self.name

class Relation(models.Model):
    RELATION_TYPES = [
        ('domination', 'Домінування'),
        ('indifference', 'Байдужість'),
    ]

    source = models.ForeignKey(Alternative, on_delete=models.CASCADE, related_name='outgoing_relations')
    target = models.ForeignKey(Alternative, on_delete=models.CASCADE, related_name='incoming_relations')
    relation_type = models.CharField(max_length=20, choices=RELATION_TYPES)

    class Meta:
        unique_together = ['source', 'target']

    def __str__(self):
        return f"{self.source} {self.get_relation_type_display()} {self.target}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.project.title}"
