from django.contrib import admin
from .models import Project, Alternative, Relation


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'description')


@admin.register(Alternative)
class AlternativeAdmin(admin.ModelAdmin):
    list_display = ('name', 'project')
    search_fields = ('name', 'description')


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('source', 'relation_type', 'target')
    list_filter = ('relation_type',)
