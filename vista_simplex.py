import tkinter as tk
from tkinter import ttk, scrolledtext

class SimplexVista:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplex Solver - Modern GUI")
        # Tamaño deseado de la ventana
        ancho_ventana = 600
        alto_ventana = 650

        # Obtener tamaño de la pantalla
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()

        # Calcular coordenadas para centrar
        x = (ancho_pantalla // 2) - (ancho_ventana // 2)
        y = (alto_pantalla // 2) - (alto_ventana // 2)

        # Establecer tamaño y posición centrada
        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        # maximizar
        # self.root.state('zoomed')
        
        # Variables de la interfaz
        self.tipo_problema = tk.StringVar(value="max")
        self.entradas_coef_obj = []
        self.entradas_restricciones = []
        
        # Callbacks que serán asignados por el controlador
        self.callback_configurar_objetivo = None
        self.callback_agregar_restriccion = None
        self.callback_eliminar_restriccion = None
        self.callback_limpiar_restricciones = None
        self.callback_resolver = None
        self.callback_exportar_imagenes = None
        self.callback_update_result_tab = None
        
        self.setup_style()
        self.build_ui()
        
        # Asegurar que el foco esté en la ventana principal después de la inicialización
        self.root.after(100, self._restore_focus)
    
    def _restore_focus(self):
        """Restaura el foco a la ventana principal y permite interacción normal"""
        try:
            self.root.focus_force()
            self.root.grab_release()  # Libera cualquier grab modal
            # Dar foco al campo de número de variables
            if hasattr(self, 'num_vars_entry'):
                self.num_vars_entry.focus_set()
        except:
            pass
    
    def setup_style(self):
        """Configura el estilo de la interfaz"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configuración mejorada de botones con hover
        style.configure("TButton", 
                       padding=6, 
                       relief="flat", 
                       background="#4CAF50", 
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none")
        
        # Hover effect para botones (verde más oscuro)
        style.map("TButton",
                 background=[('active', '#45a049'),  # Verde más oscuro para hover
                            ('pressed', '#3d8b40')],   # Verde aún más oscuro para pressed
                 foreground=[('active', 'white'),
                            ('pressed', 'white')])
        
        # Estilo para botones de eliminar (rojo)
        style.configure("Delete.TButton",
                       padding=4,
                       relief="flat",
                       background="#f44336",
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none")
        
        style.map("Delete.TButton",
                 background=[('active', '#da190b'),
                            ('pressed', '#c62828')],
                 foreground=[('active', 'white'),
                            ('pressed', 'white')])
        
        # Otros estilos
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TEntry", 
                       font=("Arial", 10),
                       fieldbackground="white",
                       borderwidth=1,
                       relief="solid")
        style.configure("TLabelFrame.Label", font=("Arial", 10, "bold"))
    
    def build_ui(self):
        """Construye toda la interfaz de usuario"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_config = ttk.Frame(notebook)
        self.tab_result = ttk.Frame(notebook)

        notebook.add(self.tab_config, text="Configurar y Resultados")
        notebook.add(self.tab_result, text="Proceso de Resolución")

        self.build_config_tab()
        self.build_result_tab()

        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def build_config_tab(self):
        """Construye la pestaña de configuración"""
        f = self.tab_config

        # Marco superior para configuración
        config_frame = ttk.LabelFrame(f, text="Configuración del Problema")
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # Tipo de problema
        ttk.Label(config_frame, text="Tipo de problema    :").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tipo_menu = ttk.OptionMenu(config_frame, self.tipo_problema, "max", "max", "min")
        tipo_menu.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Número de variables
        ttk.Label(config_frame, text="Número de variables:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.num_vars_entry = ttk.Entry(config_frame, width=10)
        self.num_vars_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Añadir validación para que solo acepte números
        self.num_vars_entry.bind('<KeyRelease>', self._validate_number_input)

        # Botón para configurar función objetivo
        config_btn = ttk.Button(config_frame, text="Configurar función objetivo", 
                               command=self._configurar_objetivo)
        config_btn.grid(row=2, column=0, columnspan=2, pady=15)

        # Función objetivo
        self.area_coeficientes = ttk.LabelFrame(f, text="Función Objetivo")
        self.area_coeficientes.pack(fill=tk.X, padx=10, pady=5)

        # Restricciones
        self.area_restricciones = ttk.LabelFrame(f, text="Restricciones")
        self.area_restricciones.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Botones de acción
        botones_frame = ttk.Frame(f)
        botones_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(botones_frame, text="Agregar Restricción", 
                  command=self._agregar_restriccion).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Limpiar Restricciones", 
                  command=self._limpiar_restricciones).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Resolver", 
                  command=self._resolver).pack(side=tk.RIGHT, padx=5)

        # Área de resultados resumidos
        resultado_frame = ttk.LabelFrame(f, text="Resultados")
        resultado_frame.pack(fill=tk.X, padx=10, pady=5)

        self.text_resultado_principal = scrolledtext.ScrolledText(resultado_frame, 
                                                                wrap=tk.WORD, 
                                                                font=("Courier", 11), 
                                                                height=8,
                                                                bg="#fafafa",
                                                                relief="sunken",
                                                                borderwidth=1)
        self.text_resultado_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _validate_number_input(self, event):
        """Valida que el input del número de variables sea un número"""
        value = event.widget.get()
        if value and not value.isdigit():
            # Remover caracteres no numéricos
            cleaned = ''.join(c for c in value if c.isdigit())
            event.widget.delete(0, tk.END)
            event.widget.insert(0, cleaned)
    
    def build_result_tab(self):
        """Construye la pestaña de resultados"""
        f = self.tab_result

        # Marco para botones
        botones_frame = ttk.Frame(f)
        botones_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(botones_frame, text="Proceso detallado de resolución:", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(botones_frame, text="Exportar Proceso como Imágenes", 
                  command=self._exportar_imagenes).pack(side=tk.RIGHT)

        # Área de texto para el proceso completo
        self.text_resultado = scrolledtext.ScrolledText(f, 
                                                       wrap=tk.WORD, 
                                                       font=("Courier", 10),
                                                       bg="#f8f8f8",
                                                       relief="sunken",
                                                       borderwidth=1)
        self.text_resultado.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
    
    def crear_area_coeficientes(self, n):
        """Crea el área de coeficientes de la función objetivo"""
        # Limpiar área de coeficientes
        for widget in self.area_coeficientes.winfo_children():
            widget.destroy()

        self.entradas_coef_obj = []
        
        # Crear marco para la función objetivo
        obj_frame = ttk.Frame(self.area_coeficientes)
        obj_frame.pack(pady=10)

        ttk.Label(obj_frame, text=f"{self.tipo_problema.get().upper()}:", 
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        for i in range(n):
            if i > 0:
                ttk.Label(obj_frame, text=" + ").pack(side=tk.LEFT, padx=2)
            
            entry = ttk.Entry(obj_frame, width=8)
            entry.pack(side=tk.LEFT, padx=2)
            entry.insert(0, "0")  # Valor por defecto
            # Añadir validación para números (incluyendo negativos y decimales)
            entry.bind('<KeyRelease>', self._validate_coefficient_input)
            self.entradas_coef_obj.append(entry)
            
            ttk.Label(obj_frame, text=f"x{i+1}").pack(side=tk.LEFT, padx=2)
    
    def _validate_coefficient_input(self, event):
        """Valida que el input de coeficientes sea un número válido"""
        value = event.widget.get()
        if value and value not in ['-', '.', '-.']:
            try:
                float(value)
            except ValueError:
                # Si no es un número válido, restaurar el valor anterior
                event.widget.delete(len(value)-1)
    
    def crear_restriccion(self, n):
        """Crea una nueva restricción en la interfaz"""
        # Crear marco para la restricción
        fila = ttk.Frame(self.area_restricciones)
        fila.pack(pady=3, fill=tk.X, padx=5)

        entradas = []
        for i in range(n):
            if i > 0:
                ttk.Label(fila, text=" + ").pack(side=tk.LEFT, padx=2)
            
            e = ttk.Entry(fila, width=6)
            e.pack(side=tk.LEFT, padx=2)
            e.insert(0, "0")  # Valor por defecto
            e.bind('<KeyRelease>', self._validate_coefficient_input)
            entradas.append(e)
            
            ttk.Label(fila, text=f"x{i+1}").pack(side=tk.LEFT, padx=2)

        # Tipo de desigualdad
        desigualdad = tk.StringVar(value="<=")
        desig_menu = ttk.OptionMenu(fila, desigualdad, "<=", "<=", ">=", "=")
        desig_menu.pack(side=tk.LEFT, padx=8)

        # Lado derecho
        rhs = ttk.Entry(fila, width=8)
        rhs.pack(side=tk.LEFT, padx=5)
        rhs.insert(0, "0")  # Valor por defecto
        rhs.bind('<KeyRelease>', self._validate_coefficient_input)

        # Botón para eliminar esta restricción (con estilo rojo)
        delete_btn = ttk.Button(fila, text="Eliminar", style="Delete.TButton",
                               command=lambda: self._eliminar_restriccion_especifica(fila))
        delete_btn.pack(side=tk.RIGHT, padx=5)

        # Agregar a la lista
        restriccion_data = (entradas, desigualdad, rhs, fila)
        self.entradas_restricciones.append(restriccion_data)
        
        return restriccion_data
    
    def eliminar_restriccion_especifica(self, fila_frame):
        """Elimina una restricción específica de la interfaz"""
        # Encontrar y remover de la lista
        self.entradas_restricciones = [
            (entradas, desig, rhs, frame) for entradas, desig, rhs, frame in self.entradas_restricciones 
            if frame != fila_frame
        ]
        # Destruir el widget
        fila_frame.destroy()
    
    def limpiar_area_restricciones(self):
        """Limpia todas las restricciones de la interfaz"""
        for widget in self.area_restricciones.winfo_children():
            widget.destroy()
        self.entradas_restricciones = []
    
    def mostrar_resultado_principal(self, texto):
        """Muestra texto en el área de resultados principal"""
        self.text_resultado_principal.delete("1.0", tk.END)
        self.text_resultado_principal.insert(tk.END, texto)
    
    def mostrar_proceso_completo(self, texto):
        """Muestra texto en el área de proceso completo"""
        self.text_resultado.delete("1.0", tk.END)
        if texto:
            self.text_resultado.insert(tk.END, texto)
        else:
            self.text_resultado.insert(tk.END, 
                "Aún no se ha resuelto ningún problema.\n\n"
                "Para ver el proceso detallado:\n"
                "1. Configure el problema en la pestaña anterior\n"
                "2. Haga clic en 'Resolver'\n"
                "3. Regrese a esta pestaña para ver el proceso completo")
    
    def obtener_numero_variables(self):
        """Obtiene el número de variables del campo de entrada"""
        return self.num_vars_entry.get()
    
    def obtener_tipo_problema(self):
        """Obtiene el tipo de problema seleccionado"""
        return self.tipo_problema.get()
    
    def obtener_coeficientes_objetivo(self):
        """Obtiene los coeficientes de la función objetivo"""
        return [e.get() for e in self.entradas_coef_obj]
    
    def obtener_restricciones_data(self):
        """Obtiene todos los datos de las restricciones"""
        return self.entradas_restricciones
    
    def tiene_coeficientes_objetivo(self):
        """Verifica si hay coeficientes de objetivo configurados"""
        return len(self.entradas_coef_obj) > 0
    
    def tiene_restricciones(self):
        """Verifica si hay restricciones configuradas"""
        return len(self.entradas_restricciones) > 0
    
    # Métodos privados que conectan con los callbacks
    def _configurar_objetivo(self):
        if self.callback_configurar_objetivo:
            self.callback_configurar_objetivo()
    
    def _agregar_restriccion(self):
        if self.callback_agregar_restriccion:
            self.callback_agregar_restriccion()
    
    def _eliminar_restriccion_especifica(self, fila_frame):
        if self.callback_eliminar_restriccion:
            self.callback_eliminar_restriccion(fila_frame)
    
    def _limpiar_restricciones(self):
        if self.callback_limpiar_restricciones:
            self.callback_limpiar_restricciones()
    
    def _resolver(self):
        if self.callback_resolver:
            self.callback_resolver()
    
    def _exportar_imagenes(self):
        if self.callback_exportar_imagenes:
            self.callback_exportar_imagenes()
    
    def _on_tab_changed(self, event):
        if self.callback_update_result_tab:
            self.callback_update_result_tab(event)
    
    # Métodos para configurar callbacks
    def set_callback_configurar_objetivo(self, callback):
        self.callback_configurar_objetivo = callback
    
    def set_callback_agregar_restriccion(self, callback):
        self.callback_agregar_restriccion = callback
    
    def set_callback_eliminar_restriccion(self, callback):
        self.callback_eliminar_restriccion = callback
    
    def set_callback_limpiar_restricciones(self, callback):
        self.callback_limpiar_restricciones = callback
    
    def set_callback_resolver(self, callback):
        self.callback_resolver = callback
    
    def set_callback_exportar_imagenes(self, callback):
        self.callback_exportar_imagenes = callback
    
    def set_callback_update_result_tab(self, callback):
        self.callback_update_result_tab = callback