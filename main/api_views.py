from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Project, Alternative, Relation, RelationshipType, Criterion, Like
from .serializers import (
    ProjectSerializer, AlternativeSerializer, RelationSerializer,
    RelationshipTypeSerializer, CriterionSerializer
)
from django.db import models
from rest_framework import serializers


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            # For list action, show only public projects or user's own projects
            return Project.objects.filter(
                models.Q(is_public=True) | models.Q(user=self.request.user)
            ).distinct()
        # For other actions, show only user's own projects
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        project = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user, project=project
        )
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return Response({
            'liked': liked,
            'likes_count': project.likes.count()
        })

    @action(detail=True, methods=['post'])
    def copy_project(self, request, pk=None):
        original_project = self.get_object()
        # Prevent copying own projects
        if original_project.user == request.user:
            return Response(
                {'error': 'Ви не можете скопіювати свій власний проект.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Create new project
        new_project = Project.objects.create(
            user=request.user,
            title=f"Копія: {original_project.title}",
            description=original_project.description,
            image=original_project.image,
            is_public=False
        )
        # Copy relationship types
        relationship_type_map = {}
        for rel_type in original_project.relationship_types.all():
            new_rel_type = RelationshipType.objects.create(
                project=new_project,
                name=rel_type.name,
                description=rel_type.description
            )
            relationship_type_map[rel_type.id] = new_rel_type
        # Copy alternatives
        for alt in original_project.alternatives.all():
            new_alt = Alternative.objects.create(
                project=new_project,
                name=alt.name,
                description=alt.description,
                rating=alt.rating,
                criteria_values=alt.criteria_values
            )
            if alt.relationship:
                new_alt.relationship = relationship_type_map[alt.relationship.id]
                new_alt.save()
        serializer = self.get_serializer(new_project)
        return Response(serializer.data)


class AlternativeViewSet(viewsets.ModelViewSet):
    serializer_class = AlternativeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Alternative.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(
            Project, id=project_id, user=self.request.user
        )
        serializer.save(project=project)


class RelationViewSet(viewsets.ModelViewSet):
    serializer_class = RelationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Relation.objects.filter(
            models.Q(source__project_id=project_id) |
            models.Q(target__project_id=project_id)
        )

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(
            Project, id=project_id, user=self.request.user
        )
        # Verify that both alternatives belong to the project
        source = serializer.validated_data['source']
        target = serializer.validated_data['target']
        if source.project != project or target.project != project:
            raise serializers.ValidationError(
                "Обидві альтернативи повинні належати до одного проекту"
            )
        serializer.save()


class RelationshipTypeViewSet(viewsets.ModelViewSet):
    serializer_class = RelationshipTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return RelationshipType.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(
            Project, id=project_id, user=self.request.user
        )
        serializer.save(project=project)


class CriterionViewSet(viewsets.ModelViewSet):
    serializer_class = CriterionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Criterion.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(
            Project, id=project_id, user=self.request.user
        )
        serializer.save(project=project) 