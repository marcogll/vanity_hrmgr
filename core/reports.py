"""Generador de reportes Excel para exportación de datos."""

import openpyxl
from openpyxl.styles import Font
from django.http import HttpResponse


def generate_excel_report(queryset, filename, headers, data_func):
    """Genera un archivo Excel a partir de un queryset.

    Args:
        queryset: Queryset de Django con los datos a exportar
        filename: Nombre del archivo sin extensión
        headers: Lista de nombres de columnas
        data_func: Función que recibe un objeto y retorna lista de valores

    Returns:
        HttpResponse con el archivo Excel para descarga
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte"

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)

    for row_num, obj in enumerate(queryset, 2):
        data = data_func(obj)
        for col_num, value in enumerate(data, 1):
            ws.cell(row=row_num, column=col_num).value = str(value) if value is not None else ""

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response