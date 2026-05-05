import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import os
import sys
import threading
from datetime import datetime
from PIL import Image, ImageTk

import db_manager
import reconocimiento
import reportes


ctk.set_appearance_mode("Light")
BG_COLOR = "#F4F2EE"       
CARD_BG = "#FFFFFF"        
ACCENT_GREEN = "#2E593F"   
TEXT_DARK = "#1E1E1E"
TEXT_MUTED = "#555555"     

class DashboardPremium(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Asistencia - Banda de Guerra")
        self.geometry("1280x800")
        self.configure(fg_color=BG_COLOR)

        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=25, fg_color=CARD_BG)
        self.sidebar_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ns")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) 

        self.logo_icon = ctk.CTkLabel(self.sidebar_frame, text="🥁 BandaApp", font=("Segoe UI", 24, "bold"), text_color=TEXT_DARK)
        self.logo_icon.grid(row=0, column=0, pady=(30, 10), padx=20, sticky="w")
        
        self.sub_label = ctk.CTkLabel(self.sidebar_frame, text="TECNM TUXTEPEC", font=("Segoe UI", 12, "bold"), text_color="#10B981")
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Menú Principal
        ctk.CTkLabel(self.sidebar_frame, text="MENÚ PRINCIPAL", font=("Segoe UI", 11, "bold"), text_color=TEXT_MUTED).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.btn_dash = ctk.CTkButton(self.sidebar_frame, text="🏠 Pantalla de Inicio", corner_radius=10, 
                                      fg_color=TEXT_DARK, text_color="#FFF", font=("Segoe UI", 15), anchor="w", height=45)
        self.btn_dash.grid(row=3, column=0, pady=5, padx=15, sticky="ew")

        self.btn_registrar = ctk.CTkButton(self.sidebar_frame, text="👤 Dar de Alta Alumno", corner_radius=10, 
                                           fg_color="transparent", text_color=TEXT_DARK, hover_color="#E5E5E5", 
                                           font=("Segoe UI", 15), anchor="w", command=self.accion_registrar, height=45)
        self.btn_registrar.grid(row=4, column=0, pady=5, padx=15, sticky="ew")

        self.btn_baja = ctk.CTkButton(self.sidebar_frame, text="🚫 Dar de Baja Alumno", corner_radius=10, 
                                      fg_color="transparent", text_color="#DC2626", hover_color="#FEE2E2", 
                                      font=("Segoe UI", 15), anchor="w", command=self.accion_baja_logica, height=45)
        self.btn_baja.grid(row=5, column=0, pady=5, padx=15, sticky="ew")

        self.btn_inventario = ctk.CTkButton(self.sidebar_frame, text="🎺 Préstamo de Equipo", corner_radius=10, 
                                            fg_color="transparent", text_color=TEXT_DARK, hover_color="#E5E5E5", 
                                            font=("Segoe UI", 15), anchor="w", command=self.abrir_modulo_inventario, height=45)
        self.btn_inventario.grid(row=6, column=0, pady=5, padx=15, sticky="ew")

        ctk.CTkLabel(self.sidebar_frame, text="IMPRIMIR Y GUARDAR", font=("Segoe UI", 11, "bold"), text_color=TEXT_MUTED).grid(row=7, column=0, padx=20, pady=(20, 5), sticky="w")

        self.btn_reportes = ctk.CTkButton(self.sidebar_frame, text="📄 Imprimir Reporte (PDF)", corner_radius=10, 
                                          fg_color="transparent", text_color=TEXT_DARK, hover_color="#E5E5E5", 
                                          font=("Segoe UI", 15), anchor="w", command=self.accion_reportes, height=45)
        self.btn_reportes.grid(row=8, column=0, pady=5, padx=15, sticky="nw")

        self.btn_excel = ctk.CTkButton(self.sidebar_frame, text="📗 Guardar en Excel", corner_radius=10, 
                                       fg_color="transparent", text_color="#10B981", hover_color="#D1FAE5", 
                                       font=("Segoe UI", 15), anchor="w", command=self.accion_excel, height=45)
        self.btn_excel.grid(row=9, column=0, pady=5, padx=15, sticky="nw")

       
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(10, 30), pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(2, weight=1)

       
        self.header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent", height=80)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.titles_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.titles_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(self.titles_frame, text="Bienvenido al Sistema de Asistencia", font=("Segoe UI", 26, "bold"), text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(self.titles_frame, text="Aquí puede ver el resumen de los alumnos y controlar la cámara.", font=("Segoe UI", 15), text_color=TEXT_MUTED).pack(anchor="w")

       
        self.kpi_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        elementos_totales, asistencias_hoy, total_instrumentos = self.obtener_estadisticas()

        self.card_1 = ctk.CTkFrame(self.kpi_frame, fg_color=CARD_BG, corner_radius=20, height=100)
        self.card_1.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(self.card_1, text="Total de Alumnos", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 0))
        self.lbl_kpi_elementos = ctk.CTkLabel(self.card_1, text=str(elementos_totales), font=("Segoe UI", 32, "bold"), text_color=TEXT_DARK)
        self.lbl_kpi_elementos.pack(anchor="w", padx=20, pady=(0, 15))

        self.card_2 = ctk.CTkFrame(self.kpi_frame, fg_color=CARD_BG, corner_radius=20, height=100)
        self.card_2.grid(row=0, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(self.card_2, text="Asistencias de Hoy", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 0))
        self.lbl_kpi_asistencias = ctk.CTkLabel(self.card_2, text=str(asistencias_hoy), font=("Segoe UI", 32, "bold"), text_color="#10B981")
        self.lbl_kpi_asistencias.pack(anchor="w", padx=20, pady=(0, 15))

        self.card_3 = ctk.CTkFrame(self.kpi_frame, fg_color=CARD_BG, corner_radius=20, height=100)
        self.card_3.grid(row=0, column=2, padx=10, sticky="ew")
        ctk.CTkLabel(self.card_3, text="Instrumentos Prestados", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 0))
        self.lbl_kpi_instrumentos = ctk.CTkLabel(self.card_3, text=str(total_instrumentos), font=("Segoe UI", 32, "bold"), text_color="#3B82F6")
        self.lbl_kpi_instrumentos.pack(anchor="w", padx=20, pady=(0, 15))

        self.card_4 = ctk.CTkFrame(self.kpi_frame, fg_color=ACCENT_GREEN, corner_radius=20, height=100)
        self.card_4.grid(row=0, column=3, padx=(10, 0), sticky="ew")
        ctk.CTkLabel(self.card_4, text="Estado del Sistema", font=("Segoe UI", 14), text_color="#D1FAE5").pack(anchor="w", padx=20, pady=(15, 0))
        ctk.CTkLabel(self.card_4, text="Excelente", font=("Segoe UI", 28, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(0, 15))

        
        self.split_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.split_frame.grid(row=2, column=0, sticky="nsew")
        self.split_frame.grid_columnconfigure(0, weight=7)
        self.split_frame.grid_columnconfigure(1, weight=3)
        self.split_frame.grid_rowconfigure(0, weight=1)

        self.camara_frame = ctk.CTkFrame(self.split_frame, corner_radius=25, fg_color=CARD_BG)
        self.camara_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.cam_header = ctk.CTkFrame(self.camara_frame, fg_color="transparent")
        self.cam_header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(self.cam_header, text="Cámara de Asistencia", font=("Segoe UI", 18, "bold"), text_color=TEXT_DARK).pack(side="left")

        self.video_container = ctk.CTkFrame(self.camara_frame, fg_color="#E5E5E5", corner_radius=15)
        self.video_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.mensaje_camara = "📸 La cámara está apagada.\n\nPresione el botón rojo de abajo\npara empezar a pasar lista."
        self.cam_placeholder_label = ctk.CTkLabel(
            self.video_container, text=self.mensaje_camara, 
            font=("Segoe UI", 18, "bold"), text_color=TEXT_MUTED, justify="center"
        )
        self.cam_placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        self.video_pantalla = tk.Label(self.video_container, bg="#E5E5E5", bd=0)

        
        self.right_panel = ctk.CTkFrame(self.split_frame, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1) 
        self.right_panel.grid_rowconfigure(1, weight=1) 

        
        self.admin_card = ctk.CTkFrame(self.right_panel, corner_radius=25, fg_color=CARD_BG)
        self.admin_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        ctk.CTkLabel(self.admin_card, text="Otras Tareas", font=("Segoe UI", 18, "bold"), text_color=TEXT_DARK).pack(anchor="w", padx=25, pady=(20, 15))

        self.btn_f1 = ctk.CTkButton(self.admin_card, text="📝 Justificar Falta (Enfermedad)", fg_color="#F3F4F6", text_color=TEXT_DARK, hover_color="#E5E5E5", anchor="w", font=("Segoe UI", 14), height=50, command=self.accion_justificar)
        self.btn_f1.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.admin_card, text="Use este botón si un alumno faltó\npero tiene permiso o receta médica.", font=("Segoe UI", 12), text_color=TEXT_MUTED, justify="left").pack(anchor="w", padx=25)

        
        self.action_card = ctk.CTkFrame(self.right_panel, corner_radius=25, fg_color=CARD_BG)
        self.action_card.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        ctk.CTkLabel(self.action_card, text="Control de la Cámara", font=("Segoe UI", 18, "bold"), text_color=TEXT_DARK).pack(pady=(25, 10))
        ctk.CTkLabel(self.action_card, text="Asegúrese de que el alumno se\npare frente a la computadora.", font=("Segoe UI", 14), text_color=TEXT_MUTED, justify="center").pack(pady=(0, 20))

        self.btn_pase_lista = ctk.CTkButton(
            self.action_card, text="🔴 ENCENDER CÁMARA", command=self.accion_pase_lista, 
            height=60, font=("Segoe UI", 16, "bold"), corner_radius=15, 
            fg_color="#DC2626", hover_color="#B91C1C"
        )
        self.btn_pase_lista.pack(padx=20, fill="x", pady=(0, 20))

   
    def cerrar_aplicacion(self):
        reconocimiento.detener_camara()
        self.destroy()
        os._exit(0) 

    def obtener_estadisticas(self):
        try:
            conexion = db_manager.conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM elementos WHERE estado = 'Activo' OR estado IS NULL")
            elementos = cursor.fetchone()[0]
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM asistencias WHERE fecha = ? AND estado = 'Presente'", (fecha_hoy,))
            asistencias = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM inventario WHERE asignado_a IS NOT NULL AND asignado_a != ''")
            instrumentos = cursor.fetchone()[0]
            conexion.close()
            return elementos, asistencias, instrumentos
        except:
            return 0, 0, 0
            
    def actualizar_kpis_ui(self):
        elem, asi, inst = self.obtener_estadisticas()
        self.lbl_kpi_elementos.configure(text=str(elem))
        self.lbl_kpi_asistencias.configure(text=str(asi))
        self.lbl_kpi_instrumentos.configure(text=str(inst))

    def accion_registrar(self):
        dialogo_nc = ctk.CTkInputDialog(text="Escriba el Número de Control (Ej. 20350211):", title="Dar de Alta")
        nc = dialogo_nc.get_input()
        if nc and nc.strip(): 
            dialogo_nom = ctk.CTkInputDialog(text="Escriba el Nombre Completo del alumno:", title="Dar de Alta")
            nom = dialogo_nom.get_input()
            if nom and nom.strip():
                reconocimiento.registrar_elemento(nc, nom)
                self.actualizar_kpis_ui()
            else:
                messagebox.showwarning("Aviso", "El nombre no puede estar vacío.")
        elif nc is not None:
            messagebox.showwarning("Aviso", "El número de control no puede estar vacío.")

    def accion_baja_logica(self):
        nc = ctk.CTkInputDialog(text="Escriba el Número de Control a Dar de Baja:", title="Dar de Baja")
        nc = nc.get_input() if nc else None
        
        if nc and nc.strip():
            nc = nc.strip()
            conexion = db_manager.conectar()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT tipo_equipo, no_serie FROM inventario WHERE asignado_a = ?", (nc,))
            equipos = cursor.fetchall()
            if equipos:
                lista = "\n".join([f"• {e[0]} (Serie: {e[1]})" for e in equipos])
                messagebox.showerror("Operación Cancelada", f"No se puede dar de baja a este alumno porque aún tiene equipo prestado:\n\n{lista}\n\nPrimero vaya a 'Préstamo de Equipo' y reciba los instrumentos.")
                conexion.close()
                return
                
            cursor.execute("UPDATE elementos SET estado = 'Inactivo' WHERE no_control = ?", (nc,))
            if cursor.rowcount > 0:
                messagebox.showinfo("Baja Exitosa", f"El alumno {nc} fue dado de baja correctamente.")
                self.actualizar_kpis_ui()
            else:
                messagebox.showerror("Error", "No se encontró a ningún alumno ACTIVO con ese número.")
            conexion.commit()
            conexion.close()

    def accion_reportes(self):
        exito, mensaje = reportes.generar_pdf()
        if exito: messagebox.showinfo("PDF Creado", mensaje)
        else: messagebox.showwarning("Aviso", mensaje)

    def accion_excel(self):
        try:
            exito, mensaje = reportes.generar_excel()
            if exito: messagebox.showinfo("Excel Creado", mensaje)
            else: messagebox.showwarning("Aviso", mensaje)
        except: messagebox.showerror("Error", "Ocurrió un problema al generar el Excel.")

    def accion_justificar(self):
        nc_input = ctk.CTkInputDialog(text="Escriba el Número de Control del alumno para justificar HOY:", title="Justificar Falta")
        nc = nc_input.get_input()
        
        if nc and nc.strip():
            nc = nc.strip()
            conexion = db_manager.conectar()
            cursor = conexion.cursor()
        
            cursor.execute("SELECT id FROM elementos WHERE no_control = ? AND (estado = 'Activo' OR estado IS NULL)", (nc,))
            if cursor.fetchone():
                cursor.execute("INSERT INTO asistencias (no_control, fecha, hora, estado) VALUES (?, ?, ?, ?)",
                               (nc, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), "Justificado"))
                conexion.commit()
                messagebox.showinfo("Éxito", f"Se ha justificado la falta del alumno: {nc}.")
            else: 
                messagebox.showerror("Error", "El alumno no está registrado o fue dado de baja.")
            conexion.close()

   
    def abrir_modulo_inventario(self):
        self.modal_inv = ctk.CTkToplevel(self)
        self.modal_inv.title("Préstamo y Control de Equipo")
        self.modal_inv.geometry("900x600")
        
        
        
        self.modal_inv.configure(fg_color=BG_COLOR)

        ctk.CTkLabel(self.modal_inv, text="Gestión de Instrumentos", font=("Segoe UI", 24, "bold"), text_color=TEXT_DARK).pack(pady=(20, 10))
        ctk.CTkLabel(self.modal_inv, text="Aquí puede registrar nuevos instrumentos o prestárselos a los alumnos.", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(pady=(0, 20))

        btn_frame = ctk.CTkFrame(self.modal_inv, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkButton(btn_frame, text="➕ Agregar Nuevo Instrumento", fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 14, "bold"), height=40, command=self._registrar_equipo_modal).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="👤 Prestar a un Alumno", fg_color="#3B82F6", hover_color="#2563EB", font=("Segoe UI", 14, "bold"), height=40, command=self._asignar_equipo_modal).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="♻️ Recibir Instrumento", fg_color="#EF4444", hover_color="#DC2626", font=("Segoe UI", 14, "bold"), height=40, command=self._liberar_equipo_modal).pack(side="left", padx=10)

        table_frame = tk.Frame(self.modal_inv, bg=CARD_BG)
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#E5E5E5", foreground=TEXT_DARK)
        style.configure("Treeview", font=("Segoe UI", 12), rowheight=35)

        self.tree_inv = ttk.Treeview(table_frame, columns=("id", "tipo", "serie", "estado", "asignado_a"), show="headings")
        for col, txt in zip(("id", "tipo", "serie", "estado", "asignado_a"), ("ID", "Qué es", "Código / Serie", "Estado", "Lo tiene prestado:")):
            self.tree_inv.heading(col, text=txt)
            
        self.tree_inv.column("id", width=50, anchor="center")
        self.tree_inv.column("tipo", width=180, anchor="w")
        self.tree_inv.column("serie", width=150, anchor="center")
        self.tree_inv.column("estado", width=120, anchor="center")
        self.tree_inv.column("asignado_a", width=200, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_inv.yview)
        self.tree_inv.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree_inv.pack(side="left", fill="both", expand=True)

        self._refrescar_tabla_inventario()

    def _refrescar_tabla_inventario(self):
        for item in self.tree_inv.get_children(): self.tree_inv.delete(item)
        conexion = db_manager.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, tipo_equipo, no_serie, estado_fisico, asignado_a FROM inventario ORDER BY id DESC")
        for r in cursor.fetchall():
            self.tree_inv.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4] if r[4] else "NADIE (Está guardado)"))
        conexion.close()

    def _registrar_equipo_modal(self):
        tipo_input = ctk.CTkInputDialog(text="¿Qué instrumento es? (Ej. Tambor, Corneta):", title="Nuevo")
        tipo = tipo_input.get_input()
        if tipo and tipo.strip():
            serie_input = ctk.CTkInputDialog(text="Escriba el Número de Serie o Código que tiene pintado:", title="Nuevo")
            serie = serie_input.get_input()
            if serie and serie.strip():
                try:
                    conexion = db_manager.conectar()
                    cursor = conexion.cursor()
                    cursor.execute("INSERT INTO inventario (tipo_equipo, no_serie, estado_fisico) VALUES (?, ?, ?)", (tipo.strip(), serie.strip(), "Bueno"))
                    conexion.commit()
                    self._refrescar_tabla_inventario()
                    conexion.close()
                except: 
                    messagebox.showerror("Error", "Ya existe un instrumento guardado con ese mismo código.")
            elif serie is not None:
                 messagebox.showwarning("Aviso", "El código no puede estar vacío.")

    def _asignar_equipo_modal(self):
        serie_input = ctk.CTkInputDialog(text="Escriba el Código del instrumento que va a prestar:", title="Prestar")
        serie = serie_input.get_input()
        if serie and serie.strip():
            nc_input = ctk.CTkInputDialog(text="Escriba el No. de Control del alumno que se lo lleva:", title="Prestar")
            nc = nc_input.get_input()
            if nc and nc.strip():
                conexion = db_manager.conectar()
                cursor = conexion.cursor()
                cursor.execute("SELECT id FROM elementos WHERE no_control = ? AND (estado = 'Activo' OR estado IS NULL)", (nc.strip(),))
                if cursor.fetchone():
                    cursor.execute("UPDATE inventario SET asignado_a = ? WHERE no_serie = ?", (nc.strip(), serie.strip()))
                    if cursor.rowcount > 0:
                        conexion.commit()
                        self._refrescar_tabla_inventario()
                        self.actualizar_kpis_ui()
                    else:
                        messagebox.showerror("Error", "No se encontró un instrumento con ese código.")
                else: 
                    messagebox.showerror("Error", "Ese alumno no existe o fue dado de baja.")
                conexion.close()

    def _liberar_equipo_modal(self):
        serie_input = ctk.CTkInputDialog(text="Escriba el Código del instrumento que le están devolviendo:", title="Devolución")
        serie = serie_input.get_input()
        if serie and serie.strip():
            conexion = db_manager.conectar()
            cursor = conexion.cursor()
            cursor.execute("UPDATE inventario SET asignado_a = NULL WHERE no_serie = ?", (serie.strip(),))
            if cursor.rowcount > 0:
                conexion.commit()
                self._refrescar_tabla_inventario()
                self.actualizar_kpis_ui()
            else:
                messagebox.showerror("Error", "No se encontró el instrumento o ya estaba en bodega.")
            conexion.close()

    
    def accion_pase_lista(self):
        if "ENCENDER" in self.btn_pase_lista.cget("text"):
            self.btn_pase_lista.configure(text="⏹ APAGAR CÁMARA Y GUARDAR", fg_color=ACCENT_GREEN, hover_color="#1E3E2A")
            self.cam_placeholder_label.place_forget()
            self.video_pantalla.place(relx=0.5, rely=0.5, anchor="center") 
            self.latest_frame = None

            threading.Thread(target=reconocimiento.iniciar_pase_lista, args=(self.actualizar_frame_ui,), daemon=True).start()
            self._loop_video()
        else:
            reconocimiento.detener_camara() 
            self.latest_frame = None 
            self.btn_pase_lista.configure(text="🔴 ENCENDER CÁMARA", fg_color="#DC2626", hover_color="#B91C1C")
            
            self.video_pantalla.place_forget()
            self.cam_placeholder_label.place(relx=0.5, rely=0.5, anchor="center") 
            messagebox.showinfo("Proceso Terminado", "La cámara se apagó y todos los registros se guardaron correctamente.")
            self.actualizar_kpis_ui()

    def actualizar_frame_ui(self, frame_rgb):
        self.latest_frame = frame_rgb

    def _loop_video(self):
        if not self.winfo_exists(): return
        if "APAGAR" in self.btn_pase_lista.cget("text"):
            if getattr(self, 'latest_frame', None) is not None:
                try:
                    img = Image.fromarray(self.latest_frame)
                    img = img.resize((720, 480)) 
                    self.tk_video_img = ImageTk.PhotoImage(image=img)
                    self.video_pantalla.configure(image=self.tk_video_img)
                except Exception:
                    pass
            self.after(30, self._loop_video)

if __name__ == "__main__":
    db_manager.inicializar_bd()
    app = DashboardPremium()
    app.mainloop()