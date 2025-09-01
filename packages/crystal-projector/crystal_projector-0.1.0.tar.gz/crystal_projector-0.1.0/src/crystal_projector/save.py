import datetime
import io
import typing
import zipfile

from .database import JSON
from .gen.bson import Bson
from .gen.database import Database as RawDatabase
from .gen.save import Save as RawSave

LATEST_VERSION = 28


def _bson_to_json_impl(x: Bson.Element) -> JSON:
    if not hasattr(x, "content"):
        return None
    elif type(x.content) in (bool, int, float, str, type(None)):
        return x.content
    elif type(x.content) is Bson:
        if x.type_byte is Bson.Element.BsonType.array:
            return [_bson_to_json_impl(e) for e in x.content.fields.elements]
        else:
            return bson_to_json(x.content)
    elif type(x.content) is Bson.String:
        return x.content.str
    elif type(x.content) in (
        Bson.BinData,
        Bson.CodeWithScope,
        Bson.DbPointer,
        Bson.F16,
        Bson.ObjectId,
        Bson.RegEx,
        Bson.Timestamp,
    ):
        raise Exception(f"Type of BSON {type(x.content)} unsupported: {x.content}")
    else:
        raise Exception(f"Got weird BSON of type {type(x.content)}: {x.content}")


def bson_to_json(x: Bson) -> JSON:
    return {
        typing.cast(Bson.Element, e).name.str: _bson_to_json_impl(e)
        for e in x.fields.elements
    }


class SaveFile(typing.NamedTuple):
    """A parsed Crystal Project `.sav` save file."""

    version: int
    """The version of this save file."""
    magic1: int
    """Unknown."""
    time_played: datetime.timedelta
    """The amount of time this game has been played."""
    magic2: int
    """Unknown."""
    last_played: datetime.datetime
    """The last time this save file was saved to."""
    home_point_name: str
    """The name of the current home point."""
    currency: int
    """The amount of currency the player has, in terms of copper."""
    party_members: typing.List["PartyMemberData"]
    """Information about each party member."""
    magic3: bytes
    """Unknown."""
    mods: typing.List["ModData"]
    """What mods are in use in this save file."""
    json_data: JSON
    """Global JSON save data."""
    maps: typing.Dict[int, RawSave.MapData]
    """Map exploration information."""
    magic4: int
    """Unknown."""
    magic5: bytes
    """Unknown."""
    logs: bytes
    """A log file. TODO: parse this."""

    @classmethod
    def load(cls, infile: typing.BinaryIO) -> "SaveFile":
        """Load a save file from memory."""

        db = RawDatabase.from_io(infile)

        result = io.BytesIO()
        for b in db.database:
            result.write((255 - b).to_bytes(1, "little"))

        if db.version != LATEST_VERSION:
            print(
                f"warning: save file is of unknown version '{db.version}' (expected {LATEST_VERSION})"
            )

        result.seek(0)
        raw_save = RawSave.from_io(result)

        logs = b""
        if raw_save.len_logs > 0:
            with io.BytesIO(raw_save.logs.zipfile) as stream:
                with zipfile.ZipFile(stream) as archive:
                    logs = archive.read("log.dat")

        return SaveFile(
            db.version,
            raw_save.magic1,
            datetime.timedelta(
                hours=raw_save.hours_played,
                minutes=raw_save.minutes_played,
                seconds=raw_save.seconds_played,
            ),
            raw_save.magic2,
            datetime.datetime(
                year=raw_save.year,
                month=raw_save.month,
                day=raw_save.day,
                minute=raw_save.minute,
                hour=raw_save.hour,
                second=raw_save.second,
            ),
            raw_save.location_name.value,
            raw_save.currency,
            [
                PartyMemberData(
                    i,
                    raw_save.party_members[i].name.string.value,
                    raw_save.party_members[i].level,
                    raw_save.party_members[i].gender,
                    raw_save.party_members[i].job,
                    bson_to_json(raw_save.party_data[i]),
                )
                for i in range(raw_save.num_party_members)
            ],
            raw_save.magic3,
            [
                ModData(
                    i,
                    raw_save.mods[i].uuid.value,
                    raw_save.mods[i].name.value,
                    raw_save.mods[i].version.value,
                    raw_save.mods[i].magic1,
                    raw_save.mod_settings[i],
                )
                for i in range(raw_save.num_mods)
            ],
            bson_to_json(raw_save.global_data),
            {map.biome: map for map in raw_save.map_data},
            raw_save.magic4,
            raw_save.magic5,
            logs,
        )


class PartyMemberData(typing.NamedTuple):
    slot: int
    """What slot this party member is in."""
    name: str
    """The name of this party member."""
    level: int
    """The level of this party member."""
    gender: int
    """The ID of the party member's gender."""
    job: int
    """The ID of the party member's job."""
    json_data: JSON
    """JSON data for this party member."""


class ModData(typing.NamedTuple):
    load_order: int
    """The index in which this mod loads."""
    uuid: str
    """The UUID of the mod."""
    name: str
    """The name of the mod."""
    version: str
    """The semantic version of the mod."""
    magic1: bytes
    """Unknown."""
    settings: RawSave.ModSettings
    """Unknown."""


if __name__ == "__main__":
    sf = SaveFile.load(open("save2.sav", "rb"))
    print(sf)
