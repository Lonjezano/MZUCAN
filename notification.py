from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
import sqlite3
from kivy.clock import Clock
from plyer import notification


def check_class_notification_status(state):
    app = App.get_running_app()
    current_day = datetime.now().weekday()
    current_time = f"{datetime.now().hour}:{datetime.now().minute}"
    hour = current_time.split(":")
    user = app.user_session
    classes = False

    try:
        if current_day >= 4 and int(hour[0]) > 18:
            data = app.connection.execute("select day,time from classes where (day_id >= 0 and time_id > 6)"
                                          " and Student_ID = '%s' ORDER BY day_id DESC,day,time_id DESC" % user)

        else:
            data = app.connection.execute("select day,time from classes where (day_id >= '%s' and time_id > '%s')"
                                          "and Student_ID = '%s' ORDER BY day_id DESC,day,time_id DESC"
                                          % (current_day, hour[0],  user))

        for rows in data:
            day = rows[0]
            slot = rows[1]
            classes = True

        if classes:
            if state:
                notification.notify(
                    title="Mzucan notification",
                    message="Turned class notification on",
                    timeout=1
                )
                notification.notify(
                    title="Mzucan notification",
                    message="Next class is %s at %s" % (day, slot),
                    timeout=1
                )
                store = JsonStore('files/log/settings.json')
                store.put('settings', class_state=True, map_state=app.root.ids.map_switch.active
                          , user=str(app.user_session).strip())
                timer(dt=None)
            else:
                notification.notify(
                    title="Mzucan notification",
                    message="Turned class notification off",
                    timeout=3
                )
                store = JsonStore('files/log/settings.json')
                store.put('settings', class_state=True, map_state=app.root.ids.map_switch.active
                          , user=str(app.user_session).strip())
        else:
            notification.notify(
                title="Mzucan notification",
                message="Turned class notification on",
                timeout=1
            )
            notification.notify(
                title="Mzucan notification",
                message="Add classes to MZUCAN",
                timeout=1
            )
            store = JsonStore('files/log/settings.json')
            store.put('settings', class_state=True, map_state=app.root.ids.map_switch.active
                      , user=str(app.user_session).strip())
    except sqlite3.OperationalError:
        store = JsonStore('files/log/settings.json')
        if store.exists('settings'):
            store.put('settings', class_state=True, map_state=app.root.ids.map_switch.active
                      , user=str(app.user_session).strip())
        notification.notify(
            title="Mzucan notification",
            message="Turned class notification on",
            timeout=1
        )
        notification.notify(
            title="Mzucan notification",
            message="Next class not found, add classes",
            timeout=1
        )



def check_map_notification_status(state):
    app = App.get_running_app()

    if state:
        store = JsonStore('files/log/settings.json')
        store.put('settings', class_state=True, map_state=app.root.ids.map_switch.active
                  , user=str(app.user_session).strip())
        notification.notify(
            title="Mzucan notification",
            # displaying time
            timeout=3,
            ticker="map notification are on"
        )

    else:
        store = JsonStore('files/log/settings.json')
        store.put('settings', class_state=True, map_state=app.root.ids.map_switch.active
                  , user=str(app.user_session).strip())
        notification.notify(
            title="Mzucan notification",
            message="Turned Map notification off",

            # displaying time
            timeout=3
        )


def timer(dt):
    print("thimer has staterd")
    store = JsonStore('files/log/settings.json')
    if store.exists('settings'):
        state = store.get('settings')['class_state']

    app = App.get_running_app()
    current_day = datetime.now().weekday()
    current_time = f"{datetime.now().hour}:{datetime.now().minute}"
    hour = current_time.split(":")
    user = app.user_session
    classes = False

    try:
        if current_day >= 4 and int(hour[0]) > 18:
            data = app.connection.execute("select class,day_id,time_id from classes where (day_id >= 0 and time_id > 6)"
                                          " and Student_ID = '%s' ORDER BY day_id DESC,day,time_id DESC" % user)

        else:
            data = app.connection.execute("select class,day_id,time_id,Cname from classes where"
                                          " (day_id >= '%s' and time_id > '%s')"
                                          "and Student_ID = '%s' ORDER BY day_id DESC,day,time_id DESC"
                                          % (current_day, hour[0], user))

        for rows in data:
            class_name = rows[0]
            day_id = rows[1]
            time_id = rows[2]
            classroom = rows[3]
            classes = True

        if classes:
            if state:
                if current_time == f"{time_id}:30":
                    notification.notify(
                        title="Mzucan notification",
                        app_name=f"MZUCAN",
                        message=f"{class_name} class starts in 30 minutes",
                        timeout=2,
                        ticker="You have a class soon"
                    )
                app.class_attendance_check(class_name, classroom)
                Clock.schedule_once(timer, 3600)

    except:
        pass
