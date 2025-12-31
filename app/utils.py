import pandas as pd
import geopandas as gpd
import folium as flm
import json, os, random

from folium.plugins import GroupedLayerControl
from branca.colormap import LinearColormap

def createMap(libs_path, count_info, la_map_path):
    libs = pd.read_csv(libs_path)
    la_libs = libs[libs["county"] == "Los Angeles"]
    la_map = gpd.read_file(la_map_path)
    count_names = [count_name for count_name, _, _ in count_info]

    counts = {}
    color_maps = {}
    layers = {}
    counts_group = {}

    m = flm.Map(
        location=[34.117237, -118.23700],
        zoom_start=9,
        min_zoom=9,
        tiles="Cartodb Positron",
        prefer_canvas=True,
        attributionControl=0
    )

    for count_name, count_path, colors in count_info:
        counts[count_name] = pd.read_csv(count_path)
        la_map[count_name] = counts[count_name]["total"].fillna(0)

        color_maps[count_name] = LinearColormap(
            colors=colors,
            vmin=max(la_map[count_name].min(), 0),
            vmax=max(la_map[count_name].max(), 1),
            caption=count_name.replace("_", " ").title()
        )
        # color_maps[count_name].add_to(m)

    la_map_geo = json.loads(la_map.to_json())

    for idx, (count_name, count_path, colors) in enumerate(count_info):
        def construct_style(cmap, field):
            def style(feature):
                value = feature["properties"].get(field, 0)

                if value is None or pd.isna(value):
                    value = 0

                return {
                    "fillColor": cmap(float(value)),
                    "color": cmap(float(value)),
                    "weight": 1.5,
                    "fillOpacity": 1
                }
            return style

        layers[count_name] = flm.GeoJson(
            la_map_geo,
            name=count_name.replace("_", " ").title(),
            style_function=construct_style(color_maps[count_name], count_name),
            highlight_function=lambda x: {
                'fillOpacity': 0.25,
                'weight': 1
            },
            tooltip=flm.GeoJsonTooltip(
                fields=['name'] + count_names,
                aliases=['Area:'] + [name.replace("_", " ").title() + ":" for name in count_names],
                style="background-color: rgb(250, 250, 248); color: #33333"
            )
        )

        fg = flm.FeatureGroup(
            name=count_name.replace("_", " ").title(),
            show=(idx == 0)
        )

        layers[count_name].add_to(fg)
        fg.add_to(m)
        counts_group[count_name.replace("_", " ").title()] = fg

    lib_markers = flm.FeatureGroup(name="Library Locations", show=True)

    for idx, row in la_libs.iterrows():
        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
            flm.Circle(
                location=[row["latitude"], row["longitude"]],
                radius=10,
                tooltip=flm.Tooltip(row.get("library_name", "Library"), max_width=200),
                color="rgb(250, 250, 248)",
                weight=1,
                opacity=1,
                fill=False,
                fill_color="rgb(250, 250, 248)",
                fill_opacity=1,
                z_index_offset=1000
            ).add_to(lib_markers)

    lib_markers.add_to(m)
    m.keep_in_front(lib_markers)

    GroupedLayerControl(
        groups={"Data Layers": list(counts_group.values()),
                "Overlays": [lib_markers]},
        exclusive_groups={"Data Layers": True, "Overlays": False},
        collapsed=False,
    ).add_to(m)

    return m

