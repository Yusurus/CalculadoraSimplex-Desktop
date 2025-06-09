import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from fractions import Fraction
import os
import io
import sys
from contextlib import redirect_stdout
from app import SolucionadorPL, parsear_fraccion

EXPORT_PATH = "/mnt/data/exportaciones_simplex"

class SimplexAppModern:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplex Solver - Modern GUI")
        self.root.geometry("1000x800")
        self.solver = SolucionadorPL()

        self.tipo_problema = tk.StringVar(value="max")
        self.entradas_coef_obj = []
        self.entradas_restricciones = []
        self.usar_fracciones = True
        self.resultado_texto = ""
        self.proceso_completo = ""

        self.setup_style()
        self.build_ui()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))

    def build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_config = ttk.Frame(notebook)
        self.tab_result = ttk.Frame(notebook)

        notebook.add(self.tab_config, text="Configurar y Resultados")
        notebook.add(self.tab_result, text="Proceso de Resolución")

        self.build_config_tab()
        self.build_result_tab()

        notebook.bind("<<NotebookTabChanged>>", self.update_result_tab)

    def build_config_tab(self):
        f = self.tab_config

        # Marco superior para configuración
        config_frame = ttk.LabelFrame(f, text="Configuración del Problema")
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # Tipo de problema
        ttk.Label(config_frame, text="Tipo de problema:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.OptionMenu(config_frame, self.tipo_problema, "max", "max", "min").grid(row=0, column=1, padx=5, pady=2)

        # Número de variables
        ttk.Label(config_frame, text="Número de variables:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.num_vars_entry = ttk.Entry(config_frame, width=10)
        self.num_vars_entry.grid(row=1, column=1, padx=5, pady=2)

        # Botón para configurar función objetivo
        ttk.Button(config_frame, text="Configurar función objetivo", 
                  command=self.configurar_objetivo).grid(row=2, column=0, columnspan=2, pady=10)

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
                  command=self.agregar_restriccion).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Limpiar Restricciones", 
                  command=self.limpiar_restricciones).pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Resolver", 
                  command=self.resolver).pack(side=tk.RIGHT, padx=5)

        # Área de resultados resumidos
        resultado_frame = ttk.LabelFrame(f, text="Resultados")
        resultado_frame.pack(fill=tk.X, padx=10, pady=5)

        self.text_resultado_principal = scrolledtext.ScrolledText(resultado_frame, 
                                                                wrap=tk.WORD, 
                                                                font=("Courier", 11), 
                                                                height=8)
        self.text_resultado_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def build_result_tab(self):
        f = self.tab_result

        # Marco para botones
        botones_frame = ttk.Frame(f)
        botones_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(botones_frame, text="Proceso detallado de resolución:", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(botones_frame, text="Exportar Proceso como Imágenes", 
                  command=self.exportar_imagenes).pack(side=tk.RIGHT)

        # Área de texto para el proceso completo
        self.text_resultado = scrolledtext.ScrolledText(f, 
                                                       wrap=tk.WORD, 
                                                       font=("Courier", 10),
                                                       bg="#f8f8f8")
        self.text_resultado.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

    def update_result_tab(self, event):
        """Actualiza la pestaña de resultados cuando se selecciona"""
        self.text_resultado.delete("1.0", tk.END)
        if self.proceso_completo:
            self.text_resultado.insert(tk.END, self.proceso_completo)
        else:
            self.text_resultado.insert(tk.END, "Aún no se ha resuelto ningún problema.\n\nPara ver el proceso detallado:\n1. Configure el problema en la pestaña anterior\n2. Haga clic en 'Resolver'\n3. Regrese a esta pestaña para ver el proceso completo")

    def configurar_objetivo(self):
        try:
            n = int(self.num_vars_entry.get())
            if n <= 0:
                raise ValueError("El número debe ser positivo")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido de variables (entero positivo)")
            return

        # Limpiar área de coeficientes
        for widget in self.area_coeficientes.winfo_children():
            widget.destroy()

        self.entradas_coef_obj = []
        
        # Crear marco para la función objetivo
        obj_frame = ttk.Frame(self.area_coeficientes)
        obj_frame.pack(pady=5)

        ttk.Label(obj_frame, text=f"{self.tipo_problema.get().upper()}:").pack(side=tk.LEFT, padx=5)

        for i in range(n):
            if i > 0:
                ttk.Label(obj_frame, text="+").pack(side=tk.LEFT, padx=2)
            
            entry = ttk.Entry(obj_frame, width=8)
            entry.pack(side=tk.LEFT, padx=2)
            entry.insert(0, "0")  # Valor por defecto
            self.entradas_coef_obj.append(entry)
            
            ttk.Label(obj_frame, text=f"x{i+1}").pack(side=tk.LEFT, padx=2)

    def agregar_restriccion(self):
        n = len(self.entradas_coef_obj)
        if n == 0:
            messagebox.showerror("Error", "Primero configure la función objetivo")
            return

        # Crear marco para la restricción
        fila = ttk.Frame(self.area_restricciones)
        fila.pack(pady=3, fill=tk.X)

        entradas = []
        for i in range(n):
            if i > 0:
                ttk.Label(fila, text="+").pack(side=tk.LEFT, padx=2)
            
            e = ttk.Entry(fila, width=6)
            e.pack(side=tk.LEFT, padx=2)
            e.insert(0, "0")  # Valor por defecto
            entradas.append(e)
            
            ttk.Label(fila, text=f"x{i+1}").pack(side=tk.LEFT, padx=2)

        # Tipo de desigualdad
        desigualdad = tk.StringVar(value="<=")
        ttk.OptionMenu(fila, desigualdad, "<=", "<=", ">=", "=").pack(side=tk.LEFT, padx=5)

        # Lado derecho
        rhs = ttk.Entry(fila, width=8)
        rhs.pack(side=tk.LEFT, padx=5)
        rhs.insert(0, "0")  # Valor por defecto

        # Botón para eliminar esta restricción
        ttk.Button(fila, text="Eliminar", 
                  command=lambda: self.eliminar_restriccion(fila)).pack(side=tk.RIGHT, padx=5)

        self.entradas_restricciones.append((entradas, desigualdad, rhs, fila))

    def eliminar_restriccion(self, fila_frame):
        """Elimina una restricción específica"""
        # Encontrar y remover de la lista
        self.entradas_restricciones = [
            (entradas, desig, rhs, frame) for entradas, desig, rhs, frame in self.entradas_restricciones 
            if frame != fila_frame
        ]
        # Destruir el widget
        fila_frame.destroy()

    def limpiar_restricciones(self):
        """Limpia todas las restricciones"""
        for widget in self.area_restricciones.winfo_children():
            widget.destroy()
        self.entradas_restricciones = []

    def capturar_salida_solver(self):
        """Captura toda la salida del solver incluyendo tableaux y comentarios"""
        # Crear un buffer para capturar la salida
        salida_buffer = io.StringIO()
        
        # Redirigir stdout al buffer
        with redirect_stdout(salida_buffer):
            try:
                # Resolver el problema (esto generará toda la salida)
                solucion, valor = self.solver.resolver()
                
                # Agregar información adicional al final
                print("\n" + "="*60)
                print("ANÁLISIS DE LA SOLUCIÓN")
                print("="*60)
                
                # Verificar si hay variables artificiales en la solución
                tiene_artificiales = False
                for i, var in enumerate(self.solver.vars_basicas):
                    if var in self.solver.indices_artificiales and abs(self.solver.tableau[i, -1]) > self.solver.epsilon:
                        tiene_artificiales = True
                        break
                
                if tiene_artificiales:
                    print("⚠️  PROBLEMA INFACTIBLE:")
                    print("   Una o más variables artificiales permanecen en la solución final")
                    print("   con valores no cero, lo que indica que no existe solución factible.")
                else:
                    print("✅ PROBLEMA FACTIBLE:")
                    print("   Se encontró una solución óptima válida.")
                
                print(f"\n📊 ESTADÍSTICAS DEL PROCESO:")
                print(f"   • Número de iteraciones: {len(self.solver.historial_tableaux) - 1}")
                print(f"   • Variables originales: {self.solver.num_variables}")
                print(f"   • Restricciones: {self.solver.num_restricciones}")
                print(f"   • Variables de holgura: {len(self.solver.vars_holgura)}")
                print(f"   • Variables artificiales: {len(self.solver.vars_artificiales_idx)}")
                
                if self.solver.M:
                    print(f"   • Valor Big M utilizado: {self.solver.M}")
                
                print(f"\n🎯 SOLUCIÓN FINAL:")
                for i, val in enumerate(solucion):
                    if abs(val) > self.solver.epsilon:  # Solo mostrar variables no cero
                        if self.usar_fracciones:
                            frac = Fraction(val).limit_denominator()
                            print(f"   x{i+1} = {frac}")
                        else:
                            print(f"   x{i+1} = {val:.6f}")
                
                tipo_original = "minimización" if self.solver.tipo_problema == "min" else "maximización"
                if self.usar_fracciones:
                    obj_frac = Fraction(valor).limit_denominator()
                    print(f"\n🏆 Valor óptimo de {tipo_original}: {obj_frac}")
                else:
                    print(f"\n🏆 Valor óptimo de {tipo_original}: {valor:.6f}")
                    
            except Exception as e:
                print(f"❌ ERROR DURANTE LA RESOLUCIÓN: {str(e)}")
                solucion, valor = None, None
        
        # Obtener el contenido capturado
        salida_completa = salida_buffer.getvalue()
        salida_buffer.close()
        
        return salida_completa, solucion, valor

    def resolver(self):
        try:
            # Validar entrada
            if not self.entradas_coef_obj:
                messagebox.showerror("Error", "Configure primero la función objetivo")
                return
            
            if not self.entradas_restricciones:
                messagebox.showerror("Error", "Agregue al menos una restricción")
                return

            # Obtener datos del problema
            tipo = self.tipo_problema.get()
            try:
                coef = [parsear_fraccion(e.get()) for e in self.entradas_coef_obj]
            except ValueError:
                messagebox.showerror("Error", "Coeficientes de función objetivo inválidos")
                return

            # Crear nuevo solver
            self.solver = SolucionadorPL()
            self.solver.usar_fracciones = self.usar_fracciones
            self.solver.verbose = True  # Asegurar que muestre información detallada
            self.solver.establecer_objetivo(coef, tipo)

            A, b, d = [], [], []

            try:
                for entradas, desig_var, rhs_entry, _ in self.entradas_restricciones:
                    fila = [parsear_fraccion(e.get()) for e in entradas]
                    lado_derecho = parsear_fraccion(rhs_entry.get())
                    A.append(fila)
                    b.append(lado_derecho)
                    d.append(desig_var.get())
            except ValueError:
                messagebox.showerror("Error", "Valores de restricciones inválidos")
                return

            self.solver.agregar_restricciones(A, b, d)

            # Capturar todo el proceso de resolución
            proceso_completo, solucion, valor = self.capturar_salida_solver()
            
            if solucion is not None and valor is not None:
                # Guardar proceso completo para la pestaña de resultados
                self.proceso_completo = proceso_completo
                
                # Mostrar solo el resumen en la pestaña principal
                resultado_resumen = "🎯 RESUMEN DE LA SOLUCIÓN\n"
                resultado_resumen += "="*50 + "\n\n"
                
                for i, val in enumerate(solucion):
                    if abs(val) > self.solver.epsilon:
                        if self.usar_fracciones:
                            frac = Fraction(val).limit_denominator()
                            resultado_resumen += f"x{i+1} = {frac}\n"
                        else:
                            resultado_resumen += f"x{i+1} = {val:.6f}\n"
                
                tipo_original = "minimización" if self.solver.tipo_problema == "min" else "maximización"
                if self.usar_fracciones:
                    obj_frac = Fraction(valor).limit_denominator()
                    resultado_resumen += f"\nValor óptimo de {tipo_original}: {obj_frac}\n"
                else:
                    resultado_resumen += f"\nValor óptimo de {tipo_original}: {valor:.6f}\n"
                
                resultado_resumen += f"\nIteraciones realizadas: {len(self.solver.historial_tableaux) - 1}\n"
                resultado_resumen += "\n💡 Para ver el proceso detallado paso a paso,\n   vaya a la pestaña 'Proceso de Resolución'"

                self.text_resultado_principal.delete("1.0", tk.END)
                self.text_resultado_principal.insert(tk.END, resultado_resumen)
                
                messagebox.showinfo("Éxito", "Problema resuelto correctamente.\nVea la pestaña 'Proceso de Resolución' para el análisis completo.")
            else:
                messagebox.showerror("Error", "No se pudo resolver el problema")

        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def exportar_imagenes(self):
        try:
            if not hasattr(self.solver, 'historial_tableaux') or not self.solver.historial_tableaux:
                messagebox.showwarning("Advertencia", "No hay tableaux para exportar. Primero resuelva un problema.")
                return
                
            carpeta = filedialog.askdirectory(initialdir=EXPORT_PATH, title="Selecciona carpeta de exportación")
            if not carpeta:
                return
                
            self.solver.visualizar_tableaux()
            archivos_movidos = 0
            
            for i in range(len(self.solver.historial_tableaux)):
                src = f"tableau_{i}.png"
                dst = os.path.join(carpeta, f"tableau_{i}.png")
                if os.path.exists(src):
                    os.rename(src, dst)
                    archivos_movidos += 1
                    
            messagebox.showinfo("Exportado", f"{archivos_movidos} imágenes guardadas en:\n{carpeta}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexAppModern(root)
    root.mainloop()