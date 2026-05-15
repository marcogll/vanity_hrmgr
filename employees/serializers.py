from rest_framework import serializers
from .models import User, Branch, Employee


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'telegram_chat_id']
        read_only_fields = ['date_joined']


class BranchSerializer(serializers.ModelSerializer):
    empleados_count = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'active', 'empleados_count', 'created_at']

    def get_empleados_count(self, obj):
        return obj.employees.filter(status='activo').count()


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    branch_nombre = serializers.CharField(source='branch.name', read_only=True)
    manager_nombre = serializers.CharField(source='manager.user.get_full_name', read_only=True)
    antiguedad = serializers.IntegerField(read_only=True)
    dias_vacaciones_prox = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'employee_number', 'curp', 'rfc', 'tipo_contrato',
                  'fecha_ingreso', 'saldo_vacaciones', 'branch', 'branch_nombre',
                  'manager', 'manager_nombre', 'status', 'antiguedad', 'dias_vacaciones_prox',
                  'created_at', 'updated_at']
        read_only_fields = ['saldo_vacaciones', 'created_at', 'updated_at']

    def get_antiguedad(self, obj):
        return obj.calcular_antiguedad()

    def get_dias_vacaciones_prox(self, obj):
        return obj.get_dias_vacaciones()


class EmployeeCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = ['employee_number', 'curp', 'rfc', 'tipo_contrato', 'fecha_ingreso',
                  'branch', 'manager', 'status', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', 'password123')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        user = User.objects.create_user(
            username=validated_data['employee_number'],
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        employee = Employee.objects.create(user=user, **validated_data)
        return employee