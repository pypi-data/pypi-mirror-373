import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
from PIL import Image, ImageTk
import threading
import os
import sys
import time
import subprocess
import importlib.util
import torch
import yaml

class TerminalCapture:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.last_line = "Terminal listo"
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.capture_stdout()
    
    def capture_stdout(self):
        sys.stdout = self
        sys.stderr = self
    
    def write(self, text):
        self.original_stdout.write(text)
        if text.strip():
            self.last_line = text.strip()
            # Agregar texto al widget de terminal con saltos de línea
            self.text_widget.insert(tk.END, text)
            self.text_widget.see(tk.END)  # Auto-scroll
            # Forzar actualización para mostrar saltos de línea
            self.text_widget.update_idletasks()
    
    def flush(self):
        self.original_stdout.flush()
    
    def get_last_line(self):
        return self.last_line

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación de Procesamiento de Video")
        self.root.geometry("1400x800")
        
        # Cargar el tema Forest-dark desde el archivo .tcl
        self.setup_theme()
        
        # Detectar dispositivo (GPU/CPU)
        self.device_info = self.get_device_info()
        
        # Variables
        self.video_path = None
        self.sam2_chkpt_path = None
        self.processing_thread = None
        
        # Cargar configuración si existe
        self.config_data = self.load_config()
        
        # Crear frames principales
        self.create_widgets()
        
    def setup_theme(self):
        """Configura el tema Forest-dark desde el archivo .tcl"""
        try:
            # Asegúrate de que el archivo forest-dark.tcl esté en el mismo directorio
            tcl_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'forest-dark.tcl')
            if os.path.exists(tcl_file):
                # Importar el archivo tcl
                self.root.tk.call('source', tcl_file)
                # Configurar el tema
                style = ttk.Style()
                style.theme_use('forest-dark')
                print("✅ Tema Forest-dark cargado correctamente")
            else:
                print("⚠️  Archivo forest-dark.tcl no encontrado. Usando tema por defecto.")
                # Configurar colores manualmente como fallback
                self.root.configure(bg='#2c3e50')
        except Exception as e:
            print(f"❌ Error al cargar el tema: {e}")
            # Fallback a colores manuales
            self.root.configure(bg='#2c3e50')
    
    def load_config(self):
        """Carga la configuración desde config.yaml si existe"""
        config_path = "config.yaml"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                print(f"✅ Configuración cargada desde {config_path}")
                return config
            except Exception as e:
                print(f"❌ Error al cargar configuración: {e}")
                return {}
        else:
            print("ℹ️ No se encontró archivo config.yaml")
            return {}
    
    def get_device_info(self):
        """Obtiene información del dispositivo (GPU/CPU)"""
        try:
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
                return f"GPU: {gpu_name} ({gpu_memory:.1f} GB)"
            else:
                return "CPU: No hay GPU disponible"
        except:
            return "CPU: Torch no disponible"
    
    def create_widgets(self):
        # Frame principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame izquierdo (menú principal)
        left_frame = ttk.Frame(main_container, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Frame derecho (dividido en terminal y controles)
        right_container = ttk.Frame(main_container)
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Frame superior derecho (controles adicionales)
        controls_frame = ttk.Frame(right_container, height=270)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Frame inferior derecho (terminal)
        terminal_frame = ttk.Frame(right_container)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contenido del frame izquierdo (menú principal)
        self.create_left_panel(left_frame)
        
        # Contenido del frame superior derecho (controles adicionales)
        self.create_controls_panel(controls_frame)
        
        # Terminal con scroll (mantenemos tk.Text para la terminal)
        terminal_label = ttk.Label(terminal_frame, text="TERMINAL DE EJECUCIÓN", 
                                  font=('Arial', 12, 'bold'))
        terminal_label.pack(pady=(0, 5))
        
        # Widget de texto para la terminal con scroll
        self.terminal_text = scrolledtext.ScrolledText(
            terminal_frame, 
            bg='#1e272e', 
            fg='#00ff00', 
            font=('Consolas', 10),
            wrap=tk.WORD,
            height=12,
            relief=tk.SUNKEN,
            bd=2
        )
        self.terminal_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar captura de terminal
        self.terminal_capture = TerminalCapture(self.terminal_text)
        
    def create_left_panel(self, parent):
        # Título
        title_label = ttk.Label(parent, text="PROCESAMIENTO DE VIDEO", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Información del dispositivo (frame normal)
        device_frame = ttk.Frame(parent)
        device_frame.pack(fill=tk.X, padx=10, pady=10)
        
        device_label = ttk.Label(device_frame, text=self.device_info, 
                                font=('Arial', 10, 'bold'))
        device_label.pack(fill=tk.X)
        
        print(f"Información del dispositivo: {self.device_info}")
        
        # Separador
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        
        # Opciones seleccionables
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        options = [
            "first_step",
            "second_step", 
            "third_step",
            "fourth_step",
            "fifth_step",
            "sixth_step"
        ]
        self.selected_option = tk.StringVar(value=options[0])
        
        for option in options:
            rb = ttk.Radiobutton(options_frame, text=f"{option.replace('_', ' ').title()}", 
                                variable=self.selected_option, 
                                value=option, command=self.on_option_selected)
            rb.pack(anchor='w', pady=5)
        
        # Separador
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=10, pady=20)
        
        # Botón de ejecutar proceso
        self.execute_btn = ttk.Button(parent, text="Ejecutar Proceso", 
                                     command=self.execute_process, 
                                     state=tk.DISABLED)
        self.execute_btn.pack(pady=20)
        
        # Botón para limpiar terminal
        clear_btn = ttk.Button(parent, text="Limpiar Terminal", 
                              command=self.clear_terminal)
        clear_btn.pack(pady=5)
        
        # Separador
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, padx=10, pady=20)
        
        # Etiquetas informativas
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_labels = [
            "Estado: Inactivo",
            "Proceso seleccionado: First Step"
        ]
        
        self.status_labels = {}
        for i, text in enumerate(info_labels):
            label = ttk.Label(info_frame, text=text, anchor='w')
            label.pack(fill=tk.X, pady=2)
            self.status_labels[f"label_{i}"] = label
    
    def create_controls_panel(self, parent):
        """Crea el panel de controles en la parte superior derecha"""
        # Título del panel de controles
        title_label = ttk.Label(parent, text="CONFIGURACIÓN", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Frame para controles en grid
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Buscador de video
        ttk.Label(grid_frame, text="Video:", 
                 font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=5)
        
        video_entry_frame = ttk.Frame(grid_frame)
        video_entry_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        self.video_search_var = tk.StringVar()
        # Cargar valor desde config si existe
        video_path = self.config_data.get('root', '')
        if video_path and os.path.exists(video_path):
            self.video_path = video_path
            self.video_search_var.set(os.path.basename(video_path))
        
        video_search_entry = ttk.Entry(video_entry_frame, 
                                      textvariable=self.video_search_var, 
                                      state='readonly', width=30)
        video_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        video_browse_btn = ttk.Button(video_entry_frame, text="...", 
                                     command=self.browse_video, width=3)
        video_browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buscador de checkpoint SAM2
        ttk.Label(grid_frame, text="Checkpoint SAM2:", 
                 font=('Arial', 11)).grid(row=1, column=0, sticky='w', pady=5)
        
        sam_entry_frame = ttk.Frame(grid_frame)
        sam_entry_frame.grid(row=1, column=1, sticky='ew', pady=5, padx=(5, 0))
        
        self.sam_search_var = tk.StringVar()
        # Cargar valor desde config si existe
        sam_chkpt = self.config_data.get('sam2_chkpt', '')
        if sam_chkpt and os.path.exists(sam_chkpt):
            self.sam2_chkpt_path = sam_chkpt
            self.sam_search_var.set(os.path.basename(sam_chkpt))
        
        sam_search_entry = ttk.Entry(sam_entry_frame, 
                                    textvariable=self.sam_search_var, 
                                    state='readonly', width=30)
        sam_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        sam_browse_btn = ttk.Button(sam_entry_frame, text="...", 
                                   command=self.browse_sam_checkpoint, width=3)
        sam_browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Parámetros en grid con valores por defecto desde config
        params = [
            ("Factor:", "fac_var", "fac", "1"),
            ("Nº Imágenes:", "n_imgs_var", "n_imgs", "100"),
            ("Nº Objetos:", "n_obj_var", "n_obj", "20"),
        ]
        
        for i, (label_text, var_name, config_key, default_value) in enumerate(params, 2):
            ttk.Label(grid_frame, text=label_text, 
                     font=('Arial', 11)).grid(row=i, column=0, sticky='w', pady=5)
            
            # Obtener valor de config o usar valor por defecto
            config_value = self.config_data.get(config_key, default_value)
            var = tk.StringVar(value=str(config_value))
            setattr(self, var_name, var)
            
            entry = ttk.Entry(grid_frame, textvariable=var, width=10)
            entry.grid(row=i, column=1, sticky='w', pady=5, padx=(5, 0))
        
        # Información de archivos seleccionados
        file_info_frame = ttk.Frame(grid_frame)
        file_info_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Habilitar botón si hay video cargado desde config
        if self.video_path:
            self.execute_btn.configure(state=tk.NORMAL)
        
        # Configurar peso de columnas
        grid_frame.columnconfigure(1, weight=1)
    
    def clear_terminal(self):
        """Limpia el contenido de la terminal"""
        self.terminal_text.delete(1.0, tk.END)
        print("Terminal limpiada\n")
    
    def browse_video(self):
        """Abre diálogo para seleccionar video"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            self.video_search_var.set(os.path.basename(file_path))
            self.update_status_labels()
            self.file_labels["file_label_0"].configure(
                text=f"Video seleccionado: {os.path.basename(file_path)}"
            )
            print(f"Video seleccionado: {os.path.basename(file_path)}\n")
            
            # Habilitar botón de ejecutar si hay video
            if self.video_path:
                self.execute_btn.configure(state=tk.NORMAL)
    
    def browse_sam_checkpoint(self):
        """Abre diálogo para seleccionar checkpoint de SAM2"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar checkpoint de SAM2",
            filetypes=[
                ("Checkpoint files", "*.pth *.pt *.ckpt *.safetensors"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.sam2_chkpt_path = file_path
            self.sam_search_var.set(os.path.basename(file_path))
            self.file_labels["file_label_1"].configure(
                text=f"Checkpoint SAM2: {os.path.basename(file_path)}"
            )
            print(f"Checkpoint SAM2 seleccionado: {os.path.basename(file_path)}\n")
    
    def on_option_selected(self):
        """Se llama cuando se selecciona una opción diferente"""
        option = self.selected_option.get()
        process_name = option.replace('_', ' ').title()
        self.status_labels["label_1"].configure(text=f"Proceso seleccionado: {process_name}")
        
        # Habilitar botón si hay video seleccionado
        if self.video_path:
            self.execute_btn.configure(state=tk.NORMAL)
    
    def update_status_labels(self):
        status_text = "Inactivo"
        option_text = f"Proceso seleccionado: {self.selected_option.get().replace('_', ' ').title()}"
        
        self.status_labels["label_0"].configure(text=f"Estado: {status_text}")
        self.status_labels["label_1"].configure(text=option_text)
    
    def execute_process(self):
        """Ejecuta el proceso seleccionado"""
        if not self.video_path:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un video primero.")
            return
        
        if self.processing_thread and self.processing_thread.is_alive():
            messagebox.showwarning("Advertencia", "Ya hay un proceso en ejecución.")
            return
        
        # Ejecutar en un hilo separado
        self.processing_thread = threading.Thread(target=self.run_selected_process, daemon=True)
        self.processing_thread.start()
    
    def run_selected_process(self):
        """Ejecuta el proceso seleccionado usando uv run"""
        try:
            step = self.selected_option.get()
            print(f"Iniciando proceso: {step}\n")
            print(f"Dispositivo: {self.device_info}\n")
            self.status_labels["label_0"].configure(text="Estado: Procesando...")
            
            # Construir el comando base con uv run
            cmd = [
                "uv", "run", "python", "-m", f"segmentedcreator.{step}",
                "--root", self.video_path,
                "--fac", self.fac_var.get(),
                "--n_imgs", self.n_imgs_var.get(),
                "--n_obj", self.n_obj_var.get(),
            ]
            
            # Agregar checkpoint SAM2 si está disponible y es relevante
            if self.sam2_chkpt_path and step in ["second_step", "third_step"]:
                cmd.extend(["--sam2_chkpt", self.sam2_chkpt_path])
                print(f"Usando checkpoint: {os.path.basename(self.sam2_chkpt_path)}\n")
            
            print(f"Ejecutando: {' '.join(cmd)}\n")
            
            # Ejecutar el proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # Capturar output en tiempo real
            for line in process.stdout:
                if line.strip():
                    print(line.strip())
                    # Forzar actualización de la interfaz
                    self.root.update_idletasks()
            
            # Esperar a que termine el proceso
            process.wait()
            
            # Verificar el código de retorno
            if process.returncode == 0:
                print("✅ Proceso completado exitosamente!\n")
                self.status_labels["label_0"].configure(text="Estado: Completado")
            else:
                print(f"❌ Error en el proceso. Código: {process.returncode}\n")
                self.status_labels["label_0"].configure(text="Estado: Error")
                messagebox.showerror("Error", f"El proceso falló con código {process.returncode}")
                
        except FileNotFoundError:
            error_msg = "Error: uv no encontrado. Asegúrate de tener uv instalado.\n"
            print(error_msg)
            self.status_labels["label_0"].configure(text="Estado: Error - uv no encontrado")
            messagebox.showerror("Error", error_msg)
            
        except Exception as e:
            error_msg = f"Error al ejecutar el proceso: {str(e)}\n"
            print(error_msg)
            self.status_labels["label_0"].configure(text="Estado: Error")
            messagebox.showerror("Error", error_msg)
    
    def on_closing(self):
        # Restaurar stdout/stderr original
        sys.stdout = self.terminal_capture.original_stdout
        sys.stderr = self.terminal_capture.original_stderr
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VideoApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()