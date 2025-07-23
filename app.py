from flask import Flask, render_template, request
from datetime import datetime, timedelta
import math

app = Flask(__name__)

def tribal_wars_distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def calc_travel_time(ax, ay, tx, ty, unit_type, world_speed, unit_speed):
    distance = tribal_wars_distance((ax, ay), (tx, ty))
    unit_speeds = {
        "Ram": 30,
        "Noble": 35,
        "LC": 10,
        "MA": 10
    }
    minutes_per_field = unit_speeds.get(unit_type, 30)
    effective_speed = world_speed * unit_speed
    total_minutes = (distance * minutes_per_field) / effective_speed
    return total_minutes / 60  # hours

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        unit_type = request.form.get("unit_type")
        world_speed = float(request.form.get("world_speed", 1))
        unit_speed = float(request.form.get("unit_speed", 1))
        date = request.form.get("landing_date")
        time = request.form.get("landing_time")
        time_format = "%Y-%m-%d %H:%M:%S" if len(time.split(':')) == 3 else "%Y-%m-%d %H:%M"
        landing = datetime.strptime(f"{date} {time}", time_format)
        attackers = request.form.get("attacker_villages").strip().split("\n")
        targets = request.form.get("target_villages").strip().split("\n")
        simple_format = request.form.get("simple_format") == "on"

        lines = []
        for atk in attackers:
            for tgt in targets:
                ax, ay = map(int, atk.strip().split("|"))
                tx, ty = map(int, tgt.strip().split("|"))
                travel_hours = calc_travel_time(ax, ay, tx, ty, unit_type, world_speed, unit_speed)
                send_time = landing - timedelta(hours=travel_hours)
                dist = tribal_wars_distance((ax, ay), (tx, ty))
                
                if simple_format:
                    lines.append(f"{atk} → {tgt} | {send_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    lines.append(
                        f"🚀 Attack Details\n"
                        f"Attacker: {atk}\n"
                        f"Target: {tgt}\n"
                        f"Distance: {dist:.2f} fields\n"
                        f"Unit Type: {unit_type}\n"
                        f"Send At: {send_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )

        result = "\n\n".join(lines)

    return render_template("index.html", result=result)
    
if __name__ == "__main__":
    app.run(debug=True)

