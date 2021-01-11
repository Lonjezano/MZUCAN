from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog


class GpsHelper:
    has_centered_map = False

    def run(self):
        # get a reference to gps blinker
        gps_blinker = App.get_running_app().root.ids.map.ids.blinker
        gps_blinker.blink()
        # android permission Request permission on android
        if platform == 'android':
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                else:
                    print("did not get all permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION,
                                 ],
                                callback)
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                                 Permission.READ_EXTERNAL_STORAGE])
            request_permissions([Permission.VIBRATE])
            request_permissions([Permission.INTERNET])
        # configure Gps
        if platform == 'android':
            from plyer import gps
            gps.configure(on_location = self.update_blinker_position,
                          on_status = self.on_auth_status)
            gps.start(minTime=1000, minDistance=0)

    def update_blinker_position(self,*args, **kwargs):

        my_lat = kwargs['lat']
        my_lon = kwargs['lon']
        print("GPs Position", my_lat, my_lon)
        gps_blinker = App.get_running_app().root.ids.map.ids.blinker
        gps_blinker.lat = my_lat
        gps_blinker.lon = my_lon

        # center map on gps
        if not self.has_centered_map:
            map = App.get_running_app().root.ids.map
            map.center_on(my_lat, my_lon)
            map.zoom = 20
            self.has_centered_map = True

    def on_auth_status(self, general_status, status_message):
        if general_status == 'provider-enabled':
            pass
        else:
            self.open_gps_access_popup()

    def open_gps_access_popup(self):
        dialog = MDDialog(title="GPS Error", text="You need to enable gps for app to work correctly")
        dialog.size_hint = [.8,.8]
        dialog.pos_hint = {"center_x": .5, "center_y": .5}
        dialog.open()