from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Request, RequestComment
from .serializers import RequestSerializer, RequestCommentSerializer
from core.permissions import IsAdminOrManager


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == 'admin':
            return True
        if request.user.role == 'manager':
            return obj.empleado.branch in request.user.branch_set.all()
        return obj.empleado.user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'manager':
            return obj.empleado.branch in request.user.branch_set.all()
        return obj.empleado.user == request.user


class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['aprobar', 'rechazar']:
            return [IsAdminOrManager()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Request.objects.all()
        if user.role == 'manager':
            branches = user.branch_set.all()
            return Request.objects.filter(empleado__branch__in=branches)
        return Request.objects.filter(empleado__user=user)

    def perform_create(self, serializer):
        empleado = self.request.user.employee
        serializer.save(empleado=empleado)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        request_obj = self.get_object()
        if request_obj.estatus != 'pendiente':
            return Response({'error': 'La solicitud ya fue procesada'}, status=status.HTTP_400_BAD_REQUEST)

        request_obj.estatus = 'aprobado'
        request_obj.comentario_admin = request.data.get('comentario', '')
        request_obj.save()

        if request_obj.tipo == 'vacacion':
            dias = request_obj.dias_solicitados()
            empleado = request_obj.empleado
            empleado.saldo_vacaciones -= dias
            empleado.save()

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        request_obj = self.get_object()
        if request_obj.estatus != 'pendiente':
            return Response({'error': 'La solicitud ya fue procesada'}, status=status.HTTP_400_BAD_REQUEST)

        request_obj.estatus = 'rechazado'
        request_obj.comentario_admin = request.data.get('comentario', '')
        request_obj.save()

        return Response(RequestSerializer(request_obj).data)


class RequestCommentViewSet(viewsets.ModelViewSet):
    serializer_class = RequestCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RequestComment.objects.filter(request_id=self.kwargs['request_pk'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)