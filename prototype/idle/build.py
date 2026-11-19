"""Monta o protótipo em um único HTML (index.html) com a economia e os sprites embutidos.

    python3 prototype/idle/build.py
"""
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPR = HERE.parent.parent / "assets" / "sprites" / "v2"


def data_uri(name):
    return "data:image/png;base64," + base64.b64encode((SPR / name).read_bytes()).decode()


html = (HERE / "template.html").read_text()
html = html.replace("/*ECON*/", (HERE / "econ.js").read_text())
html = html.replace("/*SCENES*/", (HERE / "scenes.js").read_text())
html = html.replace("__ESTAGIOS__", data_uri("plantas_estagios.png"))
html = html.replace("__EQUIP__", data_uri("equipamentos.png"))
html = html.replace("__VASOS__", data_uri("vasos.png"))
import json
rooms = {}
meta = json.loads((SPR / "comodos" / "meta.json").read_text())
for k, m in meta.items():
    n = f"comodos/{int(k):02d}"
    rooms[int(k)] = {"src": data_uri(n + ".png"), "srcS": data_uri(n + "_s.png"), "srcL": data_uri(n + "_l.png"), "meta": m}
html = html.replace("__COMODOS__", json.dumps(rooms))
html = html.replace("__SHIFT__", (SPR / "comodos" / "shift.json").read_text())
(HERE / "index.html").write_text(html)
print("index.html:", len(html) // 1024, "KB")
