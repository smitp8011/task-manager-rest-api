from django.utils import timezone
from rest_framework import serializers
from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'user', 'tasks_count', 'created_at']
        read_only_fields = ['id', 'user', 'tasks_count', 'created_at']

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def validate_name(self, value):
        user = self.context['request'].user
        # Check uniqueness per user on create or update
        category_id = self.instance.id if self.instance else None
        exists = Category.objects.filter(user=user, name__iexact=value).exclude(id=category_id).exists()
        if exists:
            raise serializers.ValidationError("A category with this name already exists for your account.")
        return value.strip()


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    category_detail = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'priority',
            'status',
            'due_date',
            'category',
            'category_detail',
            'user',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_title(self, value):
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise serializers.ValidationError("Task title must be at least 3 characters long.")
        return cleaned

    def validate_category(self, value):
        # Granular validation: ensure user cannot assign another user's category
        if value is not None:
            user = self.context['request'].user
            if value.user != user:
                raise serializers.ValidationError("Invalid category. You can only assign categories that belong to you.")
        return value

    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be scheduled in the past.")
        return value
