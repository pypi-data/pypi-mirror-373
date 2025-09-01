import io
import re
import traceback
import typing
import zipfile

import kaitaistruct
import PIL.Image
import PIL.ImageDraw

from . import database, texture_pack
from .gen.entities import Entities
from .gen.map_meta import MapMeta
from .gen.map_region import MapRegion
from .gen.voxels import Voxels
from .gen.world import World as RawWorld
from .gen.world_data import WorldData as RawWorldData


class Vector2(typing.NamedTuple):
    x: float
    y: float


class Vector2Int(typing.NamedTuple):
    x: int
    y: int


class Vector2XZ(typing.NamedTuple):
    x: float
    z: float


class Vector2IntXZ(typing.NamedTuple):
    x: int
    z: int


class Vector3(typing.NamedTuple):
    x: float
    y: float
    z: float


class Vector3Int(typing.NamedTuple):
    x: int
    y: int
    z: int


class World(typing.NamedTuple):
    version: int
    """The world's version number."""

    maps: typing.Dict[str, "Map"]
    """All the maps in this world."""

    wrap: bool
    """The `Wrap` property in the world metadata string."""
    bounds: "WorldBounds"  #
    """The `Bounds.Left`, `Bounds.Right`, `Bounds.Top`, and `Bounds.Bottom` properties in the world metadata string."""
    initial_focus_pos: "Vector3"
    """The `InitialFocusPos.X`, `InitialFocusPos.Y`, and `InitialFocusPos.Z` properties in the world metadata string."""
    dat_gen_id: str
    """The `DatGenID` property in the world metadata string."""
    warp_points: typing.Dict[int, "WarpPoint"]
    """The teleport point information found in the world teleport points string."""
    magic1: bytes
    """Unknown."""
    layers: typing.Dict["Vector2IntXZ", "ChunkLayer"]
    """Chunk layers in this world."""

    @classmethod
    def load(
        cls,
        infile: typing.BinaryIO,
        *,
        process_maps: bool = True,
        process_map_regions: bool = True,
        process_layers: bool = True,
        process_voxels: bool = True,
        process_entities: bool = True,
    ) -> "World":
        maps: typing.Dict[str, Map] = {}
        layers: typing.Dict[Vector2IntXZ, ChunkLayer] = {}

        raw_world = RawWorld.from_io(infile)
        with io.BytesIO(raw_world.data_and_maps) as world_stream:
            world_stream.seek(0)
            with zipfile.ZipFile(world_stream) as world_archive:
                for file in world_archive.namelist():
                    match = re.match(r"^[^/]+.dat$", file)
                    if match:
                        # we are in the world data file
                        with world_archive.open(file) as world_data_stream:
                            raw_wd = RawWorldData.from_io(world_data_stream)

                            metadata_kvs: typing.Dict[str, str] = {}
                            for line in raw_wd.metadata.split("\r\n"):
                                if not line:
                                    continue
                                k, v = line.split("=")
                                metadata_kvs[k] = v

                            coords: typing.Dict[int, WarpPoint] = {}
                            for line in raw_wd.warp_points.split("\r\n"):
                                if not line:
                                    continue
                                ri, rp1, rp2 = line.strip(";").split(":")
                                i = int(ri)
                                p1 = rp1.split(",")
                                p2 = rp2.split(",")
                                coords[i] = WarpPoint(
                                    i,
                                    Vector3Int(*(int(p) for p in p1)),
                                    Vector3Int(*(int(p) for p in p2)),
                                )

                            if not process_layers:
                                continue

                            for raw_layer in raw_wd.layer_infos:
                                layer = ChunkLayer(raw_layer.x, raw_layer.z, {})
                                layers[Vector2IntXZ(raw_layer.x, raw_layer.z)] = layer

                                if not process_entities and not process_voxels:
                                    continue

                                with io.BytesIO(raw_layer.layer) as layer_stream:
                                    layer_stream.seek(0)
                                    with zipfile.ZipFile(layer_stream) as layer_archive:
                                        for file in layer_archive.namelist():
                                            match = re.match(
                                                r"^y(\-?\d+)(e?)\.dat$", file
                                            )
                                            if not match:
                                                print(
                                                    f"warning: found odd file {file} in layer {raw_layer.x}, {raw_layer.z}"
                                                )
                                                continue

                                            y = int(match.group(1))
                                            layer.chunks.setdefault(y, Chunk(y))
                                            chunk = layer.chunks[y]

                                            if match.group(2):
                                                # we are in an entities file
                                                if process_entities:
                                                    with layer_archive.open(
                                                        file
                                                    ) as chunk_stream:
                                                        try:
                                                            chunk.entities = (
                                                                Entities.from_io(
                                                                    chunk_stream
                                                                )
                                                            )
                                                        except (
                                                            kaitaistruct.ValidationFailedError
                                                        ) as e:
                                                            print(
                                                                f"warning: got exception parsing entities file at {raw_layer.x:>3}, {y:>3}, {raw_layer.z:>3}: {type(e).__name__:>32}: {e.src_path or '':>32}: 0x{e.io.pos() or 0:04x}: {e.args[0].split(': ')[-1]}",
                                                                flush=True,
                                                            )
                                                        except (
                                                            kaitaistruct.KaitaiStructError
                                                        ) as e:
                                                            print(
                                                                f"warning: got exception parsing entities file at {raw_layer.x:>3}, {y:>3}, {raw_layer.z:>3}:  {type(e).__name__:>32}: {e.src_path or '':>32}:         {e.args[0].split(': ')[-1]}",
                                                                flush=True,
                                                            )
                                            else:
                                                # we are in a voxels file
                                                if process_voxels:
                                                    with layer_archive.open(
                                                        file
                                                    ) as chunk_stream:
                                                        chunk.voxels = Voxels.from_io(
                                                            chunk_stream
                                                        )

                    if process_maps:
                        match = re.match(r"^map/map_([^/]+)/meta.dat$", file)
                        if match:
                            # we are in a map meta file
                            name = match.group(1)
                            with world_archive.open(file) as map_stream:
                                maps[name] = Map(name, MapMeta.from_io(map_stream), {})

                if process_maps and process_map_regions:
                    for file in world_archive.namelist():
                        match = re.match(
                            r"^map/map_([^/]+)/region_(\-?\d+)_(\-?\d+).dat$", file
                        )
                        if match:
                            # we are in a map region file
                            name = match.group(1)
                            x = int(match.group(2))
                            z = int(match.group(3))
                            with world_archive.open(file) as region_stream:
                                maps[name].regions[Vector2IntXZ(x, z)] = (
                                    MapRegion.from_io(region_stream)
                                )

        return World(
            raw_world.version,
            maps,
            metadata_kvs.get("Wrap") == "True",
            WorldBounds(
                (
                    int(metadata_kvs["Bounds.Left"])
                    if "Bounds.Left" in metadata_kvs
                    else None
                ),
                (
                    int(metadata_kvs["Bounds.Right"])
                    if "Bounds.Right" in metadata_kvs
                    else None
                ),
                (
                    int(metadata_kvs["Bounds.Top"])
                    if "Bounds.Top" in metadata_kvs
                    else None
                ),
                (
                    int(metadata_kvs["Bounds.Bottom"])
                    if "Bounds.Bottom" in metadata_kvs
                    else None
                ),
            ),
            Vector3(
                float(metadata_kvs["InitialFocusPos.X"]),
                float(metadata_kvs["InitialFocusPos.Y"]),
                float(metadata_kvs["InitialFocusPos.Z"]),
            ),
            metadata_kvs.get("DatGenID", ""),
            coords,
            raw_wd.magic1,
            layers,
        )


class WorldBounds(typing.NamedTuple):
    left: typing.Optional[int]
    right: typing.Optional[int]
    top: typing.Optional[int]
    bottom: typing.Optional[int]


class WarpPoint(typing.NamedTuple):
    id: int
    """The ID of the point."""
    point1: Vector3Int
    """The lower bound of the point."""
    point2: Vector3Int
    """The upper bound of the point."""


class Map(typing.NamedTuple):
    name: str
    """Either 'biomeX' or 'world'."""
    metadata: MapMeta
    """Metadata for this map, such as its position and size."""
    regions: typing.Dict[Vector2IntXZ, MapRegion]
    """The regions of this map."""


class ChunkLayer(typing.NamedTuple):
    x: int
    z: int
    chunks: typing.Dict[int, "Chunk"]


class Chunk:
    y: int
    voxels: typing.Optional[Voxels]
    entities: typing.Optional[Entities]

    def __init__(
        self,
        y: int,
        voxels: typing.Optional[Voxels] = None,
        entities: typing.Optional[Entities] = None,
    ) -> None:
        self.y = y
        self.voxels = voxels
        self.entities = entities

    def __repr__(self) -> str:
        return f"Chunk(y={repr(self.y)}, voxels={repr(self.voxels)}, entities={repr(self.entities)})"


def visualize_world_map(content_path: str, world_name: str) -> PIL.Image.Image:
    databases_path = f"{content_path}/Database"

    with open(f"{databases_path}/biome.dat", "rb") as biome_file:
        biome_info = database.load_biomes(biome_file)

    def mapname(rawname: str) -> str:
        match = re.match(r"^biome(\d+)$", rawname)
        if match:
            biome = biome_info[int(match.group(1))]
            if biome:
                return biome.name
        return rawname

    with open(f"{databases_path}/voxel.dat", "rb") as voxel_file:
        voxel_info = database.load_voxels(voxel_file)

    with open(f"{content_path}/Textures/Voxel.dat", "rb") as texture_file:
        texpack = texture_pack.TexturePack.load(texture_file)
    voxel_altas = texpack.textures[10].image
    voxel_size = int(voxel_altas.size[0] / 24)  # 18
    voxel_colors = []
    for i in range(256):
        voxel = voxel_info.get(i)
        if not voxel:
            voxel_colors.append((0, 0, 0, 0))
            continue
        voxel_u = int(voxel.tex_top_u)
        voxel_v = int(voxel.tex_top_v)
        total_color = [0, 0, 0]
        n_pixels = voxel_size * voxel_size
        for x in range(voxel_size):
            for y in range(voxel_size):
                (r, g, b, a) = voxel_altas.getpixel(
                    (voxel_u * voxel_size + x, voxel_v * voxel_size + y)
                )
                total_color[0] += r
                total_color[1] += g
                total_color[2] += b
        avg_color = [int(x / n_pixels) for x in total_color]
        voxel_colors.append((*avg_color, 255))

    with open(f"{content_path}/Worlds/{world_name}.dat", "rb") as world_file:
        world = World.load(world_file, process_voxels=False, process_entities=False)
    worldmap = world.maps["world"]
    worldposx = worldmap.metadata.pos_x
    worldposy = worldmap.metadata.pos_z
    worldsizex = worldmap.metadata.size_x
    worldsizey = worldmap.metadata.size_z

    image = PIL.Image.new("RGBA", (worldsizex, worldsizey))
    draw = PIL.ImageDraw.Draw(image)
    for map in sorted(world.maps.values(), key=lambda m: -m.metadata.pos_y):
        posx = map.metadata.pos_x
        posy = map.metadata.pos_z
        sizex = map.metadata.size_x
        sizey = map.metadata.size_z

        x = posx - worldposx
        y = posy - worldposy

        for rx in range(map.metadata.num_regions_x):
            for ry in range(map.metadata.num_regions_z):
                region = map.regions[Vector2IntXZ(rx, ry)]
                pixels: typing.List[MapRegion.MapPixel] = [x for x in region.map_pixels]
                for px in range(min(64, sizex - rx * 64)):
                    for py in range(min(64, sizey - ry * 64)):
                        colorinfo = pixels.pop(0)
                        color = [*voxel_colors[colorinfo.voxel_id]]
                        color[0] -= colorinfo.water_depth * 8
                        color[1] -= colorinfo.water_depth * 8
                        color[2] += colorinfo.water_depth * 8
                        draw.point(
                            (x + rx * 64 + px, y + ry * 64 + py),
                            (*color,),
                        )

    for map in world.maps.values():
        posx = map.metadata.pos_x
        posy = map.metadata.pos_z
        sizex = map.metadata.size_x
        sizey = map.metadata.size_z

        x = posx - worldposx
        y = posy - worldposy

        draw.text(
            [(x + x + sizex) / 2, (y + y + sizey) / 2],
            mapname(map.name),
            anchor="mm",
            font_size=12,
            fill="#ffffffff",
        )

    return image


if __name__ == "__main__":
    content_path = (
        "C:/Program Files (x86)/Steam/steamapps/common/Crystal Project/Content"
    )

    # image = visualize_world_map(content_path, "field")
    # image.save("map.png")

    with open(f"{content_path}/Worlds/field.dat", "rb") as world_file:
        world = World.load(world_file, process_map_regions=False, process_layers=False)
        for biome in world.maps.values():
            print(
                f"{biome.name:>16}: {biome.metadata.pos_x:>5} {biome.metadata.pos_y:>5} {biome.metadata.pos_z:>5}; {biome.metadata.size_x:<4}x{biome.metadata.size_z:<4}; {biome.metadata.num_regions_x:<2}x{biome.metadata.num_regions_z:<2} ({biome.metadata.size_x * biome.metadata.size_z / 8} bytes in pixels)"
            )
