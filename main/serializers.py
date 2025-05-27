from rest_framework import serializers
from .models import Project, Alternative, Relation, RelationshipType, Criterion, Like
from authentication.serializers import UserSerializer

class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterion
        fields = ['id', 'name', 'type', 'description', 'project']
        read_only_fields = ['id']

class RelationshipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipType
        fields = ['id', 'name', 'description', 'project']
        read_only_fields = ['id']

class AlternativeSerializer(serializers.ModelSerializer):
    criteria_values = serializers.JSONField()
    relationship = RelationshipTypeSerializer(read_only=True)
    relationship_id = serializers.PrimaryKeyRelatedField(
        queryset=RelationshipType.objects.all(),
        source='relationship',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Alternative
        fields = ['id', 'name', 'description', 'rating', 'criteria_values', 
                 'relationship', 'relationship_id', 'project']
        read_only_fields = ['id']

class RelationSerializer(serializers.ModelSerializer):
    source = AlternativeSerializer(read_only=True)
    target = AlternativeSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Alternative.objects.all(),
        source='source',
        write_only=True
    )
    target_id = serializers.PrimaryKeyRelatedField(
        queryset=Alternative.objects.all(),
        source='target',
        write_only=True
    )

    class Meta:
        model = Relation
        fields = ['id', 'source', 'target', 'source_id', 'target_id', 'relation_type']
        read_only_fields = ['id']

class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    alternatives = AlternativeSerializer(many=True, read_only=True)
    criteria = CriterionSerializer(many=True, read_only=True)
    relationship_types = RelationshipTypeSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'is_public', 'image', 'user',
                 'alternatives', 'criteria', 'relationship_types', 'created_at',
                 'likes_count', 'is_liked']
        read_only_fields = ['id', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'project']
        read_only_fields = ['id'] 