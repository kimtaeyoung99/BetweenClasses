from flask import Flask
import sqlite3
import sys

from flask import render_template

app = Flask(__name__)


@app.route("/")
def main():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    sql_query = """
        SELECT
          lecture_room,
          (SELECT
            MIN(start_time)
          FROM timetable AS t2
          WHERE t2.lecture_room = t1.lecture_room
          AND day_of_week = (CASE CAST(strftime('%w', datetime("now", '+9 hours')) AS INTEGER)
            WHEN 1 THEN '월'
            WHEN 2 THEN '화'
            WHEN 3 THEN '수'
            WHEN 4 THEN '목'
            WHEN 5 THEN '금'
          END)
          AND time("now", '+9 hours') <= t2.start_time)
          AS next_time
        FROM (SELECT DISTINCT
          lecture_room
        FROM timetable) AS t1
        WHERE lecture_room != ""
        AND NOT EXISTS (SELECT
          *
        FROM timetable t3
        WHERE day_of_week = (CASE CAST(strftime('%w', datetime("now", '+9 hours')) AS INTEGER)
          WHEN 1 THEN '월'
          WHEN 2 THEN '화'
          WHEN 3 THEN '수'
          WHEN 4 THEN '목'
          WHEN 5 THEN '금'
        END)
        AND time("now", '+9 hours') BETWEEN start_time AND end_time
        AND t1.lecture_room = t3.lecture_room)
        ORDER BY lecture_room;"""

    return render_template("index.html", rooms=c.execute(sql_query))

if __name__ == "__main__":
    app.run("0.0.0.0", port=int(sys.argv[1]))
