from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer
from .permissions import IsOwner


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for user task categories.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        # Strict user isolation: user can only see their own categories
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for tasks with priority tagging, scheduling, and categorization.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'priority', 'status']
    ordering = ['due_date', '-created_at']

    def get_queryset(self):
        # Strict user isolation: user can only see their own tasks
        queryset = Task.objects.filter(user=self.request.user).select_related('category')

        # Filter by priority (?priority=HIGH)
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority.upper())

        # Filter by status (?status=COMPLETED)
        task_status = self.request.query_params.get('status')
        if task_status:
            queryset = queryset.filter(status=task_status.upper())

        # Filter by category id (?category=1)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch', 'post'], url_path='mark-completed')
    def mark_completed(self, request, pk=None):
        """
        Custom endpoint to toggle/mark task as COMPLETED.
        """
        task = self.get_object()
        task.status = 'COMPLETED'
        task.save()
        serializer = self.get_serializer(task)
        return Response(
            {"message": "Task marked as completed successfully.", "task": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Returns user task metrics (total, pending, completed, high priority).
        """
        user_tasks = Task.objects.filter(user=request.user)
        total = user_tasks.count()
        completed = user_tasks.filter(status='COMPLETED').count()
        in_progress = user_tasks.filter(status='IN_PROGRESS').count()
        pending = user_tasks.filter(status='PENDING').count()
        high_priority = user_tasks.filter(priority='HIGH', status__in=['PENDING', 'IN_PROGRESS']).count()

        return Response({
            "total_tasks": total,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress,
            "pending_tasks": pending,
            "urgent_high_priority_tasks": high_priority,
        }, status=status.HTTP_200_OK)
