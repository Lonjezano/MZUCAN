from kivy.garden.mapview import MapView
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.app import App
from places import MyPlace, PlacePage
from marker import Marker
from kivymd.toast import toast


class ContentMap(MDBoxLayout):
    pass


class MzuniMapView(MapView, TouchBehavior):
    getting_marker_timer = None
    dialog = None
    touch_coordinate = None
    place_name = []

    def on_long_touch(self, touch, *args):
        self.duration_long_touch = 2
        self.touch_coordinate = self.get_latlon_at(touch.pos[0], touch.pos[1])
        toast("let go !!!")
        Clock.schedule_once(self.show_dialog, 3)


    def show_dialog(self, dt):
        self.dialog = MDDialog(
            type="custom",
            size_hint=[.8, .8],
            content_cls=ContentMap()
        )
        self.dialog.open()

    def add_place(self, name, code, *args):
        lat = self.touch_coordinate.lat
        lon = self.touch_coordinate.lon
        app = App.get_running_app()
        app.connection.execute("INSERT into places (place_name,place_code,x,y,description)"
                               "VALUES('%s','%s','%s','%s', 'custom')" % (name, code, lat, lon))

        app.connection.commit()
        app.root.ids.place_scroll.clear_widgets()
        app.root.ids.place_scroll.add_widget(PlacePage())
        print(name, code)

    def start_getting_markers_in_fov(self):
        try:
            self.getting_marker_timer.cancel()

        except:
            pass

        self.getting_marker_timer = Clock.schedule_once(self.get_marker_in_fov, 1)

    def get_marker_in_fov(self, *args):
        # reference to app class
        min_lat, min_lon, max_lat, max_lon = self.get_bbox()
        app = App.get_running_app()
        sql_statement = "SELECT * FROM places WHERE x>%s AND x<%s AND y>%s AND y<%s" \
                        % (min_lat, max_lat, min_lon, max_lon)
        app.conn.execute(sql_statement)
        markers = app.conn.fetchall()
        for place in markers:
            name = place[1]
            if name in self.place_name:
                continue
            else:
                self.add_mark(place)

    def add_mark(self, place):
        # create marker
        lat, lon = place[3], place[4]
        marker = Marker(lat=lat, lon=lon)
        marker.marker_data = place
        # Specify marker
        star_status = marker.marker_data[5]
        place_desc = marker.marker_data[6]

        if star_status == "True":
            marker.source = "files/icons/star.png"
        else:
            marker.source = "files/icons/marker.png"
        """
        elif place_desc == "place":
            marker.source = "files/icons/business_building.png"
        elif place_desc == "my place":
            marker.source = "files/icons/business_building.png"
        elif place_desc == "class":
            marker.source = "files/icons/classroom.png"
        """



        # add marker
        self.add_widget(marker)



        # keep track of marker
        name = place[1]
        self.place_name.append(name)

