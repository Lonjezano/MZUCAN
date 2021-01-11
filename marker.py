from kivy.garden.mapview import MapMarkerPopup
from kivymd.uix.dialog import MDDialog
from kivy.properties import ObjectProperty
from kivy.factory import Factory
from kivymd.uix.button import MDFlatButton
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
import mzunimapview


global place_status


class Marker(MapMarkerPopup):
    # star_status = app.connection.execute("select favorite from places ;")
    custom_sheet = None

    def __init__(self, **kwargs):
        super(Marker, self).__init__(**kwargs)
        self.marker_data = []

    def on_release(self):
        App.get_running_app().header = self.marker_data[1]
        App.get_running_app().ref_marker = self.marker_data
        self.custom_sheet = MDCustomBottomSheet(screen=ContentCustomSheet())
        self.custom_sheet.open()


class ContentCustomSheet(BoxLayout):
    star_dialog = None

    def star(self, ref_point):
        global place_status
        app = App.get_running_app()
        status_data = app.conn.execute("select favorite from places where place_name = '%s';" % ref_point)
        for place_status in status_data:
            pass

        if place_status[0] != "True":
            app.connection.execute("update places set favorite = 'True' where place_name = '%s';" % ref_point)
            app.connection.commit()
            cancel_btn = MDFlatButton(
                text="OK", text_color=app.theme_cls.primary_color
            )
            cancel_btn.bind(on_press=self.cancel)
            self.star_dialog = MDDialog(
                text="Starred changes will appear the next time you run this app",
                size_hint=[.8, .8],
                buttons=[
                    cancel_btn
                ]

            )
            self.star_dialog.open()

        elif place_status[0] == 'True':
            app.connection.execute("update places set favorite = 'False' where place_name = '%s';" % ref_point)
            app.connection.commit()
            cancel_btn = MDFlatButton(
                text="OK", text_color=app.theme_cls.primary_color
            )
            cancel_btn.bind(on_press=self.cancel)
            self.star_dialog = MDDialog(
                text="Unstarred changes will appear the next time you run this app",
                size_hint=[.8, .8],
                buttons=[
                    cancel_btn
                ]

            )
            self.star_dialog.open()

    def cancel(self, instance):
        self.star_dialog.dismiss()



