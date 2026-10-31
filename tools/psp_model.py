"""Allège le modèle PSP pour le web : textures 1024 px en WebP, sol retiré. Une seule passe, résultat versionné dans model/psp.glb.
Usage : python tools/psp_model.py chemin/vers/sony_psp.glb"""
import io
import json
import struct
import sys
from pathlib import Path

from PIL import Image

src, out = Path(sys.argv[1]), Path(__file__).parent.parent / "model/psp.glb"
data = src.read_bytes()
n = struct.unpack("<I", data[12:16])[0]
gltf = json.loads(data[20:20 + n])
bin_ = data[20 + n + 8:]

# le sol fourni avec le modèle ne sert pas ici : on retire son nœud, sa géométrie reste ignorée à la lecture
for node in gltf["nodes"]:
    if "children" in node:
        node["children"] = [c for c in node["children"] if gltf["nodes"][c].get("name") != "ground"]

views = gltf["bufferViews"]
blobs = [bin_[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]] for v in views]
for img in gltf["images"]:
    i = img["bufferView"]
    pic = Image.open(io.BytesIO(blobs[i]))
    if pic.width < 64:  # masque du sol
        continue
    pic.load()
    pic = pic.convert("RGB")
    pic.thumbnail((1024, 1024))
    buf = io.BytesIO()
    pic.save(buf, "WEBP", quality=82, method=6)
    blobs[i] = buf.getvalue()
    img["mimeType"] = "image/webp"

for tex in gltf["textures"]:
    if gltf["images"][tex["source"]]["mimeType"] == "image/webp":
        tex["extensions"] = {"EXT_texture_webp": {"source": tex.pop("source")}}
gltf["extensionsUsed"] = gltf["extensionsRequired"] = ["EXT_texture_webp"]

packed = b""
for v, blob in zip(views, blobs):
    packed += b"\0" * (-len(packed) % 4)
    v["byteOffset"], v["byteLength"] = len(packed), len(blob)
    packed += blob
packed += b"\0" * (-len(packed) % 4)
gltf["buffers"][0]["byteLength"] = len(packed)

head = json.dumps(gltf, separators=(",", ":")).encode()
head += b" " * (-len(head) % 4)
size = 12 + 8 + len(head) + 8 + len(packed)
out.parent.mkdir(exist_ok=True)
out.write_bytes(struct.pack("<4sII", b"glTF", 2, size) + struct.pack("<I4s", len(head), b"JSON") + head + struct.pack("<I4s", len(packed), b"BIN\0") + packed)
print(out, size)
