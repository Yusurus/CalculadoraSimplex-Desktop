import tkinter as tk
from tkinter import messagebox
from vista_simplex import SimplexVista
from servicio_simplex import SimplexServicio

class SimplexControlador:
    def __init__(self):
        self.root = tk.Tk()
        self.vista = SimplexVista(self.root)
        self.servicio = SimplexServicio()
        
        # Configurar callbacks de la vista
        self.vista.set_callback_configurar_objetivo(self.configurar_objetivo)
        self.vista.set_callback_agregar_restriccion(self.agregar_restriccion)
        self.vista.set_callback_eliminar_restriccion(self.eliminar_restriccion)
        self.vista.set_callback_limpiar_restricciones(self.limpiar_restricciones)
        self.vista.set_callback_resolver(self.resolver_problema)
        self.vista.set_callback_exportar_imagenes(self.exportar_imagenes)
        self.vista.set_callback_update_result_tab(self.actualizar_tab_resultado)
    
    def configurar_objetivo(self):
        """Configura la función objetivo basada en el número de variables"""
        try:
            num_vars_str = self.vista.obtener_numero_variables()
            num_vars, error = self.servicio.validar_numero_variables(num_vars_str)
            
            if error:
                messagebox.showerror("Error", error)
                return
            
            # Crear área de coeficientes en la vista
            self.vista.crear_area_coeficientes(num_vars)
            messagebox.showinfo("Éxito", f"Función objetivo configurada para {num_vars} variables")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error configurando función objetivo: {str(e)}")
    
    def agregar_restriccion(self):
        """Agrega una nueva restricción a la interfaz"""
        try:
            # Verificar que se haya configurado la función objetivo primero
            if not self.vista.tiene_coeficientes_objetivo():
                messagebox.showwarning("Advertencia", 
                    "Primero debe configurar la función objetivo")
                return
            
            num_vars_str = self.vista.obtener_numero_variables()
            num_vars, error = self.servicio.validar_numero_variables(num_vars_str)
            
            if error:
                messagebox.showerror("Error", error)
                return
            
            # Crear nueva restricción en la vista
            self.vista.crear_restriccion(num_vars)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error agregando restricción: {str(e)}")
    
    def eliminar_restriccion(self, fila_frame):
        """Elimina una restricción específica"""
        try:
            self.vista.eliminar_restriccion_especifica(fila_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando restricción: {str(e)}")
    
    def limpiar_restricciones(self):
        """Limpia todas las restricciones"""
        try:
            respuesta = messagebox.askyesno("Confirmar", 
                "¿Está seguro de que desea eliminar todas las restricciones?")
            if respuesta:
                self.vista.limpiar_area_restricciones()
                messagebox.showinfo("Éxito", "Todas las restricciones han sido eliminadas")
        except Exception as e:
            messagebox.showerror("Error", f"Error limpiando restricciones: {str(e)}")
    
    def resolver_problema(self):
        """Resuelve el problema de programación lineal"""
        try:
            # Validar que se haya configurado todo
            if not self.vista.tiene_coeficientes_objetivo():
                messagebox.showwarning("Advertencia", 
                    "Debe configurar la función objetivo primero")
                return
            
            if not self.vista.tiene_restricciones():
                messagebox.showwarning("Advertencia", 
                    "Debe agregar al menos una restricción")
                return
            
            # Obtener datos de la vista
            coeficientes_str = self.vista.obtener_coeficientes_objetivo()
            tipo_problema = self.vista.obtener_tipo_problema()
            restricciones_data = self.vista.obtener_restricciones_data()
            
            # Configurar preferencias del servicio
            self.servicio.configurar_fracciones(True)  # Usar fracciones por defecto
            
            # Resolver el problema
            resumen, proceso_completo, solucion_data, error = self.servicio.resolver_problema(
                coeficientes_str, tipo_problema, restricciones_data
            )
            
            if error:
                messagebox.showerror("Error", error)
                return
            
            # Mostrar resultados en la vista
            self.vista.mostrar_resultado_principal(resumen)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", 
                "Problema resuelto exitosamente.\n\n"
                "Vea los resultados en el área de resultados y\n"
                "el proceso detallado en la pestaña 'Proceso de Resolución'.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error resolviendo problema: {str(e)}")
    
    def exportar_imagenes(self):
        """Exporta los tableaux como imágenes"""
        try:
            if not self.servicio.tiene_solucion():
                messagebox.showwarning("Advertencia", 
                    "Debe resolver un problema primero antes de exportar")
                return
            
            exito, mensaje = self.servicio.exportar_tableaux_como_imagenes()
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando imágenes: {str(e)}")
    
    def actualizar_tab_resultado(self, event):
        """Actualiza la pestaña de resultados cuando se selecciona"""
        try:
            # Obtener la pestaña seleccionada
            notebook = event.widget
            tab_seleccionada = notebook.select()
            tab_nombre = notebook.tab(tab_seleccionada, "text")
            
            # Si se selecciona la pestaña de proceso, actualizar el contenido
            if tab_nombre == "Proceso de Resolución":
                proceso_completo = self.servicio.obtener_proceso_completo()
                self.vista.mostrar_proceso_completo(proceso_completo)
                
        except Exception as e:
            print(f"Error actualizando pestaña de resultado: {str(e)}")
    
    def ejecutar(self):
        """Inicia la aplicación"""
        # Configurar el cierre de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Mostrar mensaje de bienvenida
        messagebox.showinfo("Bienvenido", 
            "Simplex Solver - Solucionador de Programación Lineal\n\n"
            "Pasos para usar la aplicación:\n"
            "1. Ingrese el número de variables\n"
            "2. Configure la función objetivo\n"
            "3. Agregue restricciones\n"
            "4. Haga clic en 'Resolver'\n\n"
            "¡Disfrute resolviendo problemas de programación lineal!")
        
        # Iniciar el bucle principal
        self.root.mainloop()
    
    def cerrar_aplicacion(self):
        """Maneja el cierre de la aplicación"""
        respuesta = messagebox.askyesnocancel("Salir", 
            "¿Está seguro de que desea salir de la aplicación?")
        if respuesta:
            self.root.destroy()


def main():
    """Función principal para ejecutar la aplicación"""
    try:
        controlador = SimplexControlador()
        controlador.ejecutar()
    except Exception as e:
        messagebox.showerror("Error Fatal", 
            f"Error iniciando la aplicación: {str(e)}")

if __name__ == "__main__":
    main()