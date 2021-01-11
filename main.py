from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.metrics import cm, dp
from kivymd.uix.datatables import MDDataTable
from kivy.clock import Clock
from kivy.core.window import Window
from mzunimapview import MzuniMapView
from places import PlacePage
from gpshelper import GpsHelper
from kivymd.uix.snackbar import Snackbar
from fpdf import FPDF
from kivy.utils import platform
import sqlite3
import managedb
import os


class AccountPassword(MDBoxLayout):
    pass

class ContentDelete(MDBoxLayout):
    pass

class ItemConfirm(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False


class MainAPP(MDApp):
    header = None
    field_check = False
    user_check = False
    user_session = None
    user_name = None
    user_reg = None
    user_image = "account"
    password_dialog = None
    delete_dialog = None
    edit_place_text = None
    remove_list = []
    ref_marker = None
    end_lat = None
    end_lon = None
    connection = None  # database connection
    conn = None  # cursor
    theme_option = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self._finish_init)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.picker_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            previous=True,
        )
        self.profile_image_picker = MDFileManager(
            exit_manager=self.exit_picker,
            select_path=self.select_image,
            previous=True,
        )

        self.table = None

    def _finish_init(self, dt):

        day_menu_items = [
            {"icon": "git", "text": "Monday"},
            {"icon": "git", "text": "Tuesday"},
            {"icon": "git", "text": "Wednesday"},
            {"icon": "git", "text": "Thursday"},
            {"icon": "git", "text": "Friday"},

        ]
        self.day_menu = MDDropdownMenu(
            caller=self.root.ids.day_picker,
            items=day_menu_items,
            callback=self.set_day,
            width_mult=4,
        )


        class_menu_items = [{"icon": "git", "text": f"{i}"} for i in managedb.class_handler()]
        self.class_menu = MDDropdownMenu(
            caller=self.root.ids.classroom_picker,
            items=class_menu_items,
            callback=self.set_classroom,
            width_mult=4
        )

        time_menu_items = [{"icon": "git", "text": f"{i}:45"} for i in range(7, 19)]
        self.time_menu = MDDropdownMenu(
            caller=self.root.ids.time_picker,
            items=time_menu_items,
            callback=self.set_time,
            width_mult=4,
        )

    def on_start(self):



        # intialize Gps
        GpsHelper().run()

        # connect to database
        self.connection = sqlite3.connect("mzucans.db")
        self.conn = self.connection.cursor()
        self.set_log_session()
        self.set_right_items_icons()
        self.load_settings()
        self.set_settings()

        # splash screen timer
        #Clock.schedule_once(self.splash_screen, 8)

    def set_log_session(self):
        try:
            with open("files/log/current_user.txt", "r") as log:
                text = log.readlines()
                self.user_session = text[0]
                self.user_name = f"{text[1]} {text[2]}"
                self.root.ids.account_user_name.text = self.user_name
                self.user_reg = text[3]
                self.root.ids.account_reg_no.text = self.user_reg
                self.user_image = text[4]
                self.root.ids.account_user_image.icon = self.user_image
                self.root.ids.profile_user_image.icon = self.user_image
                self.data_table_handler("show")
                Snackbar(text=f"welcome {self.user_name}", duration=3).show()

        except:
            pass

    def load_settings(self):
        store = JsonStore('files/log/settings.json')
        if store.exists('settings'):
            self.root.ids.class_switch.active = store.get('settings')['class_state']
            self.root.ids.map_switch.active = store.get('settings')['map_state']



    def set_day(self, instance):
        self.root.ids.day_picker.text = instance.text
        self.day_menu.dismiss()

    def set_time(self, instance):
        self.root.ids.time_picker.text = instance.text
        self.time_menu.dismiss()

    def set_classroom(self, instance):
        self.root.ids.classroom_picker.text = instance.text
        self.class_menu.dismiss()

    def splash_screen(self, *args):
        self.root.ids.screen_manager.current = "map"

    # back button that returns user to map
    def account_action_button(self):
        self.root.ids.screen_manager.current = "account"
        self.root.ids.screen_manager.transition.direction = "up"

    def log_action_button(self):
        self.root.ids.screen_manager.current = "login"
        self.root.ids.screen_manager.transition.direction = "up"

    def setting_action_button(self):
        self.root.ids.screen_manager.current = "settings"
        self.root.ids.screen_manager.transition.direction = "up"

    def class_attendance_check(self, name, room):
        data = self.connection.execute("select x,y from places where place_name='%s'" % room)
        for row in data:
            class_lat = row[0]
            class_lon = row[1]
        try:
            gps_blinker = self.root.ids.map.ids.blinker
            if class_lat == gps_blinker.lat and class_lon == gps_blinker.lon:
                self.connection.execute("INSERT INTO attendance (Class, Date, Status) "
                                        "VALUES ('%s', datetime('now','localtime'), 'Attended');" % name)
                self.connection.commit()
            elif class_lat > (gps_blinker.lat - 0.003) and class_lat < (gps_blinker.lat + 0.003):
                if class_lon > (gps_blinker.lon - 0.003) and class_lon < (gps_blinker.lon + 0.003):
                    self.connection.execute("INSERT INTO attendance (Class, Date, Status) "
                                            "VALUES ('%s', datetime('now','localtime'), 'Attended');" % name)
                    self.connection.commit()
                else:
                    self.connection.execute("INSERT INTO attendance (Class, Date, Status) "
                                            "VALUES ('%s', datetime('now','localtime'), 'Absent');" % name)
                    self.connection.commit()
            else:
                self.connection.execute("INSERT INTO attendance (Class, Date, Status) "
                                        "VALUES ('%s', datetime('now','localtime'), 'Absent');" % name)
                self.connection.commit()


        except:
            pass

    def create_class_attendance_record(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # open the text file in read mode
        with open("files/log/class_attendance.txt", "w") as f:
            print("Class\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
                  "Date\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tStatus", file=f)

        with open("files/log/class_attendance.txt", 'a') as f:
            data = self.connection.execute("select * from attendance")
            for rows in data:
                print(f"{rows[1]}\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
                      f"{rows[2]}\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
                      f"{rows[3]}", file=f)
                print(f"{rows[1]}\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
                      f"{rows[2]}\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
                      f"{rows[3]}")


        with open("files/log/class_attendance.txt", "r") as f:
            for x in f:
                pdf.cell(200, 10, txt=x, ln=1, align='C')

        # insert the texts in pdf

        # save the pdf with name .pdf
        pdf.output("/storage/emulated/0/Download/Class Attendance.pdf")
        Snackbar(text="Record saved in downloads", duration=2).show()

    def search(self):
        if managedb.search_handler():
            self.root.ids.list_box.height = len(managedb.search_handler())/7 * 366
            for i in managedb.search_handler():
                search_result = OneLineListItem(text=i)
                search_result.divider = None
                search_result.bind(on_release=self.set_search)
                self.root.ids.list_box.add_widget(search_result)

        if not managedb.search_handler():
            self.root.ids.list_box.height = 100
            null = MDLabel(text="not found", halign="center", valign="top")
            self.root.ids.list_box.add_widget(null)

    def set_search(self, instance):
        self.root.ids.search_btn.opacity = 1
        self.root.ids.search_field_picker.text = instance.text
        self.root.ids.search_btn.disabled = False
        self.root.ids.search_btn.bind(on_release=self.search_center)


    def search_center(self, *args):
        points = managedb.search_result()
        self.root.ids.map.center_on(points[0], points[1])
        self.root.ids.map.zoom = 24
        self.root.ids.screen_manager.current = "map"
        self.root.ids.screen_manager.transition.direction = "down"

    def search_chip(self, instance, value):
        self.root.ids.list_box.clear_widgets()
        data = self.connection.execute("select place_name from places where description = '%s';" % value)
        height = 0


        for i in data:
            search_result = OneLineListItem(text=i[0])
            height = height + 1
            search_result.divider = None
            search_result.bind(on_release=self.set_search)
            self.root.ids.list_box.add_widget(search_result)
        self.root.ids.list_box.height = (height + 1) / 7 * 366

    def back(self):
        if self.root.ids.screen_manager.current == "settings":
            self.root.ids.screen_manager.current = "map"
            self.root.ids.screen_manager.transition.direction = "down"
        elif self.root.ids.screen_manager.current == "search":
            self.root.ids.screen_manager.current = "map"
            self.root.ids.screen_manager.transition.direction = "down"
        elif self.root.ids.screen_manager.current == "login":
            self.root.ids.screen_manager.current = "map"
            self.root.ids.screen_manager.transition.direction = "down"
            self.clear("login")
        elif self.root.ids.screen_manager.current == "sign up":
            self.root.ids.screen_manager.current = "login"
            self.root.ids.screen_manager.transition.direction = "down"
            self.clear("signup")
        elif self.root.ids.screen_manager.current == "class":
            self.root.ids.screen_manager.current = "settings"
            self.root.ids.screen_manager.transition.direction = "down"
            self.clear("class")
        else:
            self.root.ids.screen_manager.current = "settings"
            self.root.ids.screen_manager.transition.direction = "down"

# customization.........................................................................................................
        # Home right action items
    def set_settings(self):
        try:
            if os.path.getsize("files/log/current_user.txt") != 0:
                with open("files/log/current_user.txt", "r") as log:
                    if log:
                        self.root.ids.account_access.disabled = False
                        self.root.ids.notification_access.disabled = False
                        self.root.ids.class_access.disabled = False
                        self.root.ids.logout.disabled = False
                        self.root.ids.logout.opacity = 1
            else:
                self.root.ids.account_access.disabled = True
                self.root.ids.notification_access.disabled = True
                self.root.ids.class_access.disabled = True
                self.root.ids.logout.disabled = True
                self.root.ids.logout.opacity = 0

        except FileNotFoundError:
            self.root.ids.account_access.disabled = True
            self.root.ids.notification_access.disabled = True
            self.root.ids.class_access.disabled = True

    def set_right_items_icons(self):
        try:
            if os.path.getsize("files/log/current_user.txt") != 0:
                with open("files/log/current_user.txt", 'r') as log:
                    if log:
                        self.root.ids.hometool.right_action_items = [
                            [self.user_image, lambda x: self.account_action_button()],
                            ['magnify', lambda x: self.search_animation()],
                            ['settings', lambda x: self.setting_action_button()]
                        ]
            else:
                self.root.ids.hometool.right_action_items = [
                    ['login', lambda x: self.log_action_button()],
                    ['magnify', lambda x: self.search_animation()],
                    ['settings', lambda x: self.setting_action_button()],
                ]

        except FileNotFoundError:
            self.root.ids.hometool.right_action_items = [
                ['login', lambda x: self.log_action_button()],
                ['magnify', lambda x: self.search_animation()],
                ['settings', lambda x: self.setting_action_button()],
            ]



    def search_animation(self):
        self.root.ids.screen_manager.current = "search"
        self.root.ids.screen_manager.transition.direction = "up"

    # Enable Dark Theme on app
    def set_theme(self):
        self.dialog = MDDialog(
            title="Theme",
            type="confirmation",
            items=[
                ItemConfirm(text="Light"),
                ItemConfirm(text="Dark")
            ],
            size_hint=[.5, .5],
            buttons=[
                MDFlatButton(
                    text="CANCEL", text_color=self.theme_cls.primary_color, on_release=self.close_dialog
                ),
                MDFlatButton(
                    text="OK", text_color=self.theme_cls.primary_color, on_release=self.set_theme_color
                ),
            ],
        )
        self.dialog.open()

    def set_theme_option(self, option):
        self.theme_option = option

    def set_theme_color(self, *args):
        if self.theme_option == "Dark":
            self.theme_cls.theme_style = "Dark"
        if self.theme_option == "Light":
            self.theme_cls.theme_style = "Light"
        self.dialog.dismiss()

    def close_dialog(self, *args):
        self.dialog.dismiss()
    #chose accent
    def set_accent(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()

    def data_table_handler(self, action):
        if action == "show":
            try:
                data = self.connection.execute("select class,day,time,Cname from classes where Student_ID = '%s'"
                                               % self.user_session)
                self.root.ids.class_delete_btn.disabled = False
                self.root.ids.class_save_btn.disabled = False
                class_list = []
                for rows in data:
                    class_list_data = [(rows[0], rows[1], rows[2], rows[3])]
                    class_list.append(class_list_data[0])
                self.table = MDDataTable(
                    rows_num=20,

                    column_data=[

                        ("Class", dp(20)),
                        ("Day", dp(15)),
                        ("Time", dp(15)),
                        ("Classroom", dp(18))
                    ],
                    row_data=class_list
                )
                if len(class_list) > 0:
                    self.root.ids.table.add_widget(self.table)
                    print(class_list)
                    print(len(class_list))

                elif len(class_list) == 0:
                    self.root.ids.table.clear_widgets()
                    self.root.ids.table.add_widget(MDLabel(text="No classes", halign="center"))
                    self.root.ids.class_delete_btn.disabled = True
                    self.root.ids.class_save_btn.disabled = True

            except sqlite3.OperationalError:
                self.root.ids.table.add_widget(MDLabel(text="No classes", halign="center"))
                self.root.ids.class_delete_btn.disabled = True
                self.root.ids.class_save_btn.disabled = True


        elif action == "Select":
            data = self.connection.execute("select class,day,time,Cname  from classes where Student_ID = '%s'"
                                           % self.user_session)
            class_list = []
            for rows in data:
                class_list_data = [(rows[0], rows[1], rows[2], rows[3])]
                class_list.append(class_list_data[0])
            self.table = MDDataTable(
                size_hint=(1, 1),
                rows_num=20,
                check=True,
                column_data=[
                    ("Class", dp(25)),
                    ("Day", dp(15)),
                    ("Time", dp(15)),
                    ("Classroom", dp(18))
                ],
                row_data=class_list
            )
            self.table.bind(on_check_press=self.check_press)
            self.root.ids.table.add_widget(self.table)


    def check_press(self, instance_table, current_row):
        self.remove_list.append(current_row)
        print(self.remove_list)

    def delete_btn_handler(self, state):
        if state == "Select":
            self.data_table_handler(state)
            self.root.ids.class_delete_btn.text = "Remove"
            self.root.ids.day_picker.disabled = True
            self.root.ids.time_picker.disabled = True
            self.root.ids.classroom_picker.disabled = True
            self.root.ids.class_name.disabled = True
            self.root.ids.class_save_btn.disabled = True
            self.root.ids.class_add_btn.disabled = True
        elif state == "Remove":
            managedb.class_delete(self.remove_list)
            self.data_table_handler("show")
            self.root.ids.class_delete_btn.text = "Select"
            self.root.ids.day_picker.disabled = False
            self.root.ids.time_picker.disabled = False
            self.root.ids.classroom_picker.disabled = False
            self.root.ids.class_name.disabled = False
            self.root.ids.class_save_btn.disabled = False
            self.root.ids.class_add_btn.disabled = False
        elif state == "Cancel":
            self.data_table_handler("show")
            self.root.ids.class_delete_btn.text = "Select"
            self.root.ids.day_picker.disabled = False
            self.root.ids.time_picker.disabled = False
            self.root.ids.classroom_picker.disabled = False
            self.root.ids.class_name.disabled = False
            self.root.ids.class_save_btn.disabled = False
            self.root.ids.class_add_btn.disabled = False


    # Toggle Password on sign in
    def show_password(self):
        state = self.root.ids.pass_check.active
        if state is True:
            self.root.ids.create_password.password = False
            self.root.ids.confirm_password.password = False
        else:
            self.root.ids.create_password.password = True
            self.root.ids.confirm_password.password = True

    def verify_password(self):
        password = self.root.ids.create_password.text
        confirm = self.root.ids.confirm_password.text

        if password == confirm and len(password) != 0:
            self.root.ids.confirm_password.helper_text = "Match"
        elif password != confirm:
            self.root.ids.confirm_password.helper_text = "Mismatch"
        elif len(password) == 0 and len(confirm) == 0:
            self.root.ids.confirm_password.helper_text = ""

    def delete_account_confirmation_dialog(self):
        confirm_btn = MDFlatButton(
            text="DELETE", text_color=self.theme_cls.primary_color
        )
        cancel_btn = MDFlatButton(
            text="CANCEL", text_color=self.theme_cls.primary_color
        )
        cancel_btn.bind(on_release=self.cancel_dialog)
        confirm_btn.bind(on_release=self.delete_account_dialog)
        self.delete_dialog = MDDialog(
            text="Are you sure you want to delete ypur account?",
            size_hint=[.8, .8],
            buttons=[
                cancel_btn, confirm_btn
            ],
        )
        self.delete_dialog.open()

    def delete_account_dialog(self, instance):
        self.delete_dialog.dismiss()
        self.delete_dialog = MDDialog(
            type="custom",
            content_cls=ContentDelete(),
            size_hint=[.8, .5],
        )
        self.delete_dialog.open()

    def cancel_dialog(self, instance):
        self.delete_dialog.dismiss()

    def delete_account(self, passwrd):
        self.delete_dialog.dismiss()
        data = self.connection.execute("select password from student where ID = '%s'" % self.user_session)

        try:
            for rows in data:
                password = rows[0]
            if password == passwrd:
                self.connection.execute("delete from student where ID = '%s'" % self.user_session)
                self.connection.commit()
                Snackbar(text="Account deleted", duration=2).show()
                managedb.logout()

            else:
                Snackbar(text="wrong password", duration=2).show()
                self.delete_dialog.dismiss()
        except:
            Snackbar(text="wrong password error", duration=2).show()
            self.delete_dialog.dismiss()

    def clear(self, page):
        if page == 'class':
            self.root.ids.day_picker.text = ""
            self.root.ids.time_picker.text = ""
            self.root.ids.classroom_picker.text = ""
            self.root.ids.class_name.text = ""

        elif page == "search":
            self.root.ids.search_field_picker.text = ''

        elif page == 'login':
            self.root.ids.reg.text = ""
            self.root.ids.password.text = ""

        elif page == 'signup':
            self.root.ids.first_name.text = ""
            self.root.ids.surname.text = ""
            self.root.ids.reg_no.text = ""
            self.root.ids.create_password.text = ""
            self.root.ids.confirm_password.text = ""



    def change_password(self):
        self.password_dialog = MDDialog(
            type="custom",
            size_hint=[.8, .5],
            content_cls=AccountPassword()
        )
        self.password_dialog.open()

    def file_manager_open(self):
        self.file_manager.show('/storage/emulated/0')  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.root.ids.set_user_image.icon = str(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def profile_image_picker_open(self):
        self.profile_image_picker.show('/storage/emulated/0')  # output manager to the screen
        self.picker_open = True

    def select_image(self, path):
        self.exit_picker()
        self.root.ids.account_user_image.icon = str(path)
        self.root.ids.profile_user_image.icon = str(path)
        self.user_image = str(path)
        self.set_right_items_icons()
        with open("files/log/current_user.txt", "r") as log:
            text = log.readlines()
        text[4] = str(path)
        with open("files/log/current_user.txt", "w") as log:
            log.writelines(text)
        Snackbar(text="Profile picture changed", duration=2).show()


    def exit_picker(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.picker_open = False
        self.profile_image_picker.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
                return True
            elif self.picker_open:
                self.profile_image_picker.back()
                return True
            elif self.root.ids.screen_manager.current == "map":
                return False
            else:
                self.back()
                return True


if __name__ == '__main__':
    MainAPP().run()
