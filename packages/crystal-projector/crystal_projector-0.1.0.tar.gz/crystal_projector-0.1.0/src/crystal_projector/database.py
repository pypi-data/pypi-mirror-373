import io
import json
import typing

from .gen.ability import Ability
from .gen.actor import Actor
from .gen.animation import Animation
from .gen.biome import Biome
from .gen.database import Database as RawDatabase
from .gen.difficulty import Difficulty
from .gen.equipment import Equipment
from .gen.gender import Gender
from .gen.item import Item
from .gen.job import Job
from .gen.loading import Loading as RawLoading
from .gen.monster import Monster
from .gen.passive import Passive
from .gen.recipe import Recipe
from .gen.spark import Spark
from .gen.status import Status
from .gen.system import System
from .gen.troop import Troop
from .gen.voxel import Voxel

JSONObject = typing.Dict[str, "JSON"]
"""A JSON object."""


JSONArray = typing.List["JSON"]
"""A JSON array."""


JSON = typing.Union[None, bool, float, str, "JSONObject", "JSONArray"]
"""A JSON value."""


class Database(typing.NamedTuple):
    """A parsed Crystal Project database `.dat` file."""

    version: int
    """The version of this database file."""
    database: JSONArray
    """The database."""

    @classmethod
    def load(cls, infile: typing.BinaryIO) -> "Database":
        """Load a database from memory."""

        db = RawDatabase.from_io(infile)

        result = io.BytesIO()
        for b in db.database:
            result.write((255 - b).to_bytes(1, "little"))
        return Database(
            db.version, json.loads(str(result.getvalue(), encoding="UTF-8"))
        )


class Patch:
    """A Crystal Project game mode definition.
    This is for changing the databases for Vanilla and Chaos mode.
    For Easy/Hard mode, see `difficulty.yaml`.

    We have to create this Patch class manually,
    as Quicktype does not support nested schemas well at all.
    """

    id: int
    """The unique ID of this patch."""
    name: str
    """The name of this patch."""
    abilities: typing.List[Ability]
    """Any abilities changed by this patch."""
    difficulties: typing.List[Difficulty]
    """Any difficulties changed by this patch."""
    equipment: typing.List[Equipment]
    """Any equipment changed by this patch."""
    genders: typing.List[Gender]
    """Any genders changed by this patch."""
    items: typing.List[Item]
    """Any items changed by this patch."""
    jobs: typing.List[Job]
    """Any jobs changed by this patch."""
    monsters: typing.List[Monster]
    """Any monsters changed by this patch."""
    passives: typing.List[Passive]
    """Any passives changed by this patch."""
    recipes: typing.List[Recipe]
    """Any recipes changed by this patch."""
    sparks: typing.List[Spark]
    """Any sparks changed by this patch."""
    statuses: typing.List[Status]
    """Any statuses changed by this patch."""
    troops: typing.List[Troop]
    """Any troops changed by this patch."""

    def __init__(
        self,
        id: int,
        name: str,
        abilities: typing.List[Ability],
        difficulties: typing.List[Difficulty],
        equipment: typing.List[Equipment],
        genders: typing.List[Gender],
        items: typing.List[Item],
        jobs: typing.List[Job],
        monsters: typing.List[Monster],
        passives: typing.List[Passive],
        recipes: typing.List[Recipe],
        sparks: typing.List[Spark],
        statuses: typing.List[Status],
        troops: typing.List[Troop],
    ) -> None:
        self.id = id
        self.name = name
        self.abilities = abilities
        self.difficulties = difficulties
        self.equipment = equipment
        self.genders = genders
        self.items = items
        self.jobs = jobs
        self.monsters = monsters
        self.passives = passives
        self.recipes = recipes
        self.sparks = sparks
        self.statuses = statuses
        self.troops = troops

    @classmethod
    def from_dict(cls, json) -> "Patch":
        return Patch(
            id=json["ID"],
            name=json["Name"],
            abilities=[Ability.from_dict(x) for x in json["Abilities"]],
            difficulties=[Difficulty.from_dict(x) for x in json["Difficulties"]],
            equipment=[Equipment.from_dict(x) for x in json["Equipment"]],
            genders=[Gender.from_dict(x) for x in json["Genders"]],
            items=[Item.from_dict(x) for x in json["Items"]],
            jobs=[Job.from_dict(x) for x in json["Jobs"]],
            monsters=[Monster.from_dict(x) for x in json["Monsters"]],
            passives=[Passive.from_dict(x) for x in json["Passives"]],
            recipes=[Recipe.from_dict(x) for x in json["Recipes"]],
            sparks=[Spark.from_dict(x) for x in json["Sparks"]],
            statuses=[Status.from_dict(x) for x in json["Statuses"]],
            troops=[Troop.from_dict(x) for x in json["Troops"]],
        )

    def to_dict(self) -> JSONObject:
        return {
            "ID": self.id,
            "Name": self.name,
            "Abilities": [x.to_dict() for x in self.abilities],
            "Difficulties": [x.to_dict() for x in self.difficulties],
            "Equipment": [x.to_dict() for x in self.equipment],
            "Genders": [x.to_dict() for x in self.genders],
            "Items": [x.to_dict() for x in self.items],
            "Jobs": [x.to_dict() for x in self.jobs],
            "Monsters": [x.to_dict() for x in self.monsters],
            "Passives": [x.to_dict() for x in self.passives],
            "Recipes": [x.to_dict() for x in self.recipes],
            "Sparks": [x.to_dict() for x in self.sparks],
            "Statuses": [x.to_dict() for x in self.statuses],
            "Troops": [x.to_dict() for x in self.troops],
        }


def load_abilities(infile: typing.BinaryIO) -> typing.Dict[int, Ability]:
    return {
        json["ID"]: Ability.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_actors(infile: typing.BinaryIO) -> typing.Dict[int, Actor]:
    return {
        json["ID"]: Actor.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_animations(infile: typing.BinaryIO) -> typing.Dict[int, Animation]:
    return {
        json["ID"]: Animation.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_biomes(infile: typing.BinaryIO) -> typing.Dict[int, Biome]:
    return {
        json["ID"]: Biome.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_difficulties(infile: typing.BinaryIO) -> typing.Dict[int, Difficulty]:
    return {
        json["ID"]: Difficulty.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_equipment(infile: typing.BinaryIO) -> typing.Dict[int, Equipment]:
    return {
        json["ID"]: Equipment.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_genders(infile: typing.BinaryIO) -> typing.Dict[int, Gender]:
    return {
        json["ID"]: Gender.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_items(infile: typing.BinaryIO) -> typing.Dict[int, Item]:
    return {
        json["ID"]: Item.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_jobs(infile: typing.BinaryIO) -> typing.Dict[int, Job]:
    return {
        json["ID"]: Job.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_loading(infile: typing.BinaryIO) -> typing.List[str]:
    return [s.value for s in RawLoading.from_io(infile).strings]


def load_monsters(infile: typing.BinaryIO) -> typing.Dict[int, Monster]:
    return {
        json["ID"]: Monster.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_passives(infile: typing.BinaryIO) -> typing.Dict[int, Passive]:
    return {
        json["ID"]: Passive.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_patches(infile: typing.BinaryIO) -> typing.Dict[int, Patch]:
    return {
        json["ID"]: Patch.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_recipes(infile: typing.BinaryIO) -> typing.Dict[int, Recipe]:
    return {
        json["ID"]: Recipe.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_sparks(infile: typing.BinaryIO) -> typing.Dict[int, Spark]:
    return {
        json["ID"]: Spark.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_statuses(infile: typing.BinaryIO) -> typing.Dict[int, Status]:
    return {
        json["ID"]: Status.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_system(infile: typing.BinaryIO) -> System:
    return System.from_dict(Database.load(infile).database)


def load_troops(infile: typing.BinaryIO) -> typing.Dict[int, Troop]:
    return {
        json["ID"]: Troop.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


def load_voxels(infile: typing.BinaryIO) -> typing.Dict[int, Voxel]:
    return {
        json["ID"]: Voxel.from_dict(json)
        for json in Database.load(infile).database
        if json
    }


############
# TEMP STUFF
############

if __name__ == "__main__":
    import os

    import jsonschema
    import referencing
    import referencing.exceptions
    import yaml

    root = (
        "C:/Program Files (x86)/Steam/steamapps/common/Crystal Project/Content/Database"
    )

    def resolve_schema(uri: str) -> referencing.Resource[JSON]:
        path = os.path.join(os.path.dirname(__file__), "schema", "json", uri)
        contents = yaml.load(open(path, encoding="UTF-8"), yaml.FullLoader)
        return referencing.Resource.from_contents(contents)

    def test_db(filename: str, load_fn: typing.Callable[[typing.BinaryIO], typing.Any]):
        print(f"=== {filename.upper()} ===")
        schema = yaml.load(
            open(f"schema/json/{filename}.yaml", encoding="UTF-8"), yaml.FullLoader
        )
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(
            schema, registry=referencing.Registry(retrieve=resolve_schema)
        )
        dbfile = open(f"{root}/{filename}.dat", "rb")
        raw_json = Database.load(dbfile).database

        if type(raw_json) is list:
            for thing in raw_json:
                if thing:
                    print(f"\tValidating {thing['ID']} ({thing['Name']})...")
                    validator.validate(thing, schema)
        else:
            print(f"\tValidating...")
            validator.validate(raw_json, schema)

        print("\tTesting deserialization...")
        dbfile.seek(0)
        load_fn(dbfile)
        print("\tDone!")

    def copy_over_db(filename: str):
        dbfile = open(f"{root}/{filename}.dat", "rb")
        raw_json = Database.load(dbfile).database
        with open(f"temp/{filename}.dat.json", "w", encoding="UTF-8") as outfile:
            json.dump(raw_json, outfile, indent=2)

    test_db("ability", load_abilities)
    test_db("actor", load_actors)
    test_db("animation", load_animations)
    test_db("biome", load_biomes)
    test_db("difficulty", load_difficulties)
    test_db("equipment", load_equipment)
    test_db("gender", load_genders)
    test_db("item", load_items)
    test_db("job", load_jobs)

    print(f"=== LOADING ===")
    with open(f"{root}/loading.dat", "rb") as stream:
        loading = load_loading(stream)
        for message in loading:
            print(f"\t{message}")

    test_db("monster", load_monsters)
    test_db("passive", load_passives)
    test_db("patch", load_patches)
    test_db("recipe", load_recipes)
    test_db("spark", load_sparks)
    test_db("status", load_statuses)
    test_db("system", load_system)
    test_db("troop", load_troops)
    test_db("voxel", load_voxels)
