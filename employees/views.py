from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Branch, Employee
from .serializers import UserSerializer, BranchSerializer, EmployeeSerializer, EmployeeCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def generate_api_key(self, request):
        user = request.user
        if user.role not in ['admin', 'manager']:
            return Response({'error': 'Solo admin y manager pueden generar API keys'}, status=status.HTTP_403_FORBIDDEN)

        from .authentication import generate_api_key
        user.api_key = generate_api_key()
        user.save()

        return Response({'api_key': user.api_key, 'message': 'API Key generada correctamente'})

    @action(detail=False, methods=['delete'])
    def revoke_api_key(self, request):
        user = request.user
        user.api_key = None
        user.save()
        return Response({'message': 'API Key revocada'})


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Branch.objects.all()
        if user.role == 'manager':
            return Branch.objects.filter(id__in=user.branch_set.values_list('id', flat=True))
        return Branch.objects.filter(active=True)

    @action(detail=True, methods=['get'])
    def empleados(self, request, pk=None):
        branch = self.get_object()
        employees = branch.employees.filter(status='activo')
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Employee.objects.all()
        if user.role == 'manager':
            return Employee.objects.filter(branch__in=user.branch_set.all())
        return Employee.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            employee = request.user.employee
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'No employee profile'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)