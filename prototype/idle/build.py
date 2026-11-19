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
cen = {}
meta = json.loads((SPR / "cenarios" / "meta.json").read_text())
for k, m in meta.items():
    cen[int(k)] = {"src": data_uri(f"cenarios/{int(k):02d}.png"), "meta": m}
html = html.replace("__CENARIOS__", json.dumps(cen))
(HERE / "index.html").write_text(html)
print("index.html:", len(html) // 1024, "KB")
