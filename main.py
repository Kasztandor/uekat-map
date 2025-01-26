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


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_map = None
        self.current_floor = None
        self.scatter = Scatter(do_scale=True, do_translation=True, do_rotation=False)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        self.image = Image(allow_stretch=True, keep_ratio=True)
        self.scatter.add_widget(self.image)

        # Układ nawigacyjny
        self.floor_buttons = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        self.room_scroll = ScrollView(size_hint=(1, 0.2), do_scroll_x=True, do_scroll_y=False)
        self.room_list = GridLayout(cols=1, size_hint_y=1, size_hint_x=None, spacing=10, padding=10)
        self.room_list.bind(minimum_width=self.room_list.setter('width'))
        self.room_scroll.add_widget(self.room_list)

        # Główny układ
        self.layout = BoxLayout(orientation="vertical")
        self.layout.add_widget(self.floor_buttons)
        self.layout.add_widget(self.scatter)
        self.layout.add_widget(self.room_scroll)

        self.add_widget(self.layout)

    def _update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def load_map(self, map_data):
        self.current_map = map_data
        self.image.source = map_data["png_file"]
        self.image.reload()

        # Resetowanie scattera
        self.scatter.scale = 1
        self.scatter.center = self.center

        self.update_floor_buttons()
        self.current_floor = map_data.get("map", [])[0] if map_data.get("map") else None

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
        if 'png' in floor:
            self.image.source = floor["png"]
            self.image.reload()
        else:
            print("Brak klucza 'png' w danym piętrze.")

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
