from kivy.app import App
from jnius import autoclass
from kivy.clock import Clock
from android.runnable import run_on_ui_thread
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
from kivy.core.window import Window


WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
activity = autoclass('org.kivy.android.PythonActivity').mActivity


@run_on_ui_thread
def create_webview(*args):
    app = App.get_running_app()
    gps_blinker = App.get_running_app().root.ids.map.ids.blinker
    webview = WebView(activity)
    settings = webview.getSettings()
    settings.setJavaScriptEnabled(True)
    settings.setUseWideViewPort(True)  # enables viewport html meta tags
    settings.setLoadWithOverviewMode(True)  # uses viewport
    settings.setSupportZoom(True)  # enables zoom
    settings.setBuiltInZoomControls(True)  # enables zoom controls
    wvc = WebViewClient()
    webview.setWebViewClient(wvc)
    activity.setContentView(webview)
    webview.loadUrl(f'https://graphhopper.com/maps/?point='
                    f'{gps_blinker.lat}%2C{gps_blinker.lon}&point={app.end_lat}%2C{app.end_lon}')


class Wv(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)
        Clock.schedule_once(create_webview, 0)

    def on_key(self, window, key, *args):
        if key == 27 or key == 1001:  # the esc key
            App.get_running_app().root.ids.screen_manager.current = "map"



class ServiceApp(Screen):
    def __init__(self, **kwargs):
        super(ServiceApp, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)
        self.name = "webview"

    def start_service(self):
        return Wv()

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key\
            App.get_running_app().root.ids.screen_manager.current = "map"




