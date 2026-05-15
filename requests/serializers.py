from rest_framework import serializers
from .models import Request, RequestComment
from employees.models import Employee
from datetime import date, timedelta


class RequestSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.user.get_full_name', read_only=True)
    dias_solicitados = serializers.IntegerField(read_only=True)
    saldo_vacaciones = serializers.FloatField(source='empleado.saldo_vacaciones', read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'tipo', 'fecha_inicio', 'fecha_fin', 'estatus', 'observaciones_sistema',
                  'comentario_admin', 'empleado', 'empleado_nombre', 'dias_solicitados',
                  'fuera_de_condiciones', 'saldo_vacaciones', 'created_at', 'updated_at']
        read_only_fields = ['estatus', 'observaciones_sistema', 'comentario_admin', 'created_at', 'updated_at']

    def validate(self, data):
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError("La fecha de inicio no puede ser posterior a la fecha fin")

        if data['tipo'] == 'vacacion':
            dias = self._calcular_dias_habiles(data['fecha_inicio'], data['fecha_fin'])
            empleado = data['empleado']
            if not self.instance:
                if dias > empleado.saldo_vacaciones:
                    if not data.get('fuera_de_condiciones', False):
                        raise serializers.ValidationError(
                            f"No tienes saldo suficiente. Saldo actual: {empleado.saldo_vacaciones}, días solicitados: {dias}"
                        )
            else:
                dias_actuales = self.instance.dias_solicitados()
                nuevo_saldo = empleado.saldo_vacaciones + dias_actuales
                if dias > nuevo_saldo:
                    if not data.get('fuera_de_condiciones', False):
                        raise serializers.ValidationError("Saldo insuficiente")

        if data['tipo'] == 'permiso':
            dias = self._calcular_dias_habiles(data['fecha_inicio'], data['fecha_fin'])
            if dias > 3:
                raise serializers.ValidationError("Los permisos tienen máximo 3 días hábiles")

            anticipacion = data['fecha_inicio'] - date.today()
            if anticipacion.days < 1 and not data.get('fuera_de_condiciones', False):
                raise serializers.ValidationError("Los permisos deben solicitarse con al menos 24 horas de anticipación")

        return data

    def _calcular_dias_habiles(self, fecha_inicio, fecha_fin):
        from holidays.models import Holiday
        dias = 0
        actual = fecha_inicio
        while actual <= fecha_fin:
            if actual.weekday() < 5 and not Holiday.es_dia_festivo(actual):
                dias += 1
            actual += timedelta(days=1)
        return dias


class RequestCommentSerializer(serializers.ModelSerializer):
    author_nombre = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = RequestComment
        fields = ['id', 'request', 'author', 'author_nombre', 'contenido', 'created_at']
        read_only_fields = ['author', 'created_at']