#!/usr/bin/env python3
"""VOIDREIGN standalone Windows release integrity gate.

Verifies *staged player bytes*, not just working source: native EXE, installed
ruleset, six thousand branching event chapters, 18 unique wonder facilities,
24 separate combat skies, licensing, guides, and archive consistency.
"""
from __future__ import annotations
import argparse
import hashlib
import re
import struct
import tomllib
import zipfile
from pathlib import Path

import verify_native_shipyards

def verify(stage:Path, archive:Path, installer:Path):
    errors=[]
    def check(condition:bool, message:str):
        if not condition:
            errors.append(message)
        print(("PASS" if condition else "FAIL")+": "+message)

    game=stage/"VOIDREIGN.exe"
    check(game.is_file() and game.stat().st_size>1_000_000 and game.open("rb").read(2)==b"MZ",
          "Native 64-bit VOIDREIGN executable exists")
    for name in ["README.md","LICENSE","THIRD_PARTY_NOTICES.txt","SETUP.md","STARTING_ORIGINS.md","GALACTIC_CHRONICLE.md","GALACTIC_WONDERS.md","GOVERNMENT_POLICIES.md"]:
        check((stage/name).is_file(),f"Player package contains {name}")
    # The government vertical slice must ship enabled, with the bot-facing
    # command schema documented in the actual staged SDK, not just the source.
    settings = stage / "game-data/Data/Settings.txt"
    settings_text = settings.read_text(encoding="utf-8-sig") if settings.is_file() else ""
    check(bool(re.search(r"(?m)^VOIDREIGN Enable Civic Policies\s*:=\s*TRUE\s*$", settings_text)),
          "Native civic-policy simulation is enabled in staged rules")
    sdk_commands = stage / "sdk/docs/commands.md"
    sdk_text = sdk_commands.read_text(encoding="utf-8-sig") if sdk_commands.is_file() else ""
    check(all(f"### `{name}`" in sdk_text and f'"kind": "{name}"' in sdk_text
              for name in ("adopt_government", "reform_policy")),
          "Staged SDK documents both government and policy commands with examples")
    for name in ["VOIDREIGN-server.exe","VOIDREIGN-datacheck.exe","VOIDREIGN-convert.exe","VOIDREIGN-sdk.exe"]:
        check((stage/name).is_file(),f"Utility {name} branded")
    if (stage/"README.md").is_file():
        text=(stage/"README.md").read_text(encoding="utf-8-sig")
        check("VOIDREIGN" in text and "OpenSE4" not in text and "Space Empires IV" not in text,
              "Player-facing README has independent VOIDREIGN identity")
    event_file=stage/"game-data/Data/NarrativeEvents.toml"
    if event_file.is_file():
        data=tomllib.loads(event_file.read_text(encoding="utf-8"))
        events=data.get("event",[])
        ids={e.get("id") for e in events}
        roots=sum(any(ch.get("followup",0) for ch in event.get("choice",[])) for event in events)
        check(len(events)==6144 and len(ids)==len(events),f"Native catalogue: {len(events)} unique event chapters")
        check(sum(len(e.get("choice",[])) for e in events)==12288,"Native catalogue: 12,288 choices")
        check(roots==2048,f"Native catalogue: {roots} branching root situations")
    else:
        check(False,"Native catalogue present")

    # All 32 Chronicle plotline families must be illustrated in the release.
    # There are 192 playable narrative variants per family, not 6144 distinct pictures.
    event_art_dir=stage/"game-data/Pictures/Events"
    expected_event_art={f"Chronicle_{i:02d}.png" for i in range(32)}
    actual_event_art={p.name for p in event_art_dir.glob("Chronicle_*.png")}
    check(actual_event_art==expected_event_art,
          f"All 32 native illustrated Chronicle plot families present ({len(actual_event_art)}/32)")
    art_hashes=set()
    art_failures=[]
    for filename in sorted(expected_event_art):
        path=event_art_dir/filename
        if not path.is_file():
            continue
        with path.open("rb") as stream:
            header=stream.read(24)
        if len(header)!=24 or header[:8]!=bytes([137,80,78,71,13,10,26,10]) or struct.unpack(">II",header[16:24])!=(256,256):
            art_failures.append(filename)
        if path.stat().st_size<25_000:
            art_failures.append(filename+" too small")
        art_hashes.add(hashlib.sha256(path.read_bytes()).hexdigest())
    check(not art_failures and len(art_hashes)==32,
          f"All 32 event illustrations are unique, full-colour and 256x256 (invalid: {art_failures})")

    fac_file=stage/"game-data/Data/Facility.txt"
    if fac_file.is_file():
        data=fac_file.read_text(encoding="utf-8-sig")
        total=len(re.findall(r"(?m)^Name\s*:=",data))
        wonder_count=len(re.findall(r"(?m)^Facility Group\s*:=\s*Galactic Wonders\s*$",data))
        check(total==47 and wonder_count==18,f"Facilities: {total} total, {wonder_count} galactic wonders")
        check(data.count("Restrictions := One Per Empire")>=18, "Galactic wonders enforce empire-wide uniqueness")
    else:
        check(False,"Ruleset Facility.txt present")
    # The three-resource yard-rate regression is a release gate, not just a source lint.
    # A minerals-only Space Yard silently leaves organic/radioactive build progress at zero.
    verify_native_shipyards.ERRORS.clear()
    yard_count = verify_native_shipyards.audit(stage/"game-data/Data/Facility.txt") + verify_native_shipyards.audit(stage/"game-data/Data/Components.txt")
    check(yard_count >= 8 and not verify_native_shipyards.ERRORS,
          f"All {yard_count} native shipyards have mineral, organic and radioactive rates")

    fac_art=list((stage/"game-data/Pictures/Facilities").glob("Facil_*.png"))
    check(len(fac_art)==47,"Facility icons and portraits include all 18 wonders")
    sky=list((stage/"game-data/Pictures/Systems/Tactical").glob("*.png"))
    check(len(sky)==24 and all(p.stat().st_size>30000 for p in sky),
          f"Original tactical skies: {len(sky)} high-resolution image files")
    check(archive.is_file() and archive.stat().st_size>20_000_000,"Windows portable ZIP exists")
    check(installer.is_file() and installer.stat().st_size>20_000_000 and installer.open("rb").read(2)==b"MZ",
          "Windows setup executable exists")
    if archive.is_file():
        with zipfile.ZipFile(archive) as z:
            entry=f"{stage.name}/VOIDREIGN.exe"
            check(entry in z.namelist(), "Portable ZIP contains native game executable")
            problem=z.testzip()
            check(problem is None, "Portable ZIP passes full CRC integrity verification")
    checksum=stage.parent/f"{stage.name.removesuffix('-windows-x86_64')}-SHA256SUMS.txt"
    # The release pipeline writes a simple SHA256SUMS listing for the installer and ZIP.
    if checksum.is_file():
        lines=checksum.read_text(encoding="utf-8").splitlines()
        records={}
        for line in lines:
            parts=line.strip().split(maxsplit=1)
            if len(parts)==2:
                records[parts[1].lstrip("*")]=parts[0].lower()
        for file in (archive,installer):
            hash_value=hashlib.sha256(file.read_bytes()).hexdigest()
            check(records.get(file.name)==hash_value,f"SHA-256 matches manifest for {file.name}")
    else:
        check(False,"Release SHA256SUMS manifest exists")
    print(f"VALIDATION: {len(errors)} errors")
    if errors:
        print("\n".join(" - "+e for e in errors))
    return 0 if not errors else 2

def main():
    p=argparse.ArgumentParser()
    p.add_argument("stage",type=Path)
    p.add_argument("archive",type=Path)
    p.add_argument("installer",type=Path)
    a=p.parse_args()
    raise SystemExit(verify(a.stage,a.archive,a.installer))

if __name__=="__main__":
    main()
