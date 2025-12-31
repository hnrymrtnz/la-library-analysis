from flask import *
from app import app

from .utils import *

@app.route("/")
def index():
    count_info = [
        ("libraries", "app/static/data/lib_counts.csv", ["#3F1C00", "#FF7707"]),
        ("population", "app/static/data/pop_counts.csv", ["#163F00", "#4BDA50"]),
        ("english learners", "app/static/data/el_counts.csv", ["#001337", "#076EFF"]),
        (">high school education", "app/static/data/unedu_counts.csv", ["#370033", "#E643CD"]),
        ("college enrollment", "app/static/data/enroll_counts.csv", ["#491010", "#FF2C2C"])
    ]

    if not os.path.exists("app/static/map.html"):
        print("Creating map.")
        m = createMap(
            libs_path="app/static/data/libs.csv", 
            count_info=count_info,
            la_map_path="app/static/data/la_map.json"
        )

        m.save("app/static/map.html")

    libs = pd.read_csv("app/static/data/libs.csv")
    la_libs = libs[libs["county"] == "Los Angeles"].copy()
    la_libs = la_libs.sort_values("library_name")

    return render_template("index.html")