import sqlite3
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.snackbar import Snackbar



class ContentEdit(MDBoxLayout):
    pass


class MyPlace(MDGridLayout):
    conn = sqlite3.connect("mzucans.db")
    sql_stm = "select place_name from places where description='custom' order by place_name asc;"
    app = MDApp.get_running_app()
    dialog = None
    edit_text = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3
        self.adaptive_height = True
        data = self.conn.execute(self.sql_stm)
        for i in data:
            get_list = OneLineListItem(text=str(i[0]))
            get_list.divider = None
            edit_icon = MDIconButton(
                icon="pen",
                pos_hint={"center_x": .9},
                size=[20, 20],
                user_font_size="14sp"
            )
            delete_icon = MDIconButton(
                icon="delete",
                pos_hint={"center_x": .9},
                size=[20, 20],
                user_font_size="14sp"
            )
            delete_icon.text = edit_icon.text = str(i[0])
            get_list.bind(on_release=self.show)
            delete_icon.bind(on_release=self.delete_place_dialog)
            edit_icon.bind(on_release=self.edit_place_dialog)
            self.add_widget(get_list)
            self.add_widget(edit_icon)
            self.add_widget(delete_icon)

    def show(self, instance):
        data = self.conn.execute("select x,y from places where place_name='%s'" % instance.text)
        for i in data:
            lat = i[0]
            lon = i[1]

        app = MDApp.get_running_app()
        app.root.ids.map.center_on(lat, lon)
        app.root.ids.map.zoom = 20
        app.root.ids.screen_manager.current = "map"

    def edit_place_dialog(self, instance):
        app = MDApp.get_running_app()
        edit_btn = MDFlatButton(
            text="EDIT", text_color=app.theme_cls.primary_color
        )
        cancel_btn = MDFlatButton(
            text="CANCEL", text_color=app.theme_cls.primary_color
        )
        edit_btn.msg = instance.text
        cancel_btn.bind(on_release=self.cancel_dialog)
        edit_btn.bind(on_release=self.edit_place)
        self.dialog = MDDialog(
            type="custom",
            content_cls=ContentEdit(),
            size_hint=[.8, .5],
            buttons=[
                cancel_btn, edit_btn,
            ]
        )
        self.dialog.open()

    def edit_place(self, instance):
        app = MDApp.get_running_app()
        data = app.connection.execute("select place_name from places where place_name = '%s'" % app.edit_place_text)
        check_name = None
        for rows in data:
            check_name = rows[0]

        if check_name == app.edit_place_text:
            Snackbar(text="Place exists", duration=2).show()
        else:
            sql_stmt = f"UPDATE places SET place_name='{app.edit_place_text}' WHERE place_name='{instance.msg}'"
            app.connection.execute(sql_stmt)
            app.connection.commit()
            self.clear_widgets()
            self.__init__()
            self.dialog.dismiss()
            Snackbar(text=f" {instance.msg} changed to {app.edit_place_text}", duration=2).show()

    def delete_place_dialog(self, instance):
        app = MDApp.get_running_app()
        delete_btn = MDFlatButton(
                    text="DELETE", text_color=app.theme_cls.primary_color
                )
        cancel_btn = MDFlatButton(
                    text="CANCEL", text_color=app.theme_cls.primary_color
                )
        delete_btn.msg = instance.text
        cancel_btn.bind(on_release=self.cancel_dialog)
        delete_btn.bind(on_release=self.delete_place)
        self.dialog = MDDialog(
            text=f"Delete {instance.text} from my places?",
            size_hint=[.8, .8],
            buttons=[
                 cancel_btn, delete_btn,
            ],
        )
        self.dialog.open()

    def delete_place(self, instance):
        app = MDApp.get_running_app()
        app.connection.execute("Delete from places where place_name = '%s'" % instance.msg)
        app.connection.commit()
        self.clear_widgets()
        self.__init__()
        self.dialog.dismiss()
        Snackbar(text=f"Deleted {instance.msg} from my places", duration=2).show()

    def cancel_dialog(self, instance):
        self.dialog.dismiss()



class Academic(MDBoxLayout):
    conn = sqlite3.connect("mzucans.db")
    sql_stm = "select place_name from places where description='class' order by place_name asc;"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        data = self.conn.execute(self.sql_stm)
        for i in data:
            get_list = OneLineListItem(text=str(i[0]))
            get_list.bind(on_press=self.show)
            self.add_widget(get_list)

    def show(self, instance):
        data = self.conn.execute("select x,y from places where place_name='%s'" % instance.text)
        for i in data:
            lat = i[0]
            lon = i[1]

        app = MDApp.get_running_app()
        app.root.ids.map.center_on(lat, lon)
        app.root.ids.map.zoom = 20
        app.root.ids.screen_manager.current = "map"


class Administrative(MDBoxLayout):
    conn = sqlite3.connect("mzucans.db")
    sql_stm = "select place_name from places where description='administration' order by place_name asc;"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        data = self.conn.execute(self.sql_stm)
        for i in data:
            get_list = OneLineListItem(text=str(i[0]))
            get_list.bind(on_press=self.show)
            self.add_widget(get_list)

    def show(self, instance):
        data = self.conn.execute("select x,y from places where place_name='%s'" % instance.text)
        for i in data:
            lat = i[0]
            lon = i[1]

        app = MDApp.get_running_app()
        app.root.ids.map.center_on(lat, lon)
        app.root.ids.map.zoom = 20
        app.root.ids.screen_manager.current = "map"


class Faculty(MDBoxLayout):
    conn = sqlite3.connect("mzucans.db")
    sql_stm = "select place_name from places where description='faculty' order by place_name asc;"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        data = self.conn.execute(self.sql_stm)
        for i in data:
            get_list = OneLineListItem(text=str(i[0]))
            get_list.bind(on_press=self.show)
            self.add_widget(get_list)

    def show(self, instance):
        data = self.conn.execute("select x,y from places where place_name='%s'" % instance.text)
        for i in data:
            lat = i[0]
            lon = i[1]

        app = MDApp.get_running_app()
        app.root.ids.map.center_on(lat, lon)
        app.root.ids.map.zoom = 20
        app.root.ids.screen_manager.current = "map"


class Department(MDBoxLayout):
    conn = sqlite3.connect("mzucans.db")
    sql_stm = "select place_name from places where description='department' order by place_name asc;"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        data = self.conn.execute(self.sql_stm)
        for i in data:
            get_list = OneLineListItem(text=str(i[0]))
            get_list.bind(on_press=self.show)
            self.add_widget(get_list)

    def show(self, instance):
        data = self.conn.execute("select x,y from places where place_name='%s'" % instance.text)
        for i in data:
            lat = i[0]
            lon = i[1]

        app = MDApp.get_running_app()
        app.root.ids.map.center_on(lat, lon)
        app.root.ids.map.zoom = 20
        app.root.ids.screen_manager.current = "map"


class PlacePage(MDGridLayout):
    def __init__(self, **kwargs):
        super(PlacePage, self).__init__(**kwargs)
        self.add_widget(
            MDExpansionPanel(
                icon="files/icons/map_place.png",
                content=MyPlace(),
                panel_cls=MDExpansionPanelOneLine(
                    text="My Places"
                )
            )
        )
        self.add_widget(
            MDExpansionPanel(
                icon="files/icons/presentation.png",
                content=Academic(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Classes"
                )
            )
        )
        self.add_widget(
            MDExpansionPanel(
                icon="files/icons/budget.png",
                content=Administrative(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Administration"
                )
            )
        )
        self.add_widget(
            MDExpansionPanel(
                icon="files/icons/faculty.png",
                content=Faculty(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Faculty"
                )
            )
        )
        self.add_widget(
            MDExpansionPanel(
                icon="files/icons/department.png",
                content=Department(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Department"
                )
            )
        )
        self.add_widget(
            MDExpansionPanel(
                icon="files/icons/mental-health.png",
                content=MyPlace(),
                panel_cls=MDExpansionPanelOneLine(
                    text="Others"
                )
            )
        )

