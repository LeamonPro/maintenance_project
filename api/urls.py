from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, 
    TechnicianViewSet, 
    OrdreImputationViewSet,
    TaskViewSet, 
    AdvancementNoteViewSet, 
    NotificationViewSet, 
    CustomAuthToken,
    AdminUserViewSet, 
    AdminTaskReportView,
    PreventiveTaskTemplateViewSet, 
    PreventiveChecklistSubmissionView
)

router = DefaultRouter()
router.register(r'userprofiles', UserProfileViewSet, basename='userprofile')
router.register(r'technicians', TechnicianViewSet)
router.register(r'ordres-imputation', OrdreImputationViewSet, basename='ordreimputation')
router.register(r'tasks', TaskViewSet)
router.register(r'advancement-notes', AdvancementNoteViewSet, basename='advancementnote')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'admin/users', AdminUserViewSet, basename='admin-user')
router.register(r'admin/preventive-task-templates', PreventiveTaskTemplateViewSet, basename='preventive-task-template')

urlpatterns = [
    path('', include(router.urls)),
    path('auth-token/', CustomAuthToken.as_view(), name='api_auth_token'),
    path('admin/task-reports/', AdminTaskReportView.as_view(), name='admin_task_reports'),
    path('submit-preventive-checklist/', PreventiveChecklistSubmissionView.as_view(), name='submit_preventive_checklist'),
    path('tasks/<int:pk>/print/', TaskViewSet.as_view({'get': 'print_task'}), name='task-print'),
]