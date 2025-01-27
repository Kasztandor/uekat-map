from kivy.config import Config
Config.set('kivy', 'clipboard', 'dummy')  # Suppress clipboard warning

import xml.etree.ElementTree as ET
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import os


def extract_text_coordinates(svg_file, group_label="Rooms"):
    # Wczytaj plik SVG
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Namespace SVG i Inkscape
    namespaces = {
        "svg": "http://www.w3.org/2000/svg",
        "inkscape": "http://www.inkscape.org/namespaces/inkscape",
        "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
    }

    # Znajdź grupę z inkscape:label="Rooms"
    group = root.find(f".//svg:g[@inkscape:label='{group_label}']", namespaces)
    if group is None:
        print(f"Nie znaleziono grupy o labelu '{group_label}'")
        return []

    # Lista wyników
    text_coordinates = []

    # Znajdź wszystkie elementy <text> w grupie
    text_elements = group.findall(".//svg:text", namespaces)

    for text in text_elements:
        # Pobierz tekst z <tspan>
        tspan = text.find(".//svg:tspan", namespaces)
        if tspan is not None and tspan.text:
            name = tspan.text.strip()
        else:
            continue  # Pomijamy elementy bez tekstu

        # Pobierz współrzędne `x` i `y`
        x = text.attrib.get("x")
        y = text.attrib.get("y")

        if x is not None and y is not None:
            # Dodaj do listy
            text_coordinates.append({
                "name": name,
                "x": float(x),
                "y": float(y),
            })

    return text_coordinates


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
                {"name": "-1", "file": "maps/B/n1.svg", "png": "maps/B/n1.png"},
                {"name": "Parter", "file": "maps/B/0.svg", "png": "maps/B/0.png"},
                {"name": "1", "file": "maps/B/1.svg", "png": "maps/B/1.png"},
                {"name": "2", "file": "maps/B/2.svg", "png": "maps/B/2.png"},
                {"name": "3", "file": "maps/B/3.svg", "png": "maps/B/3.png"}
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

    # Dodajemy listę pokoi dla każdego piętra
    for map_data in maps:
        for floor in map_data["map"]:
            svg_file = floor["file"]
            if os.path.exists(svg_file):  # Sprawdź, czy plik istnieje
                floor["rooms"] = extract_text_coordinates(svg_file)  # Parsowanie SVG i dodanie pokoi
            else:
                print(f"Plik {svg_file} nie istnieje.")
                floor["rooms"] = []

    return maps


class MainScreen(Screen):
    def __init__(self, maps, **kwargs):
        super().__init__(**kwargs)
        self.maps = maps

        # Główny układ
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Pole wyszukiwania
        self.search_input = TextInput(
            hint_text="Wpisz nazwę sali...",
            size_hint=(1, 0.1),
            multiline=False
        )
        layout.add_widget(self.search_input)

        # Przycisk wyszukiwania
        search_button = Button(
            text="Szukaj",
            size_hint=(1, 0.1),
            on_press=self.search_room
        )
        layout.add_widget(search_button)

        # Etykieta informacyjna
        self.search_result_label = Label(
            text="",
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.search_result_label)

        # Przyciski budynków
        for map_data in self.maps:
            button = Button(
                text=map_data["name"],
                size_hint=(1, 0.1),
                on_press=lambda instance, map_data=map_data: self.load_map(map_data),
            )
            layout.add_widget(button)

        self.add_widget(layout)

    def search_room(self, instance):
        search_term = self.search_input.text.strip().lower().replace(" ", "")
        found = False
        building_name = ""
        floor_name = ""
        room_data = None

        for map_data in self.maps:
            for floor in map_data.get("map", []):
                for room in floor.get("rooms", []):
                    room_name = room["name"].strip().lower().replace(" ", "")
                    if room_name == search_term:
                        # Znaleziono salę, przechodzimy do odpowiedniej mapy i piętra
                        building_name = map_data["name"]
                        floor_name = floor["name"]
                        room_data = room
                        self.load_map(map_data, floor, room_data)
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if found:
            self.search_result_label.text = f"Znaleziono salę: {search_term} w budynku {building_name}, piętro {floor_name}"
        else:
            self.search_result_label.text = "Nie znaleziono sali."

    def load_map(self, map_data, floor=None, room=None):
        # Przechodzimy do ekranu mapy i ładujemy odpowiednią mapę
        map_screen = self.manager.get_screen("map")
        map_screen.load_map(map_data, floor, room)
        self.manager.current = "map"


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_map = None
        self.current_floor = None
        self.current_room = None

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

        # Główny układ
        self.main_layout = BoxLayout(orientation="vertical")
        self.main_layout.add_widget(self.scatter)

        # AnchorLayout dla przycisku powrotu i etykiety
        self.top_layout = AnchorLayout(anchor_x='left', anchor_y='top', size_hint=(1, 1))

        # BoxLayout dla przycisku powrotu i etykiety
        self.top_box = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(300, 50))

        # Przycisk powrotu
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

        # Etykieta z nazwą budynku i piętra
        self.building_label = Label(
            text="",
            size_hint=(None, None),
            size=(250, 50),
            color=(0, 0, 255, 1),
            font_size=18,
            halign="left",
            valign="middle",
        )

        # Dodaj przycisk i etykietę do BoxLayout
        self.top_box.add_widget(self.back_button)
        self.top_box.add_widget(self.building_label)

        # Dodaj BoxLayout do AnchorLayout
        self.top_layout.add_widget(self.top_box)

        # Cały ekran, z podziałem na warstwy
        self.add_widget(self.main_layout)
        self.add_widget(self.floor_buttons)  # Przyciski pięter na wierzchu
        self.add_widget(self.top_layout)  # Przycisk powrotu i etykieta na samej górze

    def _update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def load_map(self, map_data, floor=None, room=None):
        self.current_map = map_data

        # Load the first floor by default if no floor is specified
        if floor is None and map_data.get("map"):
            floor = map_data["map"][0]

        self.load_floor(floor, room)

        self.update_floor_buttons()

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

    def load_floor(self, floor, room=None):
        self.current_floor = floor
        self.current_room = room

        if "png" in floor:
            self.image.source = floor["png"]
            self.image.reload()
            self.adjust_image_size()

        # Resetowanie scattera
        self.scatter.scale = 1
        self.scatter.center = self.center

        # Aktualizacja etykiety z nazwą budynku i piętra
        if self.current_map and self.current_floor:
            self.building_label.text = f"{self.current_map['name']}: {self.current_floor['name']}"

    def go_back(self, instance):
        """
        Obsługa przycisku powrotu. Przejście do ekranu wyboru budynku.
        """
        self.manager.current = "main"


class MapApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main", maps=mapLister()))
        sm.add_widget(MapScreen(name="map"))
        return sm


if __name__ == "__main__":
    MapApp().run()