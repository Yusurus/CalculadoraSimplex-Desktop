import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from fractions import Fraction

class SolucionadorPL:
    """
    Solucionador de Programación Lineal usando el método Simplex con Big M
    """
    
    def __init__(self):
        """Inicializa el solucionador con valores por defecto"""
        self.A = None                    # Matriz de coeficientes de restricciones
        self.b = None                    # Vector de lado derecho
        self.c = None                    # Vector de coeficientes de función objetivo
        self.tableau = None              # Tableau actual del método simplex
        self.vars_basicas = None         # Variables básicas actuales
        self.vars_no_basicas = None      # Variables no básicas actuales
        self.tipo_problema = "max"       # Tipo de problema (max/min)
        self.vars_artificiales = []     # Lista de variables artificiales
        self.indices_artificiales = []  # Índices de variables artificiales
        self.M = None                   # Valor Big M
        self.num_restricciones = 0      # Número de restricciones
        self.num_variables = 0          # Número de variables originales
        self.historial_tableaux = []    # Historial de tableaux para visualización
        self.usar_fracciones = True     # Mostrar resultados como fracciones
        self.verbose = True             # Mostrar información detallada
        self.epsilon = 1e-12            # Tolerancia para comparaciones numéricas
        self.vars_originales = []       # Índices de variables originales
        self.vars_holgura = []          # Índices de variables de holgura
        self.vars_artificiales_idx = [] # Índices de variables artificiales

    def establecer_objetivo(self, coeficientes, tipo_problema="max"):
        """
        Establece la función objetivo
        
        Args:
            coeficientes: Lista de coeficientes de la función objetivo
            tipo_problema: "max" o "min"
        """
        self.c = np.array(coeficientes, dtype=float)
        self.num_variables = len(coeficientes)
        self.tipo_problema = tipo_problema.lower()
        
        # Convertir problema de minimización a maximización
        if self.tipo_problema == "min":
            self.c = -self.c
            
        self.vars_originales = list(range(self.num_variables))

    def agregar_restricciones(self, A, b, desigualdades):
        """
        Agrega restricciones al problema
        
        Args:
            A: Matriz de coeficientes de restricciones
            b: Vector de lado derecho
            desigualdades: Lista de tipos de desigualdad ("<=", ">=", "=")
        """
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        self.num_restricciones = len(b)
        
        if self.A is None:
            self.A = A
            self.b = b
            self.desigualdades = desigualdades
        else:
            self.A = np.vstack((self.A, A))
            self.b = np.concatenate((self.b, b))
            self.desigualdades.extend(desigualdades)

    def _calcular_big_m(self):
        """Calcula el valor Big M basado en los coeficientes del problema"""
        max_obj = np.max(np.abs(self.c)) if len(self.c) > 0 else 1
        max_constr = np.max(np.abs(self.A)) if self.A is not None and self.A.size > 0 else 1
        max_rhs = np.max(np.abs(self.b)) if self.b is not None and self.b.size > 0 else 1
        
        max_value = max(max_obj, max_constr, max_rhs)
        M = 1000 * max_value
        M = max(1000, M)
        
        if self.verbose:
            print(f"Valor Big M calculado: {M}")
        return M

    def _convertir_a_forma_estandar(self):
        """Convierte el problema a forma estándar agregando variables de holgura y artificiales"""
        if self.M is None:
            self.M = self._calcular_big_m()
        
        # Contar variables necesarias
        num_holgura_exceso = 0
        num_artificiales = 0
        
        for desigualdad in self.desigualdades:
            if desigualdad == "<=":
                num_holgura_exceso += 1
            elif desigualdad == ">=":
                num_holgura_exceso += 1
                num_artificiales += 1
            elif desigualdad == "=":
                num_artificiales += 1
        
        # Crear matriz expandida
        total_vars = self.num_variables + num_holgura_exceso + num_artificiales
        nueva_A = np.zeros((self.num_restricciones, total_vars))
        nueva_A[:, :self.num_variables] = self.A
        
        nuevo_c = np.zeros(total_vars)
        nuevo_c[:self.num_variables] = self.c
        
        # Inicializar variables básicas
        self.vars_basicas = [None] * self.num_restricciones
        self.vars_no_basicas = []
        
        # Agregar variables de holgura y artificiales
        idx_holgura = self.num_variables
        idx_artificial = self.num_variables + num_holgura_exceso
        
        for i, desigualdad in enumerate(self.desigualdades):
            if desigualdad == "<=":
                # Agregar variable de holgura
                nueva_A[i, idx_holgura] = 1
                self.vars_basicas[i] = idx_holgura
                self.vars_holgura.append(idx_holgura)
                idx_holgura += 1
                
            elif desigualdad == ">=":
                # Agregar variable de exceso (negativa)
                nueva_A[i, idx_holgura] = -1
                self.vars_holgura.append(idx_holgura)
                idx_holgura += 1
                
                # Agregar variable artificial
                nueva_A[i, idx_artificial] = 1
                self.vars_basicas[i] = idx_artificial
                self.vars_artificiales.append(idx_artificial)
                self.indices_artificiales.append(idx_artificial)
                self.vars_artificiales_idx.append(idx_artificial)
                nuevo_c[idx_artificial] = -self.M
                idx_artificial += 1
                
            elif desigualdad == "=":
                # Agregar variable artificial
                nueva_A[i, idx_artificial] = 1
                self.vars_basicas[i] = idx_artificial
                self.vars_artificiales.append(idx_artificial)
                self.indices_artificiales.append(idx_artificial)
                self.vars_artificiales_idx.append(idx_artificial)
                nuevo_c[idx_artificial] = -self.M
                idx_artificial += 1
        
        # Actualizar matrices
        self.A = nueva_A
        self.c = nuevo_c
        
        # Manejar RHS negativos
        for i in range(len(self.b)):
            if self.b[i] < 0:
                self.A[i] = -self.A[i]
                self.b[i] = -self.b[i]
                if self.desigualdades[i] == ">=":
                    self.desigualdades[i] = "<="
                elif self.desigualdades[i] == "<=":
                    self.desigualdades[i] = ">="
        
        # Establecer variables no básicas
        self.vars_no_basicas = list(set(range(total_vars)) - set(self.vars_basicas))

    def _crear_tableau_inicial(self):
        """Crea el tableau inicial del método simplex"""
        filas = self.num_restricciones + 1
        columnas = self.A.shape[1] + 1
        
        # Inicializar tableau
        self.tableau = np.zeros((filas, columnas))
        self.tableau[:self.num_restricciones, :self.A.shape[1]] = self.A
        self.tableau[:self.num_restricciones, -1] = self.b
        self.tableau[self.num_restricciones, :self.A.shape[1]] = -self.c
        
        # Aplicar método Big M si hay variables artificiales
        if len(self.vars_artificiales) > 0:
            if self.verbose:
                print("\nAplicando método Big M para variables artificiales")
            
            for art_idx in self.indices_artificiales:
                for j in range(self.num_restricciones):
                    if art_idx == self.vars_basicas[j]:
                        coeff = self.tableau[self.num_restricciones, art_idx]
                        self.tableau[self.num_restricciones, :] += (-coeff) * self.tableau[j, :]
                        break
        
        self.historial_tableaux.append(self.tableau.copy())

    def _mostrar_tableau(self, iteracion=None):
        """Muestra el tableau actual en formato tabular"""
        if not self.verbose:
            return
        
        tableau = self.tableau.copy()
        filas, columnas = tableau.shape
        
        # Reorganizar columnas para mejor visualización
        idx_orig = self.vars_originales
        idx_holgura = self.vars_holgura
        idx_art = self.vars_artificiales_idx
        idx_rhs = [columnas - 1]
        
        nuevo_orden = idx_orig + idx_holgura + idx_art + idx_rhs
        tableau_reorg = np.zeros((filas, len(nuevo_orden)))
        
        for i, idx_anterior in enumerate(nuevo_orden):
            tableau_reorg[:, i] = tableau[:, idx_anterior]
        
        # Crear etiquetas de columnas
        headers = []
        for i in idx_orig:
            headers.append(f"x{i+1}")
        for i in idx_holgura:
            headers.append(f"x{i+1}")
        for i, idx in enumerate(idx_art):
            headers.append(f"a{i+1}")
        headers.append("LD")
        
        # Crear etiquetas de filas
        etiquetas_filas = []
        for j in range(filas - 1):
            idx_basica = self.vars_basicas[j]
            if idx_basica in self.vars_originales:
                etiquetas_filas.append(f"x{idx_basica+1}")
            elif idx_basica in self.vars_holgura:
                etiquetas_filas.append(f"x{idx_basica+1}")
            elif idx_basica in self.vars_artificiales_idx:
                etiquetas_filas.append(f"a{self.vars_artificiales_idx.index(idx_basica)+1}")
        etiquetas_filas.append("z")
        
        # Formatear números
        if self.usar_fracciones:
            tableau_str = np.zeros_like(tableau_reorg, dtype=object)
            for i in range(filas):
                for j in range(len(nuevo_orden)):
                    frac = Fraction(tableau_reorg[i, j]).limit_denominator()
                    if frac.denominator == 1:
                        tableau_str[i, j] = str(frac.numerator)
                    else:
                        tableau_str[i, j] = f"{frac.numerator}/{frac.denominator}"
            tableau_mostrar = tabulate(tableau_str, headers=headers, 
                                     showindex=etiquetas_filas, tablefmt="grid")
        else:
            tableau_mostrar = tabulate(tableau_reorg, headers=headers, 
                                     showindex=etiquetas_filas, tablefmt="grid")
        
        titulo = f"Iteración {iteracion}" if iteracion is not None else "Tableau Inicial"
        print(f"\n{titulo}")
        print(tableau_mostrar)

    def _seleccionar_columna_pivote(self):
        """Selecciona la columna pivote usando la regla del más negativo"""
        fila_objetivo = self.tableau[self.num_restricciones, :-1]
        idx_min = np.argmin(fila_objetivo)
        
        if fila_objetivo[idx_min] >= -self.epsilon:
            return -1  # Solución óptima encontrada
        
        return idx_min

    def _seleccionar_fila_pivote(self, col_pivote):
        """Selecciona la fila pivote usando la prueba de la razón mínima"""
        razones = []
        
        for i in range(self.num_restricciones):
            if self.tableau[i, col_pivote] <= self.epsilon:
                razones.append(float('inf'))
            else:
                razones.append(self.tableau[i, -1] / self.tableau[i, col_pivote])
        
        if all(r == float('inf') for r in razones):
            return -1  # Problema no acotado
        
        # Encontrar la razón mínima no negativa
        razon_min = float('inf')
        idx_min = -1
        
        for i, razon in enumerate(razones):
            if 0 <= razon < razon_min:
                razon_min = razon
                idx_min = i
        
        return idx_min

    def _pivotear(self, fila_pivote, col_pivote):
        """Realiza las operaciones de pivoteo en el tableau"""
        elemento_pivote = self.tableau[fila_pivote, col_pivote]
        
        if self.verbose:
            print(f"  Elemento pivote: {elemento_pivote:.4f}")
        
        # Normalizar fila pivote
        self.tableau[fila_pivote] = self.tableau[fila_pivote] / elemento_pivote
        
        # Eliminar en otras filas
        for i in range(self.tableau.shape[0]):
            if i != fila_pivote:
                factor = self.tableau[i, col_pivote]
                self.tableau[i] = self.tableau[i] - factor * self.tableau[fila_pivote]
        
        # Actualizar variables básicas
        var_saliente = self.vars_basicas[fila_pivote]
        var_entrante = col_pivote
        
        self.vars_basicas[fila_pivote] = var_entrante
        
        if var_saliente in self.vars_artificiales:
            self.vars_artificiales.remove(var_saliente)
        
        self.vars_no_basicas = list(set(range(self.tableau.shape[1] - 1)) - set(self.vars_basicas))
        self.historial_tableaux.append(self.tableau.copy())

    def resolver(self):
        """
        Resuelve el problema de programación lineal usando el método simplex
        
        Returns:
            tuple: (solución, valor_objetivo)
        """
        # Preparar problema
        self._convertir_a_forma_estandar()
        self._crear_tableau_inicial()
        self._mostrar_tableau(iteracion=0)
        
        iteracion = 1
        max_iteraciones = 100
        
        # Algoritmo simplex
        while iteracion <= max_iteraciones:
            # Seleccionar columna pivote
            col_pivote = self._seleccionar_columna_pivote()
            if col_pivote == -1:
                print("\n¡Solución óptima encontrada!")
                break
            
            # Seleccionar fila pivote
            fila_pivote = self._seleccionar_fila_pivote(col_pivote)
            if fila_pivote == -1:
                print("\n¡El problema es no acotado!")
                break
            
            if self.verbose:
                print(f"\nPivote: Fila {fila_pivote+1}, Columna {col_pivote+1}")
            
            # Realizar pivoteo
            self._pivotear(fila_pivote, col_pivote)
            self._mostrar_tableau(iteracion=iteracion)
            
            iteracion += 1
        
        # Verificar límite de iteraciones
        if iteracion > max_iteraciones:
            print("\nAdvertencia: Se alcanzó el máximo de iteraciones. La solución puede no ser óptima.")
        
        # Extraer solución
        solucion = np.zeros(self.num_variables)
        for i, var in enumerate(self.vars_basicas):
            if var < self.num_variables:
                solucion[var] = self.tableau[i, -1]
        
        # Verificar factibilidad
        tiene_artificial_en_solucion = False
        for i, var in enumerate(self.vars_basicas):
            if var in self.indices_artificiales and abs(self.tableau[i, -1]) > self.epsilon:
                tiene_artificial_en_solucion = True
                break
        
        if tiene_artificial_en_solucion:
            print("\nAdvertencia: Variable artificial permanece en la solución final con valor no cero.")
            print("Esto indica que el problema es infactible.")
        
        # Calcular valor objetivo
        valor_objetivo = self.tableau[self.num_restricciones, -1]
        if self.tipo_problema == "min":
            valor_objetivo = -valor_objetivo
        
        return solucion, valor_objetivo

    def visualizar_tableaux(self):
        """Genera visualizaciones PNG de todos los tableaux"""
        if not self.historial_tableaux:
            print("No hay tableaux para visualizar. Ejecute resolver() primero.")
            return
        
        num_tableaux = len(self.historial_tableaux)
        
        for i, tableau in enumerate(self.historial_tableaux):
            filas, columnas = tableau.shape
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.set_axis_off()
            
            # Reorganizar para visualización
            idx_orig = self.vars_originales
            idx_holgura = self.vars_holgura
            idx_art = self.vars_artificiales_idx
            idx_rhs = [columnas - 1]
            
            nuevo_orden = idx_orig + idx_holgura + idx_art + idx_rhs
            tableau_reorg = np.zeros((filas, len(nuevo_orden)))
            
            for j, idx_anterior in enumerate(nuevo_orden):
                tableau_reorg[:, j] = tableau[:, idx_anterior]
            
            # Etiquetas
            etiquetas_col = []
            for idx in idx_orig:
                etiquetas_col.append(f"x{idx+1}")
            for idx in idx_holgura:
                etiquetas_col.append(f"x{idx+1}")
            for j, idx in enumerate(idx_art):
                etiquetas_col.append(f"a{j+1}")
            etiquetas_col.append("LD")
            
            etiquetas_fila = []
            for j in range(filas - 1):
                idx_basica = self.vars_basicas[j]
                if idx_basica in self.vars_originales:
                    etiquetas_fila.append(f"x{idx_basica+1}")
                elif idx_basica in self.vars_holgura:
                    etiquetas_fila.append(f"x{idx_basica+1}")
                elif idx_basica in self.vars_artificiales_idx:
                    etiquetas_fila.append(f"a{self.vars_artificiales_idx.index(idx_basica)+1}")
            etiquetas_fila.append("z")
            
            # Formatear datos
            if self.usar_fracciones:
                datos_str = np.zeros_like(tableau_reorg, dtype=object)
                for r in range(filas):
                    for c in range(len(nuevo_orden)):
                        frac = Fraction(tableau_reorg[r, c]).limit_denominator()
                        if frac.denominator == 1:
                            datos_str[r, c] = str(frac.numerator)
                        else:
                            datos_str[r, c] = f"{frac.numerator}/{frac.denominator}"
                datos_mostrar = datos_str
            else:
                datos_mostrar = np.round(tableau_reorg, 4)
            
            # Crear tabla
            tabla = ax.table(
                cellText=datos_mostrar,
                loc='center',
                cellLoc='center',
                colLabels=etiquetas_col,
                rowLabels=etiquetas_fila
            )
            
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(10)
            tabla.scale(1.2, 1.5)
            
            titulo = f"Tableau Inicial" if i == 0 else f"Tableau después de Iteración {i}"
            plt.title(titulo)
            plt.tight_layout()
            plt.savefig(f"tableau_{i}.png")
            plt.close()
        
        print(f"\nVisualizaciones guardadas como tableau_0.png hasta tableau_{num_tableaux-1}.png")


def parsear_fraccion(s):
    """Convierte string a float, manejando fracciones"""
    if '/' in s:
        num, denom = s.split('/')
        return float(num) / float(denom)
    else:
        return float(s)


def parsear_entrada():
    """Interfaz de usuario para ingresar el problema de programación lineal"""
    solver = SolucionadorPL()
    
    print("\n===== SOLUCIONADOR DE PROGRAMACIÓN LINEAL =====")
    
    # Tipo de problema
    print("Ingrese el tipo de problema (max/min):")
    while True:
        tipo_problema = input().strip().lower()
        if tipo_problema in ("max", "min"):
            break
        else:
            print("Error: Ingrese 'max' o 'min'.")
    
    # Número de variables
    print("\nIngrese el número de variables de decisión:")
    while True:
        try:
            num_vars = int(input())
            if num_vars > 0:
                break
            else:
                print("Error: Ingrese un entero positivo.")
        except ValueError:
            print("Error: Ingrese un entero válido.")
    
    # Coeficientes de función objetivo
    print(f"\nIngrese {num_vars} coeficientes de la función objetivo (separados por espacios):")
    print("Puede usar decimales o fracciones como 1/3:")
    while True:
        entrada_c = input().split()
        if len(entrada_c) != num_vars:
            print(f"Error: Ingrese exactamente {num_vars} coeficientes.")
            continue
        try:
            c = [parsear_fraccion(coef) for coef in entrada_c]
            break
        except ValueError:
            print("Error: Ingrese números o fracciones válidos.")
    
    solver.establecer_objetivo(c, tipo_problema)
    
    # Número de restricciones
    print("\nIngrese el número de restricciones:")
    while True:
        try:
            num_restricciones = int(input())
            if num_restricciones > 0:
                break
            else:
                print("Error: Ingrese un entero positivo.")
        except ValueError:
            print("Error: Ingrese un entero válido.")
    
    # Restricciones
    A = []
    b = []
    desigualdades = []
    
    print("\nPara cada restricción, ingrese coeficientes, tipo de desigualdad (<=, >=, =), y valor del lado derecho:")
    print("Ejemplo: 2 3 <= 10  (significa 2x₁ + 3x₂ <= 10)")
    print("Puede usar valores decimales (3.14) o fracciones (1/3)")
    
    for i in range(num_restricciones):
        print(f"\nRestricción {i+1}:")
        while True:
            restriccion = input().strip()
            partes = restriccion.split()
            
            if len(partes) < 3:
                print("Error: Formato inválido. Ingrese coeficientes, desigualdad (<=, >=, =), y lado derecho.")
                continue
            
            desig = partes[-2]
            if desig not in ("<=", ">=", "="):
                print("Error: La desigualdad debe ser <=, >=, o =.")
                continue
            
            try:
                coefs = [parsear_fraccion(x) for x in partes[:-2]]
                rhs = parsear_fraccion(partes[-1])
                break
            except ValueError:
                print("Error: Ingrese números o fracciones válidos para coeficientes y lado derecho.")
        
        # Completar con ceros si faltan coeficientes
        if len(coefs) < num_vars:
            coefs.extend([0] * (num_vars - len(coefs)))
        
        A.append(coefs)
        b.append(rhs)
        desigualdades.append(desig)
    
    solver.agregar_restricciones(A, b, desigualdades)
    return solver


def main():
    """Función principal del programa"""
    print("\nSolucionador de Programación Lineal con método Simplex y Big M")
    
    # Obtener problema del usuario
    solver = parsear_entrada()
    
    # Configurar formato de salida
    while True:
        usar_fracciones = input("\n¿Mostrar resultados como fracciones? (s/n): ").strip().lower()
        if usar_fracciones in ("s", "n"):
            usar_fracciones = usar_fracciones == "s"
            break
        else:
            print("Error: Por favor ingrese 's' o 'n'.")
    
    solver.usar_fracciones = usar_fracciones
    
    # Resolver problema
    print("\n===== RESOLVIENDO PROBLEMA =====")
    solucion, valor_objetivo = solver.resolver()
    
    # Mostrar resultados
    print("\n===== SOLUCIÓN =====")
    for i, val in enumerate(solucion):
        if usar_fracciones:
            frac = Fraction(val).limit_denominator()
            if frac.denominator == 1:
                print(f"x{i+1} = {frac.numerator}")
            else:
                print(f"x{i+1} = {frac.numerator}/{frac.denominator}")
        else:
            print(f"x{i+1} = {val:.4f}")
    
    if usar_fracciones:
        obj_frac = Fraction(valor_objetivo).limit_denominator()
        if obj_frac.denominator == 1:
            print(f"Valor óptimo = {obj_frac.numerator}")
        else:
            print(f"Valor óptimo = {obj_frac.numerator}/{obj_frac.denominator}")
    else:
        print(f"Valor óptimo = {valor_objetivo:.4f}")
    
    # Opción de visualización
    while True:
        visualizar = input("\n¿Generar visualizaciones de tableaux? (s/n): ").strip().lower()
        if visualizar in ("s", "n"):
            if visualizar == "s":
                solver.visualizar_tableaux()
            break
        else:
            print("Error: Por favor ingrese 's' o 'n'.")


if __name__ == "__main__":
    main()