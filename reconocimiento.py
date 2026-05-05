import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import db_manager  
import tkinter as tk
from tkinter import messagebox

CARPETA_ROSTROS = "rostros_registrados"
pase_activo = False

def registrar_elemento(no_control, nombre):
    """Enciende la cámara, captura un rostro y lo guarda (o reactiva) en SQLite."""
    no_control = str(no_control).strip()
    nombre = str(nombre).strip().upper()

    if not no_control or not nombre:
        messagebox.showwarning("Aviso", "No puedes dejar los campos en blanco.")
        return

    conexion = db_manager.conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, estado FROM elementos WHERE no_control = ?", (no_control,))
    registro = cursor.fetchone()

    es_reactivacion = False

    if registro:
        estado_actual = registro[1]
        if estado_actual == 'Activo' or estado_actual is None:
            messagebox.showerror("Bloqueo de Seguridad", f"El No. Control {no_control} ya está registrado y activo en el sistema.")
            conexion.close()
            return
        else:
            respuesta = messagebox.askyesno("Reactivar Alumno", f"El alumno {no_control} fue dado de baja anteriormente.\n\n¿Deseas REACTIVARLO y tomarle una nueva foto?")
            if respuesta:
                es_reactivacion = True
            else:
                conexion.close()
                return

    cap = cv2.VideoCapture(0)
    print("📸 Presiona 'c' para capturar la foto o 'q' para cancelar.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Registro - Presiona 'c' para capturar", frame)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('c'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_frame)

            if len(encodings) == 1:
                encoding = encodings[0]
                encoding_bytes = encoding.tobytes()
                
                try:
                    if es_reactivacion:
                        cursor.execute("UPDATE elementos SET nombre = ?, rostro_encoding = ?, estado = 'Activo' WHERE no_control = ?",
                                       (nombre, encoding_bytes, no_control))
                        mensaje_exito = f"Elemento {nombre} REACTIVADO exitosamente."
                    else:
                        cursor.execute("INSERT INTO elementos (no_control, nombre, rostro_encoding, estado) VALUES (?, ?, ?, 'Activo')",
                                       (no_control, nombre, encoding_bytes))
                        mensaje_exito = f"Elemento {nombre} REGISTRADO exitosamente."
                        
                    conexion.commit()

                    if not os.path.exists(CARPETA_ROSTROS):
                        os.makedirs(CARPETA_ROSTROS)

                    ruta_imagen = os.path.join(CARPETA_ROSTROS, f"{no_control}.jpg")
                    cv2.imwrite(ruta_imagen, frame)

                    messagebox.showinfo("Éxito", mensaje_exito)
                except Exception as e:
                    messagebox.showerror("Error", f"Error inesperado en BD: {e}")
                finally:
                    conexion.close()
                break 

            elif len(encodings) > 1:
                messagebox.showwarning("Alerta de Seguridad", "Hay más de una persona en la cámara. Debe estar solo.")
            else:
                messagebox.showwarning("Mala Captura", "No se detectó ningún rostro con claridad.")
            
        elif key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def detener_camara():
    global pase_activo
    pase_activo = False


def iniciar_pase_lista(ui_callback=None):
    global pase_activo
    
    conexion = db_manager.conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT no_control, nombre, rostro_encoding FROM elementos WHERE estado = 'Activo' OR estado IS NULL")
    registros = cursor.fetchall()
    conexion.close()

    if not registros:
        return

    nombres_conocidos = []
    encodings_conocidos = []
    no_controles = []

    for reg in registros:
        no_control, nombre, encoding_bytes = reg
        encodings_conocidos.append(np.frombuffer(encoding_bytes, dtype=np.float64))
        nombres_conocidos.append(nombre)
        no_controles.append(no_control)

    cap = cv2.VideoCapture(0)
    pase_activo = True  
    registrados_esta_sesion = set()

    while pase_activo:
        ret, frame = cap.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        if len(face_locations) > 1:
            cv2.putText(frame, "ALERTA: MULTIPLES ROSTROS", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if ui_callback:
                ui_callback(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            continue 

        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(encodings_conocidos, face_encoding, tolerance=0.5)
            nombre_display = "Desconocido"
            color_borde = (0, 0, 255)

            if True in matches:
                first_match_index = matches.index(True)
                nombre_display = nombres_conocidos[first_match_index]
                no_control_match = no_controles[first_match_index]
                color_borde = (0, 255, 0)

                if no_control_match not in registrados_esta_sesion:
                    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                    hora_actual = datetime.now().strftime("%H:%M:%S")
                    
                    conexion = db_manager.conectar()
                    cursor = conexion.cursor()
                    cursor.execute("SELECT id FROM asistencias WHERE no_control = ? AND fecha = ?", (no_control_match, fecha_hoy))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO asistencias (no_control, fecha, hora, estado) VALUES (?, ?, ?, ?)",
                                       (no_control_match, fecha_hoy, hora_actual, "Presente"))
                        conexion.commit()
                    conexion.close()
                    registrados_esta_sesion.add(no_control_match)

            top, right, bottom, left = face_location
            top *= 4; right *= 4; bottom *= 4; left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), color_borde, 2)
            cv2.putText(frame, nombre_display, (left, top - 15), cv2.FONT_HERSHEY_DUPLEX, 0.6, color_borde, 1)

        if ui_callback:
            frame_rgb_ui = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ui_callback(frame_rgb_ui)
        else:
            cv2.imshow("Pase de Lista", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if not ui_callback:
        cv2.destroyAllWindows()