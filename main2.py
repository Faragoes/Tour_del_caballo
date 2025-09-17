# tour_caballo_kivy.py
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp

# Movimientos del caballo (dx, dy)
MOVIMIENTOS_CABALLO = [(2, 1), (1, 2), (-1, 2), (-2, 1),
                       (-2, -1), (-1, -2), (1, -2), (2, -1)]

class BoardWidget(Widget):
    def __init__(self, nivel=5, **kwargs):
        super().__init__(**kwargs)
        self.nivel = nivel
        self.cell_size = 0
        self.labels = []
        self.valid_moves = []
        self.visited = set()
        self.movimiento_actual = 0
        self.pos_x = 0
        self.pos_y = 0

        self.palette_dark = {
            "background": (0.06, 0.06, 0.06, 1),
            "cell_light": (0.20, 0.20, 0.20, 1),
            "cell_dark": (0.10, 0.10, 0.10, 1),
            "visited": (0.22, 0.45, 0.22, 1),
            "highlight": (1, 0.85, 0.0, 1),
            "text": (1, 1, 1, 1)
        }
        self.palette_light = {
            "background": (0.95, 0.95, 0.95, 1),
            "cell_light": (0.98, 0.98, 0.98, 1),
            "cell_dark": (0.78, 0.78, 0.78, 1),
            "visited": (0.55, 0.75, 0.55, 1),
            "highlight": (1, 0.6, 0.0, 1),
            "text": (0, 0, 0, 1)
        }
        self.mode = "dark"
        self.colors = self.palette_dark
        Window.clearcolor = self.colors["background"]

        # inicializar tablero y labels
        self.rebuild_board()

        self.bind(size=self._update_board, pos=self._update_board)

    def set_mode(self, mode):
        self.mode = mode
        self.colors = self.palette_light if mode == "light" else self.palette_dark
        Window.clearcolor = self.colors["background"]
        for lbl in self.labels:
            lbl.color = self.colors["text"]
        self._update_board()

    def compute_valid_moves(self):
        self.valid_moves = []
        for dx, dy in MOVIMIENTOS_CABALLO:
            nx = self.pos_x + dx
            ny = self.pos_y + dy
            if 0 <= nx < self.nivel and 0 <= ny < self.nivel and self.tablero[ny][nx] == -1:
                self.valid_moves.append((nx, ny))

    def _update_board(self, *args):
        w, h = self.width, self.height
        board_size = min(w, h)
        self.cell_size = board_size / self.nivel
        origin_x = self.x + (w - board_size) / 2
        origin_y = self.y + (h - board_size) / 2

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.colors["background"])
            Rectangle(pos=(origin_x, origin_y), size=(board_size, board_size))

            for row in range(self.nivel):
                for col in range(self.nivel):
                    x = origin_x + col * self.cell_size
                    y = origin_y + (self.nivel - 1 - row) * self.cell_size
                    if self.tablero[row][col] != -1:
                        Color(*self.colors["visited"])
                    else:
                        if (row + col) % 2 == 0:
                            Color(*self.colors["cell_light"])
                        else:
                            Color(*self.colors["cell_dark"])
                    Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

            Color(*self.colors["highlight"])
            for (nx, ny) in self.valid_moves:
                x = origin_x + nx * self.cell_size
                y = origin_y + (self.nivel - 1 - ny) * self.cell_size
                Line(rectangle=(x + dp(2), y + dp(2), self.cell_size - dp(4), self.cell_size - dp(4)), width=dp(4))

        idx = 0
        for row in range(self.nivel):
            for col in range(self.nivel):
                lbl = self.labels[idx]
                x = origin_x + col * self.cell_size
                y = origin_y + (self.nivel - 1 - row) * self.cell_size
                lbl.pos = (x, y)
                lbl.size = (self.cell_size, self.cell_size)
                lbl.font_size = max(dp(12), self.cell_size * 0.35)
                val = self.tablero[row][col]
                lbl.text = str(val) if val != -1 else ""
                lbl.color = self.colors["text"]
                idx += 1

        ks = max(dp(24), self.cell_size * 0.8)
        target_x = origin_x + self.pos_x * self.cell_size + (self.cell_size - ks) / 2
        target_y = origin_y + (self.nivel - 1 - self.pos_y) * self.cell_size + (self.cell_size - ks) / 2
        self.knight.pos = (target_x, target_y)
        self.knight.size = (ks, ks)

        self.canvas.ask_update()
        for lbl in self.labels:
            lbl.canvas.ask_update()
        self.knight.canvas.ask_update()

    def get_cell_at(self, x, y):
        origin_x = self.x + (self.width - min(self.width, self.height)) / 2
        origin_y = self.y + (self.height - min(self.width, self.height)) / 2
        board_size = min(self.width, self.height)
        if not (origin_x <= x <= origin_x + board_size and origin_y <= y <= origin_y + board_size):
            return None
        local_x = x - origin_x
        local_y = y - origin_y
        col = int(local_x // self.cell_size)
        row_from_bottom = int(local_y // self.cell_size)
        row = self.nivel - 1 - row_from_bottom
        if 0 <= col < self.nivel and 0 <= row < self.nivel:
            return (col, row)
        return None

    def on_touch_down(self, touch):
        cell = self.get_cell_at(touch.x, touch.y)
        if not cell:
            return super().on_touch_down(touch)
        col, row = cell
        if (col, row) in self.valid_moves:
            self.movimiento_actual += 1
            self.tablero[row][col] = self.movimiento_actual
            self.visited.add((col, row))
            self.animate_knight_to(col, row)
        else:
            self.show_popup("Movimiento inválido", "No puedes mover ahí.")
        return True

    def animate_knight_to(self, col, row):
        ks = max(dp(24), self.cell_size * 0.8)
        origin_x = self.x + (self.width - min(self.width, self.height)) / 2
        origin_y = self.y + (self.height - min(self.width, self.height)) / 2
        target_x = origin_x + col * self.cell_size + (self.cell_size - ks) / 2
        target_y = origin_y + (self.nivel - 1 - row) * self.cell_size + (self.cell_size - ks) / 2
        dist = abs(col - self.pos_x) + abs(row - self.pos_y)
        duration = max(0.06, 0.07 * dist)
        anim = Animation(pos=(target_x, target_y), duration=duration, t="out_quad")

        def _on_complete(animation, widget):
            self.pos_x = col
            self.pos_y = row
            self.compute_valid_moves()
            self._update_board()
            total = self.nivel * self.nivel
            if self.movimiento_actual == total:
                self.show_level_completed()
            elif not self.valid_moves:
                self.show_game_over()

        anim.bind(on_complete=_on_complete)
        anim.start(self.knight)

    def show_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint=(1, None), height=dp(40))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(dp(320), dp(180)))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_game_over(self):
        content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        content.add_widget(Label(text="No quedan movimientos válidos."))
        btns = BoxLayout(size_hint=(1, None), height=dp(44), spacing=dp(8))
        b_re = Button(text="Reiniciar nivel")
        b_close = Button(text="Salir")
        btns.add_widget(b_re)
        btns.add_widget(b_close)
        content.add_widget(btns)
        popup = Popup(title="😢 Fin del juego", content=content, size_hint=(None, None), size=(dp(360), dp(200)))
        b_re.bind(on_release=lambda *_: (popup.dismiss(), self.rebuild_board()))
        b_close.bind(on_release=lambda *_: App.get_running_app().stop())
        popup.open()

    def show_level_completed(self):
        content = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        content.add_widget(Label(text=f"¡Completaste el tablero {self.nivel}x{self.nivel}!"))
        hb = BoxLayout(size_hint=(1, None), height=dp(44), spacing=dp(8))
        b_next = Button(text="Siguiente nivel")
        b_exit = Button(text="Salir")
        hb.add_widget(b_next)
        hb.add_widget(b_exit)
        content.add_widget(hb)
        popup = Popup(title="¡Nivel completado!", content=content, size_hint=(None, None), size=(dp(380), dp(220)))

        def seguir(*a):
            popup.dismiss()
            self.rebuild_board(nivel=self.nivel + 1)

        def salir(*a):
            popup.dismiss()
            App.get_running_app().stop()

        b_next.bind(on_release=seguir)
        b_exit.bind(on_release=salir)
        popup.open()

    def rebuild_board(self, nivel=None):
        if nivel is not None:
            self.nivel = nivel
        # eliminar widgets hijos existentes para labels y knight
        for child in list(self.children):
            if isinstance(child, Label) or isinstance(child, Image):
                self.remove_widget(child)
        self.labels = []
        self.tablero = [[-1 for _ in range(self.nivel)] for _ in range(self.nivel)]
        self.movimiento_actual = 1
        self.pos_x = 0
        self.pos_y = 0
        self.tablero[self.pos_y][self.pos_x] = 1
        self.visited = {(self.pos_x, self.pos_y)}

        for _ in range(self.nivel * self.nivel):
            lbl = Label(text="", halign="center", valign="middle", size_hint=(None, None))
            lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (inst.width, inst.height)))
            lbl.color = self.colors["text"]
            self.add_widget(lbl)
            self.labels.append(lbl)

        ruta = os.path.abspath("caballo.png")
        if os.path.exists(ruta):
            self.knight = Image(source=ruta, allow_stretch=True, keep_ratio=True, size_hint=(None, None))
        else:
            self.knight = Label(text="♞", font_size=dp(32), size_hint=(None, None), bold=True)
        self.knight.size = (dp(40), dp(40))
        self.add_widget(self.knight)

        self.compute_valid_moves()
        self._update_board()

class GameRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        topbar = BoxLayout(size_hint=(1, None), height=dp(56), padding=dp(6), spacing=dp(6))
        self.btn_reiniciar = Button(text="🔄 Reiniciar nivel", size_hint=(None, 1), width=dp(160))
        self.btn_modo = Button(text="🌙 Modo Claro", size_hint=(None, 1), width=dp(160))
        topbar.add_widget(self.btn_reiniciar)
        topbar.add_widget(self.btn_modo)
        topbar.add_widget(Widget())  # filler

        self.add_widget(topbar)

        self.board = BoardWidget(nivel=5, size_hint=(1, 1))
        self.add_widget(self.board)

        self.btn_reiniciar.bind(on_release=lambda *_: self.board.rebuild_board())
        self.btn_modo.bind(on_release=self.toggle_mode)

        self.board.set_mode("dark")

    def toggle_mode(self, *a):
        new_mode = "light" if self.board.mode == "dark" else "dark"
        self.board.set_mode(new_mode)
        self.btn_modo.text = "☀️ Modo Oscuro" if new_mode == "light" else "🌙 Modo Claro"

class TourCaballoApp(App):
    def build(self):
        Window.size = (820, 860)
        return GameRoot()

if __name__ == "__main__":
    TourCaballoApp().run()
