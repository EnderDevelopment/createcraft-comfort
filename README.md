# CreateCraft Comfort Minecraft Modpack

CreateCraft Comfort is a Forge 1.20.1 Minecraft modpack built around Create automation, Create add-ons, Book of Dragons, and practical quality-of-life mods. The pack is generated as a Modrinth `.mrpack` file with compatible mod releases resolved from Modrinth and verified with SHA-512 checksums.

## Install

Requirements:

- Python 3.10 or newer
- Internet access
- A launcher that supports Modrinth modpacks, such as the Modrinth App

1. Download or clone this project.
2. Open a terminal in the project directory.
3. Run:

```bash
python build_pack.py
```

4. Find the generated file at:

```text
dist/dragonworks-create-dragons.mrpack
```

5. Import the `.mrpack` file into the Modrinth App.

The generated pack uses Minecraft 1.20.1 with Forge 47.3.0. The build stops with an error if a required project has no compatible Forge 1.20.1 release.

## Use

1. Launch the imported instance from the Modrinth App.
2. Use Create to build machines, transport systems, and automation.
3. Use Create: Steam 'n' Rails, Create Big Cannons, and Create Crafts & Additions for additional Create mechanics.
4. Use Book of Dragons for the included dragon content.
5. Use JEI and Jade to inspect recipes and information in game.
6. Use JourneyMap for minimap and world map features.
7. Use AppleSkin and Mouse Tweaks for interface and gameplay conveniences.

To customize the pack, edit the `PACK_MODS` list in `build_pack.py` and add or remove Modrinth project slugs that support Forge 1.20.1. Run the build script again to create a fresh package.

---

More Minecraft mod projects by EnderDevelopment: https://github.com/EnderDevelopment

Project page: https://dash.enderdevelopment.com/community/1b2077bb-bc10-419d-b0ee-382e5d7cc77f?utm_source=github&utm_medium=readme&utm_campaign=auto_publish&utm_content=1b2077bb-bc10-419d-b0ee-382e5d7cc77f
