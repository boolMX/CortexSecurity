import customtkinter as ctk
from tkinter import messagebox, Canvas, filedialog
import hashlib
import urllib.request
import urllib.parse
import math
import secrets
import string
import json
import threading
import os
import sys
import random
import time
import webbrowser
import socket
import subprocess
from dotenv import load_dotenv

# --- CARGA DE VARIABLES DE ENTORNO ---
load_dotenv()

# --- CONFIGURACIÓN ESTÉTICA PROFESIONAL ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Tipografías
FUENTE_TITULO = "Segoe UI"
FUENTE_TEXTO = "Segoe UI"
FUENTE_MONO = "Consolas"

# Paleta de Colores Profesional (Cibernético)
COLOR_PRIMARIO = "#005A9C"    # Azul Profundo
COLOR_SECUNDARIO = "#00B4D8"  # Cian Brillante
COLOR_FONDO = "#1E1E1E"       # Gris Oscuro Carbón
COLOR_TEXTO = "#E0E0E0"       # Blanco Suave
COLOR_EXITO = "#00FF66"       # Verde Neón
COLOR_ERROR = "#FF3333"       # Rojo Alerta

class CortexSecuritySuite(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Parámetros Geométricos de la Ventana
        self.title("CortexSecuritySuite v1.0 - Professional Edition")
        self.geometry("650x780")
        self.resizable(False, False)
        
        # 2. Inicialización del Subsistema de Iconos
        self._inicializar_icono_sistema()
        
        # 3. Credenciales e Endpoints de la Infraestructura Cloud
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", "MISSING_KEY") 
        self.URL_HISTORIAL = "https://oymrvsynecygpxsbatum.supabase.co/rest/v1/historial_seguridad"
        self.URL_PHISHING = "https://oymrvsynecygpxsbatum.supabase.co/rest/v1/urls_phishing"
        
        # Variables globales de estado
        self.ultimo_analisis = None
        self.forzando_bruta = False
        self.escaneando_puertos = False
        self.escaneando_subdominios = False
        self.VAULT_FILE = os.path.join(os.path.dirname(__file__), "vault.cortex")
        
        # 4. Configuración del Fondo
        self._configurar_fondo()
        
        # 5. Despliegue de Componentes de la Interfaz Gráfica
        self._ensamblar_componentes_ui()
        
        # 6. Barra de Redes Sociales (Footer)
        self._ensamblar_redes_sociales()

    def _inicializar_icono_sistema(self):
        self.ruta_icono = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.exists(self.ruta_icono):
            try:
                self.iconbitmap(self.ruta_icono)
                if sys.platform == "win32":
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cortex.securitysuite.v10")
            except Exception as e:
                print(f"[-] Advertencia en subsistema de iconos: {e}")

    def _configurar_fondo(self):
        # Fondo liso profesional en lugar de partículas
        self.configure(fg_color=COLOR_FONDO)
        # Si quieres un gradiente sutil o algo más, puedes agregarlo aquí

    def _ensamblar_componentes_ui(self):
        # Título Principal
        self.lbl_titulo = ctk.CTkLabel(
            self, 
            text="Cortex Security Suite", 
            font=(FUENTE_TITULO, 30, "bold"), 
            text_color=COLOR_PRIMARIO, 
            bg_color=COLOR_FONDO
        )
        self.lbl_titulo.pack(pady=(20, 5))
        
        self.lbl_sub = ctk.CTkLabel(
            self, 
            text="Herramientas de Ciberseguridad", 
            font=(FUENTE_TEXTO, 12, "normal"), 
            text_color=COLOR_SECUNDARIO, 
            bg_color=COLOR_FONDO
        )
        self.lbl_sub.pack(pady=(0, 20))
        
        # Tabs
        self.tabview = ctk.CTkTabview(
            self, 
            width=610, 
            height=580, 
            fg_color="#242424",
            segmented_button_selected_color=COLOR_PRIMARIO, 
            segmented_button_selected_hover_color="#004080"
        )
        self.tabview.pack(padx=20, pady=5)
        
        self.tabview.add("Analizador")
        self.tabview.add("Generador")
        self.tabview.add("Hashes")
        self.tabview.add("Filtros")
        self.tabview.add("Historial")
        
        self.setup_tab_analizador()
        self.setup_tab_generador()
        self.setup_tab_hashes()
        self.setup_tab_filtros_nuevos()
        self.setup_tab_historial()

    def _ensamblar_redes_sociales(self):
        frame_footer = ctk.CTkFrame(self, fg_color="transparent", bg_color=COLOR_FONDO)
        frame_footer.pack(side="bottom", fill="x", pady=(0, 12), padx=30)

        lbl_credito = ctk.CTkLabel(
            frame_footer, 
            text="© 2026 Cortex Security Suite v1.0", 
            font=(FUENTE_TEXTO, 10, "italic"), 
            text_color="#555555"
        )
        lbl_credito.pack(side="left")

        frame_links = ctk.CTkFrame(frame_footer, fg_color="transparent")
        frame_links.pack(side="right")

        redes = [
            {"nombre": "GitHub", "url": "https://github.com/boolMX"},
            {"nombre": "LinkedIn", "url": "https://www.linkedin.com/in/diego-antonio-galdos-cruz-433895355/"},
            {"nombre": "Instagram", "url": "https://www.instagram.com/bool.mx/?hl=es"}
        ]

        for red in redes:
            btn_red = ctk.CTkButton(
                frame_links, 
                text=red["nombre"], 
                font=(FUENTE_TEXTO, 10, "bold"), 
                text_color="#888888", 
                fg_color="transparent", 
                hover=False, 
                width=55, 
                height=20, 
                command=lambda u=red["url"]: webbrowser.open(u)
            )
            btn_red.pack(side="left", padx=2)
            btn_red.bind("<Enter>", lambda e, b=btn_red: b.configure(text_color=COLOR_PRIMARIO))
            btn_red.bind("<Leave>", lambda e, b=btn_red: b.configure(text_color="#888888"))

    # =========================================================================
    # CORE DE AUDITORÍA BASE (ANALIZADOR, GENERADOR, HASHES)
    # =========================================================================
    def setup_tab_analizador(self):
        tab = self.tabview.tab("Analizador")
        self.entry_pass = ctk.CTkEntry(
            tab, 
            placeholder_text="Ingresa la contraseña a evaluar...", 
            font=(FUENTE_TEXTO, 13), 
            width=360, 
            height=40, 
            show="*", 
            border_color=COLOR_SECUNDARIO, 
            fg_color="#2A2A2A"
        )
        self.entry_pass.pack(pady=10)
        
        self.btn_analizar = ctk.CTkButton(
            tab, 
            text="ANALIZAR SEGURIDAD", 
            font=(FUENTE_TEXTO, 12, "bold"), 
            fg_color=COLOR_PRIMARIO, 
            text_color="white", 
            hover_color="#004080", 
            width=200, 
            height=40, 
            command=self.iniciar_analisis_asincrono
        )
        self.btn_analizar.pack(pady=5)
        
        self.btn_reporte = ctk.CTkButton(
            tab, 
            text="EXPORTAR REPORTE", 
            font=(FUENTE_TEXTO, 11, "bold"), 
            fg_color="#2A2A2A", 
            border_color=COLOR_PRIMARIO, 
            border_width=1, 
            text_color=COLOR_PRIMARIO, 
            state="disabled", 
            width=200, 
            height=35, 
            command=self.exportar_reporte_auditoria
        )
        self.btn_reporte.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(
            tab, 
            width=400, 
            height=12, 
            progress_color=COLOR_PRIMARIO, 
            fg_color="#2A2A2A"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        
        self.frame_res = ctk.CTkFrame(
            tab, 
            width=480, 
            height=160, 
            corner_radius=10, 
            border_width=1, 
            border_color="#2B2B2B", 
            fg_color="#1F1F1F"
        )
        self.frame_res.pack(pady=10, fill="x", padx=40)
        
        self.lbl_bits = ctk.CTkLabel(self.frame_res, text="Entropía: --", font=(FUENTE_TEXTO, 13), text_color=COLOR_TEXTO)
        self.lbl_bits.pack(pady=(12, 4))
        self.lbl_status = ctk.CTkLabel(self.frame_res, text="Nivel: --", font=(FUENTE_TEXTO, 15, "bold"))
        self.lbl_status.pack(pady=4)
        self.lbl_api = ctk.CTkLabel(self.frame_res, text="Estado en la Red: --", font=(FUENTE_TEXTO, 12), text_color="#8B949E", wraplength=400)
        self.lbl_api.pack(pady=(4, 12))

    def iniciar_analisis_asincrono(self):
        password = self.entry_pass.get()
        if not password: return
        self.btn_analizar.configure(state="disabled", text="ESCANEANDO...")
        threading.Thread(target=self.procesar_analisis_subhilo, args=(password,), daemon=True).start()

    def procesar_analisis_subhilo(self, password):
        # ... (Lógica de análisis igual que antes, solo cambié el User-Agent)
        chars = 0
        if any(c.islower() for c in password): chars += 26
        if any(c.isupper() for c in password): chars += 26
        if any(c.isdigit() for c in password): chars += 10
        if any(not c.isalnum() for c in password): chars += 32
        
        bits = len(password) * math.log2(chars) if chars > 0 and len(password) > 0 else 0
        target_progress = min(bits / 128, 1.0)
        current_progress = 0.0
        while current_progress < target_progress:
            current_progress += 0.05
            self.progress_bar.set(min(current_progress, target_progress))
            self.after(16)
            
        if bits < 28: nivel, color = "CRÍTICO - Muy Débil ❌", COLOR_ERROR
        elif bits < 59: nivel, color = "ADVERTENCIA - Débil ⚠️", "#FF8800"
        elif bits < 127: nivel, color = "SEGURO - Fuerte ✔️", COLOR_EXITO
        else: nivel, color = "GRADO MILITAR 🚀", COLOR_SECUNDARIO

        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefijo, sufijo = sha1_hash[:5], sha1_hash[5:]
        veces_filtrada = 0
        try:
            url = f"https://api.pwnedpasswords.com/range/{prefijo}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Cortex-Suite'})
            with urllib.request.urlopen(req) as response:
                lineas = response.read().decode('utf-8').splitlines()
            for linea in lineas:
                hash_api, conteo = linea.split(':')
                if hash_api == sufijo: veces_filtrada = int(conteo); break
            estado_red = f"¡ALERTA! Filtrada {veces_filtrada} veces." if veces_filtrada > 0 else "Limpia: Sin filtraciones."
        except Exception:
            veces_filtrada = -1; estado_red = "Error de conexión."

        self.ultimo_analisis = {"pass": password, "bits": bits, "nivel": nivel, "filtrada": veces_filtrada}
        self.after(0, lambda: self.aplicar_resultados_ui(bits, nivel, color, estado_red, veces_filtrada))

    def aplicar_resultados_ui(self, bits, nivel, color, estado_red, veces_filtrada):
        self.lbl_bits.configure(text=f"Entropía: {bits:.2f} bits")
        self.lbl_status.configure(text=f"Nivel: {nivel}", text_color=color)
        self.lbl_api.configure(text=estado_red, text_color=COLOR_ERROR if veces_filtrada > 0 else COLOR_EXITO)
        self.btn_reporte.configure(state="normal", fg_color=COLOR_PRIMARIO, text_color="white")
        self.btn_analizar.configure(state="normal", text="ANALIZAR SEGURIDAD")
        threading.Thread(target=self.guardar_en_servidor_sql, args=(bits, nivel, "Sí" if veces_filtrada > 0 else "No"), daemon=True).start()

    def exportar_reporte_auditoria(self):
        if not self.ultimo_analisis: return
        ruta = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de Texto", "*.txt")])
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"REPORTE DE AUDITORÍA - CORTEX SECURITY\n\nEntropía: {self.ultimo_analisis['bits']:.2f} bits\nEvaluación: {self.ultimo_analisis['nivel']}\nFiltrada: {self.ultimo_analisis['filtrada']} veces.")
            messagebox.showinfo("Cortex Audit", "Reporte exportado.")

    def setup_tab_generador(self):
        tab = self.tabview.tab("Generador")
        self.lbl_longitud = ctk.CTkLabel(tab, text="Longitud de Contraseña: 16", font=(FUENTE_TEXTO, 13), text_color=COLOR_TEXTO)
        self.lbl_longitud.pack(pady=(15, 5))
        self.slider_longitud = ctk.CTkSlider(tab, from_=8, to=32, number_of_steps=24, button_color=COLOR_PRIMARIO, progress_color=COLOR_SECUNDARIO)
        self.slider_longitud.set(16)
        self.slider_longitud.pack(pady=5)
        self.chk_mayus = ctk.CTkCheckBox(tab, text="Incluir Mayúsculas (A-Z)", font=(FUENTE_TEXTO, 12), fg_color=COLOR_PRIMARIO, text_color=COLOR_TEXTO)
        self.chk_mayus.select()
        self.chk_mayus.pack(pady=8, anchor="w", padx=180)
        self.chk_num = ctk.CTkCheckBox(tab, text="Incluir Números (0-9)", font=(FUENTE_TEXTO, 12), fg_color=COLOR_PRIMARIO, text_color=COLOR_TEXTO)
        self.chk_num.select()
        self.chk_num.pack(pady=8, anchor="w", padx=180)
        self.chk_sym = ctk.CTkCheckBox(tab, text="Incluir Símbolos (!@#$)", font=(FUENTE_TEXTO, 12), fg_color=COLOR_PRIMARIO, text_color=COLOR_TEXTO)
        self.chk_sym.select()
        self.chk_sym.pack(pady=8, anchor="w", padx=180)
        self.btn_generar = ctk.CTkButton(tab, text="GENERAR PASSWORD", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.generar_password)
        self.btn_generar.pack(pady=20)
        self.entry_gen_resultado = ctk.CTkEntry(tab, width=380, height=40, font=(FUENTE_MONO, 13), border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A", justify="center")
        self.entry_gen_resultado.pack(pady=5)

    def generar_password(self):
        caracteres = string.ascii_lowercase
        if self.chk_mayus.get(): caracteres += string.ascii_uppercase
        if self.chk_num.get(): caracteres += string.digits
        if self.chk_sym.get(): caracteres += string.punctuation
        password = ''.join(secrets.choice(caracteres) for _ in range(int(self.slider_longitud.get())))
        self.entry_gen_resultado.delete(0, "end"); self.entry_gen_resultado.insert(0, password)

    def setup_tab_hashes(self):
        tab = self.tabview.tab("Hashes")
        lbl_info = ctk.CTkLabel(tab, text="Firma Criptográfica de Textos:", font=(FUENTE_TEXTO, 13), text_color=COLOR_TEXTO)
        lbl_info.pack(pady=15)
        self.entry_hash_input = ctk.CTkEntry(tab, placeholder_text="Texto a procesar...", font=(FUENTE_TEXTO, 13), width=420, height=35, border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A")
        self.entry_hash_input.pack(pady=5)
        self.entry_hash_input.bind("<KeyRelease>", self.calcular_hashes_dinamicos)
        self.lbl_md5 = ctk.CTkLabel(tab, text="MD5:\n--", font=(FUENTE_MONO, 11), text_color=COLOR_SECUNDARIO, justify="left")
        self.lbl_md5.pack(pady=12, anchor="w", padx=60)
        self.lbl_sha1 = ctk.CTkLabel(tab, text="SHA-1:\n--", font=(FUENTE_MONO, 11), text_color=COLOR_EXITO, justify="left")
        self.lbl_sha1.pack(pady=12, anchor="w", padx=60)
        self.lbl_sha256 = ctk.CTkLabel(tab, text="SHA-256:\n--", font=(FUENTE_MONO, 11), text_color="#00D4FF", justify="left")
        self.lbl_sha256.pack(pady=12, anchor="w", padx=60)

    def calcular_hashes_dinamicos(self, event):
        texto = self.entry_hash_input.get()
        if not texto: return
        self.lbl_md5.configure(text=f"MD5:\n{hashlib.md5(texto.encode()).hexdigest()}")
        self.lbl_sha1.configure(text=f"SHA-1:\n{hashlib.sha1(texto.encode()).hexdigest()}")
        self.lbl_sha256.configure(text=f"SHA-256:\n{hashlib.sha256(texto.encode()).hexdigest()}")

    # =========================================================================
    # PESTAÑA FILTROS (TODAS LAS HERRAMIENTAS TÁCTICAS)
    # =========================================================================
    def setup_tab_filtros_nuevos(self):
        tab = self.tabview.tab("Filtros")
        sub_tabview = ctk.CTkTabview(tab, width=540, height=480, fg_color="#1A1A1A", segmented_button_selected_color=COLOR_PRIMARIO)
        sub_tabview.pack(padx=10, pady=5)
        
        sub_tabview.add("Phishing")
        sub_tabview.add("Forense")
        sub_tabview.add("Bruta")
        sub_tabview.add("Puertos")
        sub_tabview.add("Subdominios")
        sub_tabview.add("Bóveda")
        sub_tabview.add("Procesos")
        
        # --- 1. PHISHING ---
        t1 = sub_tabview.tab("Phishing")
        self.entry_url = ctk.CTkEntry(t1, placeholder_text="Pegar enlace sospechoso...", font=(FUENTE_TEXTO, 13), width=360, border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A")
        self.entry_url.pack(pady=10)
        f_btn = ctk.CTkFrame(t1, fg_color="transparent")
        f_btn.pack()
        b1 = ctk.CTkButton(f_btn, text="ESCANEAR URL", font=(FUENTE_TEXTO, 11, "bold"), width=130, fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.analizar_phishing_url)
        b1.pack(side="left", padx=5)
        b2 = ctk.CTkButton(f_btn, text="REPORTAR", font=(FUENTE_TEXTO, 11, "bold"), width=130, fg_color="#2A2A2A", border_color=COLOR_PRIMARIO, border_width=1, text_color=COLOR_PRIMARIO, hover_color=COLOR_PRIMARIO, command=self.reportar_url_phishing_cloud)
        b2.pack(side="left", padx=5)
        self.txt_res_url = ctk.CTkTextbox(t1, width=440, height=180, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_url.pack(pady=10)
        
        # --- 2. FORENSE ---
        t2 = sub_tabview.tab("Forense")
        b3 = ctk.CTkButton(t2, text="SELECCIONAR ARCHIVO", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.analizar_integridad_archivo)
        b3.pack(pady=15)
        self.txt_res_file = ctk.CTkTextbox(t2, width=440, height=200, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_file.pack(pady=5)
        
        # --- 3. BRUTA ---
        t3 = sub_tabview.tab("Bruta")
        self.entry_brute_pass = ctk.CTkEntry(t3, placeholder_text="Contraseña objetivo (max 5 chars)", font=(FUENTE_TEXTO, 13), width=300, border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A")
        self.entry_brute_pass.pack(pady=15)
        self.btn_brute = ctk.CTkButton(t3, text="EJECUTAR SIMULACIÓN", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.alternar_fuerza_bruta)
        self.btn_brute.pack(pady=5)
        self.txt_res_brute = ctk.CTkTextbox(t3, width=440, height=160, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_brute.pack(pady=15)

        # --- 4. PUERTOS ---
        t4 = sub_tabview.tab("Puertos")
        self.entry_port_ip = ctk.CTkEntry(t4, placeholder_text="IP o Dominio (ej: 127.0.0.1)", font=(FUENTE_TEXTO, 13), width=300, border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A")
        self.entry_port_ip.pack(pady=10)
        self.btn_ports = ctk.CTkButton(t4, text="INICIAR NETWORK SCAN", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.alternar_escaneo_puertos)
        self.btn_ports.pack(pady=5)
        self.txt_res_ports = ctk.CTkTextbox(t4, width=440, height=180, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_ports.pack(pady=10)

        # --- 5. SUBDOMINIOS ---
        t5 = sub_tabview.tab("Subdominios")
        self.entry_sub_domain = ctk.CTkEntry(t5, placeholder_text="Dominio raíz (ej: google.com)", font=(FUENTE_TEXTO, 13), width=300, border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A")
        self.entry_sub_domain.pack(pady=10)
        self.btn_subs = ctk.CTkButton(t5, text="RECON SUBDOMAINS", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.alternar_recon_subdominios)
        self.btn_subs.pack(pady=5)
        self.txt_res_subs = ctk.CTkTextbox(t5, width=440, height=180, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_subs.pack(pady=10)

        # --- 6. BÓVEDA ---
        t6 = sub_tabview.tab("Bóveda")
        self.entry_vault_pass = ctk.CTkEntry(t6, placeholder_text="Llave Maestra de Bóveda", font=(FUENTE_TEXTO, 13), show="*", width=340, border_color=COLOR_SECUNDARIO, fg_color="#2A2A2A")
        self.entry_vault_pass.pack(pady=10)
        f_btn_vault = ctk.CTkFrame(t6, fg_color="transparent")
        f_btn_vault.pack()
        b_read = ctk.CTkButton(f_btn_vault, text="LEER BÓVEDA", font=(FUENTE_TEXTO, 11, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.leer_vault_local)
        b_read.pack(side="left", padx=5)
        b_write = ctk.CTkButton(f_btn_vault, text="GUARDAR GENERADA", font=(FUENTE_TEXTO, 11, "bold"), fg_color="#2A2A2A", border_color=COLOR_PRIMARIO, border_width=1, text_color=COLOR_PRIMARIO, hover_color=COLOR_PRIMARIO, command=self.guardar_en_vault_local)
        b_write.pack(side="left", padx=5)
        self.txt_res_vault = ctk.CTkTextbox(t6, width=440, height=180, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_vault.pack(pady=10)

        # --- 7. PROCESOS ---
        t7 = sub_tabview.tab("Procesos")
        b_proc = ctk.CTkButton(t7, text="MAPEAR PROCESOS ACTIVOS", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.listar_procesos_forenses)
        b_proc.pack(pady=15)
        self.txt_res_proc = ctk.CTkTextbox(t7, width=440, height=200, font=(FUENTE_MONO, 11), fg_color="#1C1C1C")
        self.txt_res_proc.pack(pady=5)

    # --- Lógicas de Filtros ---
    def analizar_phishing_url(self):
        url = self.entry_url.get().strip()
        if not url: return
        self.txt_res_url.delete("1.0", "end")
        self.txt_res_url.insert("end", ">>> Consultando Blacklist Cloud...\n")
        threading.Thread(target=self._consultar_phishing_servidor, args=(url,), daemon=True).start()

    def _consultar_phishing_servidor(self, url):
        alertas = []
        if not url.startswith("https://"): alertas.append("[-] HEURÍSTICA: HTTP Inseguro.")
        if "@" in url: alertas.append("[-] HEURÍSTICA: Máscara '@' detectada.")
        url_consulta = f"{self.URL_PHISHING}?url_maliciosa=eq.{urllib.parse.quote(url)}"
        req = urllib.request.Request(url_consulta, method="GET")
        req.add_header("apikey", self.SUPABASE_KEY); req.add_header("Authorization", f"Bearer {self.SUPABASE_KEY}")
        es_cloud = False
        try:
            with urllib.request.urlopen(req) as r:
                if json.loads(r.read().decode('utf-8')): es_cloud = True
        except: pass
        self.after(0, lambda: self._mostrar_resultado_phishing(alertas, es_cloud))

    def _mostrar_resultado_phishing(self, alertas, es_cloud):
        self.txt_res_url.delete("1.0", "end")
        if es_cloud: self.txt_res_url.insert("end", "🚨 CRÍTICO: DETECTADO EN BLACKLIST CLOUD 🚨\n\n")
        if alertas: self.txt_res_url.insert("end", "\n".join(alertas))
        elif not es_cloud: self.txt_res_url.insert("end", ">>> Estructura Limpia.")

    def reportar_url_phishing_cloud(self):
        url = self.entry_url.get().strip()
        if not url: return
        data = json.dumps({"url_maliciosa": url, "tipo_fraude": "Phishing Confirmado"}).encode('utf-8')
        req = urllib.request.Request(self.URL_PHISHING, data=data, method="POST")
        req.add_header("apikey", self.SUPABASE_KEY); req.add_header("Authorization", f"Bearer {self.SUPABASE_KEY}"); req.add_header("Content-Type", "application/json"); req.add_header("Prefer", "return=representation")
        def env():
            try:
                with urllib.request.urlopen(req) as r: r.read()
                self.after(0, lambda: messagebox.showinfo("Intel", "Reportado con éxito."))
            except: self.after(0, lambda: messagebox.showerror("Error", "Error de red."))
        threading.Thread(target=env, daemon=True).start()

    def analizar_integridad_archivo(self):
        ruta = filedialog.askopenfilename()
        if not ruta: return
        self.txt_res_file.delete("1.0", "end")
        def h():
            sha = hashlib.sha256()
            try:
                with open(ruta, "rb") as f:
                    for b in iter(lambda: f.read(65536), b""): sha.update(b)
                sha256_hash = sha.hexdigest().upper()
                r = f"Objeto: {os.path.basename(ruta)}\nSHA-256:\n{sha256_hash}"
                self.after(0, lambda: [self.txt_res_file.delete("1.0", "end"), self.txt_res_file.insert("end", r)])
                threading.Thread(target=self.guardar_en_servidor_sql, args=(f"File: {os.path.basename(ruta)}", f"INTEGRIDAD: {sha256_hash[:16]}...", "No"), daemon=True).start()
            except: pass
        threading.Thread(target=h, daemon=True).start()

    def alternar_fuerza_bruta(self):
        if self.forzando_bruta: self.forzando_bruta = False; return
        t = self.entry_brute_pass.get()
        if len(t) > 5: messagebox.showwarning("Límite", "Máximo 5 caracteres."); return
        self.forzando_bruta = True
        self.txt_res_brute.delete("1.0", "end")
        threading.Thread(target=self._crack, args=(t,), daemon=True).start()

    def _crack(self, target):
        a = string.ascii_lowercase + string.digits; i = 0
        for l in range(1, 6):
            if not self.forzando_bruta: break
            from itertools import product
            for c in product(a, repeat=l):
                if not self.forzando_bruta: break
                i += 1; w = "".join(c)
                if i % 80000 == 0:
                    self.after(0, lambda p=w: [self.txt_res_brute.delete("1.0", "end"), self.txt_res_brute.insert("end", f"Probando: {p}")])
                if w == target:
                    self.forzando_bruta = False
                    self.after(0, lambda: [self.txt_res_brute.delete("1.0", "end"), self.txt_res_brute.insert("end", f"[+] Descifrada: {w}\nIntentos: {i}")])
                    return

    # --- Lógicas Avanzadas ---
    def alternar_escaneo_puertos(self):
        if self.escaneando_puertos:
            self.escaneando_puertos = False
            self.btn_ports.configure(text="INICIAR NETWORK SCAN", fg_color=COLOR_PRIMARIO)
            return
        ip = self.entry_port_ip.get().strip()
        if not ip: return
        self.escaneando_puertos = True
        self.btn_ports.configure(text="DETENER", fg_color=COLOR_ERROR)
        self.txt_res_ports.delete("1.0", "end")
        self.txt_res_ports.insert("end", f">>> Mapeando puertos en {ip}...\n")
        threading.Thread(target=self._scan_puertos_subhilo, args=(ip,), daemon=True).start()

    def _scan_puertos_subhilo(self, ip):
        puertos_comunes = [22, 80, 443, 445, 3306, 3389]
        abiertos = []
        for puerto in puertos_comunes:
            if not self.escaneando_puertos: break
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((ip, puerto)) == 0:
                    abiertos.append(str(puerto))
                    self.after(0, lambda p=puerto: self.txt_res_ports.insert("end", f"[+] Puerto Abierto: {p}\n"))
                s.close()
            except: pass
        self.escaneando_puertos = False
        res_str = f"Abiertos: {','.join(abiertos)}" if abiertos else "Todo Cerrado"
        threading.Thread(target=self.guardar_en_servidor_sql, args=(f"IP: {ip}", f"NETWORK SCAN: {res_str}", "No"), daemon=True).start()
        self.after(0, lambda: [self.btn_ports.configure(text="INICIAR NETWORK SCAN", fg_color=COLOR_PRIMARIO), self.txt_res_ports.insert("end", "\n>>> Escaneo enviado a la nube.")])

    def alternar_recon_subdominios(self):
        if self.escaneando_subdominios: self.escaneando_subdominios = False; return
        dom = self.entry_sub_domain.get().strip()
        if not dom: return
        self.escaneando_subdominios = True
        self.txt_res_subs.delete("1.0", "end")
        self.txt_res_subs.insert("end", f">>> Reconociendo DNS en {dom}...\n")
        threading.Thread(target=self._recon_subdominios_subhilo, args=(dom,), daemon=True).start()

    def _recon_subdominios_subhilo(self, dominio):
        subs_comunes = ["www", "mail", "dev", "admin", "api", "campus"]
        encontrados = 0
        for sub in subs_comunes:
            if not self.escaneando_subdominios: break
            objetivo = f"{sub}.{dominio}"
            try:
                socket.gethostbyname(objetivo)
                encontrados += 1
                self.after(0, lambda o=objetivo: self.txt_res_subs.insert("end", f"[+] Encontrado: {o}\n"))
            except socket.gaierror: pass
        self.escaneando_subdominios = False
        threading.Thread(target=self.guardar_en_servidor_sql, args=(f"Target: {dominio}", f"DNS RECON: {encontrados} subdominios.", "No"), daemon=True).start()
        self.after(0, lambda: self.txt_res_subs.insert("end", "\n>>> Mapeo DNS guardado en la nube."))

    def _XOR_cipher(self, texto, llave):
        return "".join(chr(ord(c) ^ ord(llave[i % len(llave)])) for i, c in enumerate(texto))

    def leer_vault_local(self):
        llave = self.entry_vault_pass.get()
        if not llave: return
        self.txt_res_vault.delete("1.0", "end")
        if not os.path.exists(self.VAULT_FILE): return
        try:
            with open(self.VAULT_FILE, "r", encoding="utf-8") as f: data_cifrada = f.read()
            self.txt_res_vault.insert("end", f"--- CREDENCIALES DESCIFRADAS ---\n\n{self._XOR_cipher(data_cifrada, llave)}")
        except: pass

    def guardar_en_vault_local(self):
        llave = self.entry_vault_pass.get()
        pass_gen = self.entry_gen_resultado.get()
        if not llave or not pass_gen: return
        texto_a_guardar = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Password: {pass_gen}\n"
        with open(self.VAULT_FILE, "w", encoding="utf-8") as f: f.write(self._XOR_cipher(texto_a_guardar, llave))
        messagebox.showinfo("Vault", "Cifrado guardado de forma local.")

    def listar_procesos_forenses(self):
        self.txt_res_proc.delete("1.0", "end")
        self.txt_res_proc.insert("end", ">>> Volcando procesos activos...\n\n")
        try:
            if sys.platform == "win32":
                cmd = "tasklist /fo csv /nh"
                resultado = subprocess.check_output(cmd, shell=True).decode('cp1252')
                lineas = [l for l in resultado.strip().split("\n") if l]
                for linea in lineas[:15]:
                    partes = linea.replace('"', '').split(",")
                    self.txt_res_proc.insert("end", f"[PID: {partes[1]}] {partes[0]} | RAM: {partes[4]}\n")
                threading.Thread(target=self.guardar_en_servidor_sql, args=(f"Host: Local PC", f"FORENSE: {len(lineas)} procesos.", "No"), daemon=True).start()
                self.txt_res_proc.insert("end", "\n>>> Tabla registrada en la nube.")
            else:
                self.txt_res_proc.insert("end", "[!] Solo disponible en Windows.\n")
        except Exception as e:
            self.txt_res_proc.insert("end", f"[-] Error: {e}\n")

    # =========================================================================
    # INFRAESTRUCTURA DE TELEMETRÍA EN LA NUBE
    # =========================================================================
    def setup_tab_historial(self):
        tab = self.tabview.tab("Historial")
        self.txt_historial = ctk.CTkTextbox(tab, width=540, height=380, font=(FUENTE_MONO, 11), border_width=1, border_color="#2B2B2B", fg_color="#1C1C1C")
        self.txt_historial.pack(pady=15)
        self.btn_refresh = ctk.CTkButton(tab, text="ACTUALIZAR", font=(FUENTE_TEXTO, 12, "bold"), fg_color=COLOR_PRIMARIO, text_color="white", hover_color="#004080", command=self.iniciar_carga_historial)
        self.btn_refresh.pack(pady=5)
        self.iniciar_carga_historial()

    def iniciar_carga_historial(self):
        threading.Thread(target=self.cargar_historial_desde_servidor, daemon=True).start()

    def guardar_en_servidor_sql(self, entropia, nivel, filtrada):
        payload = {"entropia": str(entropia), "nivel": nivel, "filtrada": filtrada}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.URL_HISTORIAL, data=data, method="POST")
        req.add_header("apikey", self.SUPABASE_KEY); req.add_header("Authorization", f"Bearer {self.SUPABASE_KEY}"); req.add_header("Content-Type", "application/json"); req.add_header("Prefer", "return=minimal")
        try:
            with urllib.request.urlopen(req) as r: r.read()
            self.iniciar_carga_historial()
        except: pass

    def cargar_historial_desde_servidor(self):
        self.txt_historial.configure(state="normal")
        self.txt_historial.delete("1.0", "end")
        self.txt_historial.insert("end", ">>> Sincronizando...\n")
        req = urllib.request.Request(f"{self.URL_HISTORIAL}?order=id.desc", method="GET")
        req.add_header("apikey", self.SUPABASE_KEY); req.add_header("Authorization", f"Bearer {self.SUPABASE_KEY}")
        try:
            with urllib.request.urlopen(req) as r: registros = json.loads(r.read().decode('utf-8'))
            self.txt_historial.delete("1.0", "end")
            for reg in registros:
                f_limpia = reg['fecha'].replace("T", " ").split(".")[0]
                self.txt_historial.insert("end", f"[{f_limpia}] {reg['entropia']} | {reg['nivel']}\n")
        except:
            self.txt_historial.delete("1.0", "end"); self.txt_historial.insert("end", "[-] Error de red.\n")
        self.txt_historial.configure(state="disabled")

if __name__ == "__main__":
    app = CortexSecuritySuite()
    app.mainloop()