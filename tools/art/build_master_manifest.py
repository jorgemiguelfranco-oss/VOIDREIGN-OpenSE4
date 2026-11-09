from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GAME=ROOT/"game-data"
SOURCES={
 "component_facility_art":"art-library/voidreign-art-native-components/GENERATION-MANIFEST.json",
 "component_facility_atlases":"art-library/voidreign-art-native-components/ATLAS-MANIFEST.json",
 "faction_ship_art":"art-library/voidreign-art-faction-ships/GENERATION-MANIFEST.json",
 "system_biomes":"art-library/voidreign-art-system-biomes/GENERATION-MANIFEST.json",
 "planet_object_art":"art-library/voidreign-art-planets/GENERATION-MANIFEST.json",
 "faction_leader_portraits":"art-library/voidreign-art-faction-portraits/GENERATION-MANIFEST.json",
 "interface_art":"game-data/VOIDREIGN-UI-ART-MANIFEST.json",
 "original_audio":"game-data/AUDIO-MANIFEST.json",
}
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1<<20),b""):h.update(block)
 return h.hexdigest()
sources={}
for name,relative in SOURCES.items():
 p=ROOT/relative
 if not p.is_file():
  raise SystemExit(f"Missing provenance manifest: {relative}")
 item={"file":relative,"bytes":p.stat().st_size,"sha256":sha(p)}
 payload=json.loads(p.read_text(encoding="utf-8-sig"))
 item["title"]=payload.get("title",name)
 if name=="component_facility_art":
  item["components"]=payload.get("components",0);item["facilities"]=payload.get("facilities",0);item["assets"]=len(payload.get("assets",[]))
 elif name=="component_facility_atlases":
  item["component_cells"]=payload.get("component_atlas",{}).get("count",0)
  item["facility_cells"]=payload.get("facility_atlas",{}).get("count",0)
 elif name=="faction_ship_art":
  item["factions"]=len(payload.get("factions",[]));item["hull_classes"]=len(payload.get("hulls",[]));item["assets"]=len(payload.get("assets",[]))
 elif name=="system_biomes":
  item["biomes"]=len(payload.get("biomes",[]));item["assets"]=len(payload.get("assets",[]));item["system_variants_per_biome"]=payload.get("system_variants_per_biome");item["tactical_tiles_per_biome"]=payload.get("tactical_tile_variants_per_biome")
 elif name=="planet_object_art":
  item["assets"]=len(payload.get("assets",[]))
 elif name=="faction_leader_portraits":
  item["assets"]=len(payload.get("assets",[]))
 elif name=="interface_art":
  item["assets"]=len(payload.get("assets",[]));item["ui"]=payload.get("ui",{})
 elif name=="original_audio":
  item["music_tracks"]=len(payload.get("music",[]));item["sound_effects"]=len(payload.get("sound_effects",[]))
 sources[name]=item
manifest={
 "title":"VOIDREIGN complete original game art and audio manifest",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "project":"VOIDREIGN-OpenSE4",
 "runtime_external_dependencies":[],
 "asset_summary":{
  "component_portraits":49,
  "facility_portraits":29,
  "faction_ship_portraits":72,
  "faction_ship_miniatures":72,
  "faction_leader_portraits":6,
  "planetary_stellar_object_art":16,
  "system_biomes":6,
  "system_scene_variants":24,
  "system_layout_backgrounds":48,
  "tactical_biome_tiles":54,
  "resource_icons":6,
  "status_icons":38,
  "main_menu_buttons":12,
  "order_icons":40,
  "auxiliary_ui_sheets":8,
  "original_music_tracks":3,
  "original_sound_effects":18
 },
 "provenance_manifests":sources,
 "verification":{
  "command":"python tools/art/verify_art_assets.py",
  "expected_result":"zero errors and zero warnings"
 }
}
out=GAME/"VOIDREIGN-ART-MANIFEST.json"
out.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f"Wrote {out}")
print("Manifest sources:",len(sources))
for k,v in sources.items():print(f"{k}: {v['bytes']} bytes sha256={v['sha256']}")
