import xml.etree.ElementTree as ET
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout

class MainScreen(Screen):
    def __init__(self, maps, **kwargs):
        super().__init__(**kwargs)
        self.maps = maps
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Przyciski budynków
        for map_data in self.maps:
            button = Button(
                text=map_data["name"],
                size_hint=(1, 0.1),
                on_press=lambda instance, map_data=map_data: self.load_map(map_data),
            )
            layout.add_widget(button)

        self.add_widget(layout)

    def load_map(self, map_data):
        # Przechodzimy do ekranu mapy i ładujemy odpowiednią mapę
        map_screen = self.manager.get_screen("map")
        map_screen.load_map(map_data)
        self.manager.current = "map"


from kivy.uix.anchorlayout import AnchorLayout

class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_map = None
        self.current_floor = None

        # Scatter do obsługi mapy
        self.scatter = Scatter(do_scale=True, do_translation=True, do_rotation=False)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        # Obraz mapy
        self.image = Image(allow_stretch=True, keep_ratio=True, size_hint=(None, None))
        self.scatter.add_widget(self.image)

        # Przyciski pięter
        self.floor_buttons = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)

        # ScrollView z listą sal
        self.room_scroll = ScrollView(size_hint=(1, 0.2), do_scroll_x=True, do_scroll_y=False)
        self.room_list = GridLayout(cols=1, size_hint_y=1, size_hint_x=None, spacing=10, padding=10)
        self.room_list.bind(minimum_width=self.room_list.setter('width'))
        self.room_scroll.add_widget(self.room_list)

        # Główny układ
        self.main_layout = BoxLayout(orientation="vertical")
        self.main_layout.add_widget(self.scatter)
        self.main_layout.add_widget(self.room_scroll)

        # AnchorLayout dla przycisku powrotu
        self.top_layout = AnchorLayout(anchor_x='left', anchor_y='top', size_hint=(1, 1))
        self.back_button = Button(
            text="<-",
            size_hint=(None, None),
            size=(50, 50),
            background_normal="",
            background_color=(0.8, 0.8, 0.8, 1),  # Szary kolor
            color=(0, 0, 0, 1),
            font_size=20,
            border=(16, 16, 16, 16),
        )
        self.back_button.bind(on_press=self.go_back)
        self.top_layout.add_widget(self.back_button)

        # Cały ekran, z podziałem na warstwy
        self.add_widget(self.main_layout)
        self.add_widget(self.floor_buttons)  # Przyciski pięter na wierzchu
        self.add_widget(self.top_layout)  # Przycisk powrotu na samej górze

    def _update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def load_map(self, map_data):
        self.current_map = map_data

        if "png_file" in map_data:
            self.image.source = map_data["png_file"]
            self.image.reload()
            self.adjust_image_size()

        # Resetowanie scattera
        self.scatter.scale = 1
        self.scatter.center = self.center

        self.update_floor_buttons()
        self.current_floor = map_data.get("map", [])[0] if map_data.get("map") else None

    def adjust_image_size(self):
        """
        Automatycznie dopasowuje szerokość mapy do szerokości okna.
        """
        if self.image.texture:
            texture_width, texture_height = self.image.texture.size
            screen_width = self.width

            # Skalowanie obrazu, aby pasował na szerokość ekranu
            scale_factor = screen_width / texture_width
            self.image.size = (texture_width * scale_factor, texture_height * scale_factor)

            # Centrowanie obrazu
            self.image.pos = (0, (self.height - self.image.height) / 2)

    def on_size(self, *args):
        """
        Aktualizacja rozmiaru obrazu przy zmianie rozmiaru okna.
        """
        self.adjust_image_size()

    def update_floor_buttons(self):
        self.floor_buttons.clear_widgets()
        for floor in self.current_map.get("map", []):
            button = Button(
                text=floor["name"],
                on_press=lambda instance, floor=floor: self.load_floor(floor),
            )
            self.floor_buttons.add_widget(button)

    def load_floor(self, floor):
        self.current_floor = floor
        if "png" in floor:
            self.image.source = floor["png"]
            self.image.reload()
            self.adjust_image_size()

        # Resetowanie scattera
        self.scatter.scale = 1
        self.scatter.center = self.center

    def update_room_list(self):
        self.room_list.clear_widgets()
        rooms = sorted(self.current_floor.get("rooms", []), key=lambda x: x["name"])
        for room in rooms:
            button = Button(
                text=room["name"],
                size_hint_x=None,
                width=200
            )
            self.room_list.add_widget(button)

    def go_back(self, instance):
        """
        Obsługa przycisku powrotu. Przejście do ekranu wyboru budynku.
        """
        self.manager.current = "main"


def mapLister():
    # Przykładowe dane map
    maps = [
        {
            "name": "Budynek A",
            "map": [
                {"name": "Parter", "file": "maps/A/0.svg", "png": "maps/A/0.png"},
                {"name": "1", "file": "maps/A/1.svg", "png": "maps/A/1.png"},
                {"name": "2", "file": "maps/A/2.svg", "png": "maps/A/2.png"},
                {"name": "3", "file": "maps/A/3.svg", "png": "maps/A/3.png"}
            ],
            "svg_file": "maps/A/0.svg",
            "png_file": "maps/A/0.png"
        },
        {
            "name": "Budynek B",
            "map": [
                {"name": "-1", "file": "maps/A/n1.svg", "png": "maps/B/n1.png"},
                {"name": "Parter", "file": "maps/A/0.svg", "png": "maps/B/0.png"},
                {"name": "1", "file": "maps/A/1.svg", "png": "maps/B/1.png"},
                {"name": "2", "file": "maps/A/2.svg", "png": "maps/B/2.png"},
                {"name": "3", "file": "maps/A/3.svg", "png": "maps/B/3.png"}
            ],
            "svg_file": "maps/B/0.svg",
            "png_file": "maps/B/0.png"
        },
        {
            "name": "CNTI",
            "map": [
                {"name": "1", "file": "maps/CNTI/1.svg", "png": "maps/CNTI/1.png"},
                {"name": "2", "file": "maps/CNTI/2.svg", "png": "maps/CNTI/2.png"},
                {"name": "3", "file": "maps/CNTI/3.svg", "png": "maps/CNTI/3.png"},
                {"name": "4", "file": "maps/CNTI/4.svg", "png": "maps/CNTI/4.png"},
                {"name": "5", "file": "maps/CNTI/5.svg", "png": "maps/CNTI/5.png"},
                {"name": "6", "file": "maps/CNTI/6.svg", "png": "maps/CNTI/6.png"},
                {"name": "7", "file": "maps/CNTI/7.svg", "png": "maps/CNTI/7.png"}
            ],
            "svg_file": "maps/CNTI/1.svg",
            "png_file": "maps/CNTI/1.png"
        }
    ]
    return maps


class MapApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main", maps=mapLister()))
        sm.add_widget(MapScreen(name="map"))

        return sm


if __name__ == "__main__":
    MapApp().run()
