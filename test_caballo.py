from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import os

class TestApp(App):
    def build(self):
        layout = FloatLayout()

        ruta = os.path.abspath("caballo.png")
        print("Cargando:", ruta)

        caballo = Image(
            source=ruta,
            size_hint=(None, None),
            size=(100, 100),   # 🔹 Fuerzo tamaño fijo
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        layout.add_widget(caballo)

        return layout

if __name__ == "__main__":
    TestApp().run()
