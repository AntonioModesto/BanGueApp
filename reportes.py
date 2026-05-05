import os
import csv
from fpdf import FPDF
from datetime import datetime
import db_manager

def generar_pdf():
    conexion = db_manager.conectar()
    cursor = conexion.cursor()
    query = '''
        SELECT a.fecha, a.hora, e.no_control, e.nombre, a.estado
        FROM asistencias a
        JOIN elementos e ON a.no_control = e.no_control
        ORDER BY a.fecha DESC, a.hora DESC
    '''
    cursor.execute(query)
    registros = cursor.fetchall()
    conexion.close()

    if not registros:
        return False, "No hay asistencias registradas."

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="BANDA DE GUERRA - TECNM TUXTEPEC", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, txt="Reporte General de Asistencias", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 10, txt=f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='C')
    pdf.ln(5)

    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(25, 10, "Fecha", border=1, align='C', fill=True)
    pdf.cell(20, 10, "Hora", border=1, align='C', fill=True)
    pdf.cell(30, 10, "No. Control", border=1, align='C', fill=True)
    pdf.cell(85, 10, "Nombre", border=1, align='C', fill=True)
    pdf.cell(30, 10, "Estado", border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font("Arial", '', 10)
    for reg in registros:
        fecha, hora, no_control, nombre, estado = reg
        pdf.cell(25, 10, str(fecha), border=1, align='C')
        pdf.cell(20, 10, str(hora), border=1, align='C')
        pdf.cell(30, 10, str(no_control), border=1, align='C')
        pdf.cell(85, 10, str((nombre[:38] + '..') if len(nombre) > 38 else nombre), border=1, align='L')
        pdf.cell(30, 10, str(estado), border=1, align='C')
        pdf.ln()

    nombre_archivo = "Reporte_Asistencias.pdf"
    try:
        pdf.output(os.path.join(os.path.dirname(__file__), nombre_archivo))
        return True, f"¡Éxito! PDF guardado: {nombre_archivo}"
    except Exception as e:
        return False, f"Error: {e}"

def generar_excel():
    conexion = db_manager.conectar()
    cursor = conexion.cursor()
    query = '''
        SELECT a.fecha, a.hora, e.no_control, e.nombre, a.estado
        FROM asistencias a
        JOIN elementos e ON a.no_control = e.no_control
        ORDER BY a.fecha DESC, a.hora DESC
    '''
    cursor.execute(query)
    registros = cursor.fetchall()
    conexion.close()

    if not registros:
        return False, "No hay asistencias registradas."

    nombre_archivo = "Reporte_Asistencias.csv"
    ruta = os.path.join(os.path.dirname(__file__), nombre_archivo)
    
    try:
        with open(ruta, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Hora", "No. Control", "Nombre", "Estado Asistencia"])
            for reg in registros:
                writer.writerow(reg)
        return True, f"¡Éxito! Excel (CSV) guardado: {nombre_archivo}"
    except Exception as e:
        return False, f"Error: {e}"