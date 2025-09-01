import io
import typing

import PIL.Image

from .gen.texture_pack import TexturePack as RawTexturePack


def get_texture(pack: RawTexturePack, i: int) -> "Texture":
    stream = io.BytesIO(pack.textures[i].image)
    stream.seek(0)
    return Texture(
        pack.texture_headers[i].magic1,
        pack.textures[i].name,
        PIL.Image.open(stream),
    )


class TexturePack(typing.NamedTuple):
    version: int
    textures: typing.List["Texture"]

    @classmethod
    def load(cls, infile: typing.BinaryIO) -> "TexturePack":
        raw = RawTexturePack.from_io(infile)
        return TexturePack(
            raw.version, [get_texture(raw, i) for i in range(raw.num_textures)]
        )


class Texture(typing.NamedTuple):
    magic1: bytes
    name: str
    image: PIL.Image.Image


if __name__ == "__main__":
    pack = TexturePack.load(
        open(
            "C:/Program Files (x86)/Steam/steamapps/common/Crystal Project/Content/Textures/Voxel.dat",
            "rb",
        )
    )
    print(pack)
