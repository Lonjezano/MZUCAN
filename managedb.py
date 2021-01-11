from kivy.app import App
from kivymd.uix.snackbar import Snackbar
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import time
import os

if platform == "android":
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

# login manager
def login():
    app = App.get_running_app()
    reg = app.root.ids.reg.text
    password = app.root.ids.password.text
    if reg != "" and password != "":

        data = app.conn.execute("select * from student where reg = '%s' " % reg)

        for rows in data:
            user = rows[0]
            first_name = rows[1]
            last_name = rows[2]
            _reg_ = rows[3]
            _pass_ = rows[4]
            user_image = rows[5]

        try:
            if reg == _reg_ and password == _pass_:
                print("allow access")
                print("The user is %s %s " % (first_name, last_name))
                app.root.ids.screen_manager.current = "map"
                app.root.ids.screen_manager.transition.direction = "up"
                with open("files/log/current_user.txt", "w") as f:
                    print(user, file=f)
                    print(first_name, file=f)
                    print(last_name, file=f)
                    print(reg, file=f)
                    print(user_image, file=f, end="")

                app.user_image = user_image
                app.root.ids.account_user_image.icon = user_image
                app.root.ids.profile_user_image.icon = user_image
                app.set_log_session()
                app.set_right_items_icons()
                app.set_settings()
                Snackbar(text="logged in as %s %s" % (first_name, last_name), duration=1).show()

            else:
                print("Access denied")
                #toast("wrong information")
                Snackbar(text="Invalid password", duration=1).show()

        except UnboundLocalError:
            #toast("user does not exist")
            Snackbar(text="User does not exist", duration=1).show()

    else:
        print("empty")
        #toast("fill all fields")
        Snackbar(text="fill all fields",  duration=1).show()


# sign up manager
def sign_up():
    app = App.get_running_app()
    first_name = app.root.ids.first_name.text
    last_name = app.root.ids.surname.text
    reg = app.root.ids.reg_no.text
    user_image = app.root.ids.set_user_image.icon
    password = app.root.ids.confirm_password.text
    data = app.connection.execute("select reg from student where reg ='%s'" % reg)
    for rows in data:
        reg_check = rows[0]

    try:
        if reg == reg_check:
            app.user_check = True

    except:
        if len(password) < 8:
            app.root.ids.screen_manager.current = "sign up"
            Snackbar(text="error password is short", duration=2).show()
        else:
            app.connection.execute(
                "CREATE TABLE IF NOT EXISTS student (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,"
                "firstname Text NOT NULL,"
                " surname TEXT NOT NULL,"
                "reg TEXT NOT NULL,"
                "password TEXT NOT NULL,"
                "user_image text NOT NULL DEFAULT 'account')"
            )
            app.connection.execute("INSERT INTO student(firstname,surname,reg,password,user_image)"
                                   "VALUES('%s','%s','%s','%s','%s')" % (first_name, last_name, reg, password, user_image))
            app.connection.commit()
            Snackbar(text="Account created", duration=2).show()


# class manager
def class_add():
    app = App.get_running_app()
    print(app.user_session)
    class_name = app.root.ids.class_name.text
    day = app.root.ids.day_picker.text
    time = app.root.ids.time_picker.text
    classroom = app.root.ids.classroom_picker.text
    user = app.user_session

    if day == "Monday":
        day_num = 0
    elif day == "Tuesday":
        day_num = 1
    elif day == "Wednesday":
        day_num = 2
    elif day == "Thursday":
        day_num = 3
    elif day == "Friday":
        day_num = 4

    if class_name != "" and day != "" and time != "" and classroom != "":
        app.connection.execute(
            "CREATE TABLE IF NOT EXISTS classes (ID INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,"
            "class TEXT NOT NULL,"
            "day TEXT NOT NULL,"
            "day_id INTEGER NOT NULL,"
            "time TEXT NOT NULL,"
            "time_id INTEGER NOT NULL,"
            "Cname TEXT NOT NULL,"
            "Student_ID TEXT NOT NULL)")
        data = app.connection.execute("select * from classes where Student_ID = '%s'" % user)
        add_condition = True
        for rows in data:
            class_day = rows[2]
            class_time = rows[3]

            if day == class_day and time == class_time:
                add_condition = False

        time_num = str(time).split(":")

        if add_condition:
            app.connection.execute("INSERT INTO classes(class,day,day_id,time,time_id,Cname,Student_ID)"
                                   "VALUES('%s','%s','%s','%s','%s','%s','%s')"
                                   % (class_name, day, day_num, time, time_num[0], classroom, user))
            Snackbar(text="class added", duration=1).show()
            app.clear("class")
        else:
            Snackbar(text="Time slot already exist", duration=2).show()

    else:
        Snackbar(text="Fill all fields", duration=1).show()


def class_delete(data):
    app = App.get_running_app()
    try:
        if not data:
            Snackbar(text="Select class to delete", duration=1).show()
        else:
            for selected in data:
                app.connection.execute("delete from classes where (day = '%s' and time = '%s') and (Student_ID = '%s')"
                                       % (selected[1], selected[2], app.user_session))
            app.remove_list = []
            Snackbar(text="Class deleted", duration=1).show()
    except:
        Snackbar(text="Class delete failed", duration=1).show()

def class_save():
    app = App.get_running_app()
    app.connection.commit()
    Snackbar(text="Saved", duration=1).show()


def class_handler():
    app = App.get_running_app()
    data = app.connection.execute("select place_name from places where description = 'class';")
    container = []
    for rows in data:
        container.append(rows[0])
    return container

def search_handler():
    app = App.get_running_app()
    text = app.root.ids.search_field_picker.text
    data = app.connection.execute(f"select place_name from places where place_name like '%{text}%';")
    container = []

    for rows in data:
        container.append(rows[0])
    return container

def search_result():
    app = App.get_running_app()
    text = app.root.ids.search_field_picker.text
    data = app.connection.execute(f"select x,y from places where place_name = '{text}';")
    points = []
    for rows in data:
        points.append(rows[0])
        points.append(rows[1])
    return points

def change_password(old_pass, new_pass):
    app = App.get_running_app()
    reg = str(app.user_reg).strip()
    data = app.connection.execute("select password from student where reg = '%s';" % reg)
    for rows in data:
        current_pass = rows[0]

    if old_pass == current_pass:
        if len(new_pass) >= 4:
            sql_stmt = f"UPDATE student SET password='{new_pass}' WHERE reg='{reg}'"
            app.connection.execute(sql_stmt)
            app.connection.commit()
            app.password_dialog.dismiss()
            Snackbar(text="Password changed", duration=1).show()
        else:
            Snackbar(text="should at least be 4 char long", duration=1).show()
    else:
        Snackbar(text="Old password is wrong", duration=1).show()

def logout():
    app = App.get_running_app()
    with open("files/log/current_user.txt", "w") as log:
        log.truncate(0)



    app.set_log_session()
    app.set_settings()
    app.set_right_items_icons()
    app.root.ids.profile_user_image.icon = "account"
    app.root.ids.screen_manager.current = "map"





"""
conn = sqlite3.connect("mzucans.db")
cursor = conn.cursor()
conn.execute("CREATE TABLE IF NOT EXISTS student (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,"
             "firstname Text NOT NULL, surname TEXT NOT NULL,reg TEXT NOT NULL, password TEXT NOT NULL)")
conn.commit()
"""
