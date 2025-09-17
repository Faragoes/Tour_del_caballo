import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

movimientos_caballo = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                       (-2, -1), (-1, -2), (1, -2), (2, -1)]

class TourCaballoManual:
    def __init__(self, root):
        self.root = root
        self.nivel = 5
        self.tamaño_celda = 80

        # Colores modo oscuro y claro
        self.modos_colores = {
            "oscuro": {
                "fondo": "#1e1e1e",
                "claro": "#2e2e2e",
                "visitado": "#3e5e3e",
                "pista": "#ffff00",
                "texto": "#ffffff",
                "cuadros_claros": "#3a3a3a",
                "cuadros_oscuros": "#121212",
                "boton_bg": "#2e2e2e",
                "boton_fg": "#ffffff",
            },
            "claro": {
                "fondo": "#f0f0f0",
                "claro": "#d0d0d0",
                "visitado": "#a3c293",
                "pista": "#ff9900",
                "texto": "#000000",
                "cuadros_claros": "#e0e0e0",
                "cuadros_oscuros": "#a0a0a0",
                "boton_bg": "#d0d0d0",
                "boton_fg": "#000000",
            }
        }

        self.modo_actual = "oscuro"
        self.colores = self.modos_colores[self.modo_actual]

        self.frame_superior = tk.Frame(root, bg=self.colores["fondo"])
        self.frame_superior.pack()

        self.boton_reiniciar = tk.Button(
            self.frame_superior, text="Reiniciar nivel",
            command=self.reiniciar_nivel,
            bg=self.colores["boton_bg"], fg=self.colores["boton_fg"]
        )
        self.boton_reiniciar.pack(side=tk.LEFT, padx=10, pady=5)

        self.boton_modo = tk.Button(
            self.frame_superior, text="Modo Claro",
            command=self.cambiar_modo,
            bg=self.colores["boton_bg"], fg=self.colores["boton_fg"]
        )
        self.boton_modo.pack(side=tk.LEFT, padx=10, pady=5)

        self.canvas = tk.Canvas(root, bg=self.colores["fondo"], highlightthickness=0,
                                width=self.nivel * self.tamaño_celda,
                                height=self.nivel * self.tamaño_celda)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.manejar_click)

        self.img_original = Image.open("caballo.png").resize((self.tamaño_celda - 20, self.tamaño_celda - 20))
        self.img_caballo = ImageTk.PhotoImage(self.img_original)

        self.iniciar_nivel()

    def cambiar_modo(self):
        # Cambiar modo
        self.modo_actual = "claro" if self.modo_actual == "oscuro" else "oscuro"
        self.colores = self.modos_colores[self.modo_actual]

        # Actualizar colores UI
        self.frame_superior.config(bg=self.colores["fondo"])
        self.boton_reiniciar.config(bg=self.colores["boton_bg"], fg=self.colores["boton_fg"])
        self.boton_modo.config(
            bg=self.colores["boton_bg"],
            fg=self.colores["boton_fg"],
            text="Modo Oscuro" if self.modo_actual == "claro" else "Modo Claro"
        )
        self.canvas.config(bg=self.colores["fondo"])

        # Redibujar tablero con nuevos colores
        self.dibujar_tablero()
        self.dibujar_caballo()
        self.resaltar_movimientos_legales()

    def iniciar_nivel(self):
        self.canvas.config(width=self.nivel * self.tamaño_celda,
                           height=self.nivel * self.tamaño_celda)

        self.tablero = [[-1 for _ in range(self.nivel)] for _ in range(self.nivel)]
        self.movimiento_actual = 0
        self.pos_x = 0
        self.pos_y = 0
        self.tablero[self.pos_y][self.pos_x] = self.movimiento_actual
        self.moviendo = False
        self.dibujar_tablero()
        self.dibujar_caballo()
        self.resaltar_movimientos_legales()

    def reiniciar_nivel(self):
        self.iniciar_nivel()

    def dibujar_tablero(self):
        self.canvas.delete("all")
        lado = self.tamaño_celda
        for i in range(self.nivel):
            for j in range(self.nivel):
                x1, y1 = j * lado, i * lado
                x2, y2 = x1 + lado, y1 + lado
                color = self.colores["cuadros_claros"] if (i + j) % 2 == 0 else self.colores["cuadros_oscuros"]
                if self.tablero[i][j] != -1:
                    color = self.colores["visitado"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cccccc")
                if self.tablero[i][j] != -1:
                    self.canvas.create_text((x1 + x2)//2, (y1 + y2)//2, text=str(self.tablero[i][j]),
                                            fill=self.colores["texto"], font=("Helvetica", 14, "bold"))

    def dibujar_caballo(self):
        lado = self.tamaño_celda
        x, y = self.pos_x * lado + 10, self.pos_y * lado + 10
        self.caballo = self.canvas.create_image(x, y, anchor=tk.NW, image=self.img_caballo)

    def mover_caballo_animado(self, x_final, y_final):
        if self.moviendo:
            return
        self.moviendo = True

        pasos = 10
        dx = ((x_final - self.pos_x) * self.tamaño_celda) // pasos
        dy = ((y_final - self.pos_y) * self.tamaño_celda) // pasos
        contador = 0

        def animar():
            nonlocal contador
            if contador < pasos:
                self.canvas.move(self.caballo, dx, dy)
                contador += 1
                self.root.after(20, animar)
            else:
                self.pos_x, self.pos_y = x_final, y_final
                self.dibujar_tablero()
                self.dibujar_caballo()
                self.canvas.tag_raise(self.caballo)
                x = self.pos_x * self.tamaño_celda + 10
                y = self.pos_y * self.tamaño_celda + 10
                self.canvas.coords(self.caballo, x, y)
                self.moviendo = False
                if self.movimiento_actual == self.nivel * self.nivel - 1:
                    self.nivel_completado()
                else:
                    self.resaltar_movimientos_legales()

        animar()

    def resaltar_movimientos_legales(self):
        lado = self.tamaño_celda
        self.movimientos_legales = []
        for dx, dy in movimientos_caballo:
            nx, ny = self.pos_x + dx, self.pos_y + dy
            if 0 <= nx < self.nivel and 0 <= ny < self.nivel and self.tablero[ny][nx] == -1:
                x1, y1 = nx * lado, ny * lado
                x2, y2 = x1 + lado, y1 + lado
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.colores["pista"], width=3)
                self.movimientos_legales.append((nx, ny))

        if not self.movimientos_legales and self.movimiento_actual < self.nivel * self.nivel - 1:
            messagebox.showinfo("😢 Fin del juego", "No quedan movimientos válidos.")
            self.reiniciar_nivel()

    def manejar_click(self, evento):
        if self.moviendo:
            return
        lado = self.tamaño_celda
        col = evento.x // lado
        fila = evento.y // lado
        if (col, fila) in self.movimientos_legales:
            self.movimiento_actual += 1
            self.tablero[fila][col] = self.movimiento_actual
            self.mover_caballo_animado(col, fila)
        else:
            messagebox.showinfo("Movimiento inválido", "No puedes mover ahí.")

    def nivel_completado(self):
        if messagebox.askyesno("¡Nivel completado!", f"¡Completaste el tablero {self.nivel}x{self.nivel}!\n¿Quieres continuar al siguiente nivel?"):
            self.nivel += 1
            self.iniciar_nivel()
        else:
            self.root.destroy()

# Ejecutar juego
if __name__ == "__main__":
    root = tk.Tk()
    root.title("♞ Tour del Caballo - Modo Oscuro")
    juego = TourCaballoManual(root)
    root.mainloop()
