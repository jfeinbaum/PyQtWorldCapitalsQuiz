from wcq import get_legend, get_times
import json

legend = get_legend()
times = get_times()
obj = {}
for country, names in legend.items():
    obj[country] = {"display": names[0],
                    "allowed": tuple(names),
                    "time": times[country]}

obj_json = json.dumps(obj, indent=4)
with open("data.json", "w") as fp:
    fp.write(obj_json)

