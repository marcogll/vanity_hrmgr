from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employees.views import UserViewSet, BranchViewSet, EmployeeViewSet
from requests.views import RequestViewSet, RequestCommentViewSet
from absences.views import AbsenceViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'requests', RequestViewSet, basename='requests')
router.register(r'absences', AbsenceViewSet, basename='absences')

urlpatterns = [
    path('', include(router.urls)),
]