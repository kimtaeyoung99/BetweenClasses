import sqlite3


def main():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS timetable")
    c.execute("CREATE TABLE timetable (lecture_room TEXT, day_of_week TEXT, start_time DATETIME, end_time DATETIME)")

    for row in c.execute("SELECT * FROM lecture").fetchall():
        for times in row[3].split():
            # lecture_room, day_of_week, start_time, end_time
            for time, lecture_room in zip(times.split(" "), row[4].split("<br>")):
                print(lecture_room, time[0], time[2:7], time[8:])
                c.execute("INSERT INTO timetable VALUES (?, ?, ?, ?)", (lecture_room, time[0], time[2:7], time[8:]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
