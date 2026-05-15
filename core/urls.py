"""URLs de la API REST con viewsets y endpoint de dashboard."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employees.views import UserViewSet, BranchViewSet, EmployeeViewSet
from requests.views import RequestViewSet, RequestCommentViewSet
from absences.views import AbsenceViewSet
from .api_views import DashboardAPIView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'requests', RequestViewSet, basename='requests')
router.register(r'absences', AbsenceViewSet, basename='absence')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
]