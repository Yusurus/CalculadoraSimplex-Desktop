import tkinter as tk
from tkinter import messagebox
from fractions import Fraction
from app import SolucionadorPL, parsear_fraccion  # Tu clase original

class SimplexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solucionador Simplex - Big M")
        self.solver = SolucionadorPL()

        self.tipo_problema = tk.StringVar(value="max")
        self.entradas_coef_obj = []
        self.entradas_restricciones = []

        self.build_ui()

    def build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Tipo de problema
        tk.Label(frame, text="Tipo de problema:").grid(row=0, column=0)
        tk.OptionMenu(frame, self.tipo_problema, "max", "min").grid(row=0, column=1)

        # Número de variables
        tk.Label(frame, text="Número de variables:").grid(row=1, column=0)
        self.num_vars_entry = tk.Entry(frame)
        self.num_vars_entry.grid(row=1, column=1)

        # Botón para configurar coeficientes
        tk.Button(frame, text="Configurar función objetivo", command=self.configurar_objetivo).grid(row=2, columnspan=2, pady=5)

        # Área dinámica para coeficientes
        self.area_coeficientes = tk.Frame(self.root)
        self.area_coeficientes.pack(pady=10)

        # Área para restricciones
        self.area_restricciones = tk.Frame(self.root)
        self.area_restricciones.pack(pady=10)

        # Botones para agregar restricción y resolver
        tk.Button(self.root, text="Agregar Restricción", command=self.agregar_restriccion).pack()
        tk.Button(self.root, text="Resolver", command=self.resolver).pack(pady=10)

        # Área de resultados
        self.resultado_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.resultado_label.pack(pady=5)

    def configurar_objetivo(self):
        try:
            n = int(self.num_vars_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Número de variables inválido")
            return

        # Limpiar entradas anteriores
        for widget in self.area_coeficientes.winfo_children():
            widget.destroy()

        self.entradas_coef_obj = []
        tk.Label(self.area_coeficientes, text="Coeficientes de la función objetivo:").pack()
        fila = tk.Frame(self.area_coeficientes)
        fila.pack()

        for i in range(n):
            entry = tk.Entry(fila, width=5)
            entry.pack(side=tk.LEFT)
            self.entradas_coef_obj.append(entry)

    def agregar_restriccion(self):
        n = len(self.entradas_coef_obj)
        if n == 0:
            messagebox.showerror("Error", "Primero configure la función objetivo")
            return

        fila = tk.Frame(self.area_restricciones)
        fila.pack(pady=2)

        entradas = []
        for _ in range(n):
            e = tk.Entry(fila, width=5)
            e.pack(side=tk.LEFT)
            entradas.append(e)

        desigualdad = tk.StringVar(value="<=")
        tk.OptionMenu(fila, desigualdad, "<=", ">=", "=").pack(side=tk.LEFT)

        rhs = tk.Entry(fila, width=5)
        rhs.pack(side=tk.LEFT)

        self.entradas_restricciones.append((entradas, desigualdad, rhs))

    def resolver(self):
        try:
            tipo = self.tipo_problema.get()
            coef = [parsear_fraccion(e.get()) for e in self.entradas_coef_obj]
            self.solver.establecer_objetivo(coef, tipo)

            A, b, d = [], [], []

            for entradas, desig_var, rhs_entry in self.entradas_restricciones:
                fila = [parsear_fraccion(e.get()) for e in entradas]
                lado_derecho = parsear_fraccion(rhs_entry.get())
                A.append(fila)
                b.append(lado_derecho)
                d.append(desig_var.get())

            self.solver.agregar_restricciones(A, b, d)
            solucion, valor = self.solver.resolver()

            resultado_texto = "\n".join([f"x{i+1} = {Fraction(val).limit_denominator()}" for i, val in enumerate(solucion)])
            resultado_texto += f"\nValor óptimo = {Fraction(valor).limit_denominator()}"
            self.resultado_label.config(text=resultado_texto)

        except Exception as e:
            messagebox.showerror("Error", str(e))


# Ejecutar
if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexApp(root)
    root.mainloop()
