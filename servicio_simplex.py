import os
import io
import sys
from contextlib import redirect_stdout
from fractions import Fraction
from tkinter import messagebox, filedialog
from app import SolucionadorPL, parsear_fraccion

EXPORT_PATH = "/mnt/data/exportaciones_simplex"

class SimplexServicio:
    def __init__(self):
        self.solver = SolucionadorPL()
        self.usar_fracciones = True
        self.proceso_completo = ""
    
    def validar_numero_variables(self, num_vars_str):
        """Valida el número de variables introducido"""
        try:
            n = int(num_vars_str)
            if n <= 0:
                raise ValueError("El número debe ser positivo")
            return n, None
        except ValueError:
            return None, "Ingrese un número válido de variables (entero positivo)"
    
    def validar_coeficientes_objetivo(self, coeficientes_str):
        """Valida y convierte los coeficientes de la función objetivo"""
        try:
            coeficientes = [parsear_fraccion(coef) for coef in coeficientes_str]
            return coeficientes, None
        except ValueError:
            return None, "Coeficientes de función objetivo inválidos"
    
    def validar_restricciones(self, restricciones_data):
        """Valida y convierte los datos de las restricciones"""
        try:
            A, b, d = [], [], []
            for entradas, desig_var, rhs_entry, _ in restricciones_data:
                fila = [parsear_fraccion(e.get()) for e in entradas]
                lado_derecho = parsear_fraccion(rhs_entry.get())
                A.append(fila)
                b.append(lado_derecho)
                d.append(desig_var.get())
            return A, b, d, None
        except ValueError:
            return None, None, None, "Valores de restricciones inválidos"
    
    def configurar_solver(self, coeficientes, tipo_problema, A, b, d):
        """Configura el solver con los datos del problema"""
        self.solver = SolucionadorPL()
        self.solver.usar_fracciones = self.usar_fracciones
        self.solver.verbose = True
        self.solver.establecer_objetivo(coeficientes, tipo_problema)
        self.solver.agregar_restricciones(A, b, d)
    
    def capturar_salida_solver(self):
        """Captura toda la salida del solver incluyendo tableaux y comentarios"""
        salida_buffer = io.StringIO()
        
        with redirect_stdout(salida_buffer):
            try:
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
                    if abs(val) > self.solver.epsilon:
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
        
        salida_completa = salida_buffer.getvalue()
        salida_buffer.close()
        
        return salida_completa, solucion, valor
    
    def generar_resumen_solucion(self, solucion, valor):
        """Genera un resumen de la solución para mostrar en la interfaz principal"""
        if solucion is None or valor is None:
            return "No se pudo resolver el problema"
        
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
        
        return resultado_resumen
    
    def resolver_problema(self, coeficientes_str, tipo_problema, restricciones_data):
        """Resuelve el problema de programación lineal completo"""
        # Validar coeficientes
        coeficientes, error = self.validar_coeficientes_objetivo(coeficientes_str)
        if error:
            return None, None, None, error
        
        # Validar restricciones
        A, b, d, error = self.validar_restricciones(restricciones_data)
        if error:
            return None, None, None, error
        
        # Configurar solver
        self.configurar_solver(coeficientes, tipo_problema, A, b, d)
        
        # Resolver y capturar salida
        proceso_completo, solucion, valor = self.capturar_salida_solver()
        
        if solucion is not None and valor is not None:
            self.proceso_completo = proceso_completo
            resumen = self.generar_resumen_solucion(solucion, valor)
            return resumen, proceso_completo, (solucion, valor), None
        else:
            return None, None, None, "No se pudo resolver el problema"
    
    def exportar_tableaux_como_imagenes(self, carpeta_destino=None):
        """Exporta los tableaux como imágenes"""
        try:
            if not hasattr(self.solver, 'historial_tableaux') or not self.solver.historial_tableaux:
                return False, "No hay tableaux para exportar. Primero resuelva un problema."
            
            if carpeta_destino is None:
                carpeta_destino = filedialog.askdirectory(
                    initialdir=EXPORT_PATH, 
                    title="Selecciona carpeta de exportación"
                )
                if not carpeta_destino:
                    return False, "Exportación cancelada"
            
            self.solver.visualizar_tableaux()
            archivos_movidos = 0
            
            for i in range(len(self.solver.historial_tableaux)):
                src = f"tableau_{i}.png"
                dst = os.path.join(carpeta_destino, f"tableau_{i}.png")
                if os.path.exists(src):
                    os.rename(src, dst)
                    archivos_movidos += 1
            
            mensaje = f"{archivos_movidos} imágenes guardadas en:\n{carpeta_destino}"
            return True, mensaje
            
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"
    
    def obtener_proceso_completo(self):
        """Obtiene el proceso completo de resolución"""
        return self.proceso_completo
    
    def tiene_solucion(self):
        """Verifica si hay una solución disponible"""
        return hasattr(self.solver, 'historial_tableaux') and self.solver.historial_tableaux
    
    def configurar_fracciones(self, usar_fracciones):
        """Configura el uso de fracciones"""
        self.usar_fracciones = usar_fracciones