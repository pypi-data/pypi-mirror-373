import enum
import io
import json
import typing
import uuid

from . import database


class Mod:
    id: uuid.UUID
    title: str
    description: str
    author: str
    version: str
    editor_version: int
    steam_workshop_file_id: int
    timestamp: str
    is_localization: bool
    language: typing.Optional[str]
    has_custom_content: bool
    fonts: typing.Optional["Fonts"]
    system: typing.Optional[database.System]
    tree: typing.List["TreeItem"]
    abilities: typing.List[database.Ability]
    animations: typing.List[database.Animation]
    biomes: typing.List[database.Biome]
    difficulties: typing.List[database.Difficulty]
    equipment: typing.List[database.Equipment]
    folders: typing.List["Folder"]
    genders: typing.List[database.Gender]
    items: typing.List[database.Item]
    jobs: typing.List[database.Job]
    monsters: typing.List[database.Monster]
    passives: typing.List[database.Passive]
    recipes: typing.List[database.Recipe]
    sparks: typing.List[database.Spark]
    statuses: typing.List[database.Status]
    troops: typing.List[database.Troop]
    entities: typing.List[database.JSON]

    def __init__(
        self,
        id: uuid.UUID,
        title: str,
        description: str,
        author: str,
        version: str,
        editor_version: int,
        steam_workshop_file_id: int,
        timestamp: str,
        is_localization: bool,
        language: typing.Optional[str],
        has_custom_content: bool,
        fonts: typing.Optional["Fonts"],
        system: typing.Optional[database.System],
        tree: typing.List["TreeItem"],
        abilities: typing.List[database.Ability],
        animations: typing.List[database.Animation],
        biomes: typing.List[database.Biome],
        difficulties: typing.List[database.Difficulty],
        equipment: typing.List[database.Equipment],
        folders: typing.List["Folder"],
        genders: typing.List[database.Gender],
        items: typing.List[database.Item],
        jobs: typing.List[database.Job],
        monsters: typing.List[database.Monster],
        passives: typing.List[database.Passive],
        recipes: typing.List[database.Recipe],
        sparks: typing.List[database.Spark],
        statuses: typing.List[database.Status],
        troops: typing.List[database.Troop],
        entities: database.JSONArray,
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.author = author
        self.version = version
        self.editor_version = editor_version
        self.steam_workshop_file_id = steam_workshop_file_id
        self.timestamp = timestamp
        self.is_localization = is_localization
        self.language = language
        self.has_custom_content = has_custom_content
        self.fonts = fonts
        self.system = system
        self.tree = tree
        self.abilities = abilities
        self.animations = animations
        self.biomes = biomes
        self.difficulties = difficulties
        self.equipment = equipment
        self.folders = folders
        self.genders = genders
        self.items = items
        self.jobs = jobs
        self.monsters = monsters
        self.passives = passives
        self.recipes = recipes
        self.sparks = sparks
        self.statuses = statuses
        self.troops = troops
        self.entities = entities

    @classmethod
    def from_dict(cls, json: database.JSONObject) -> "Mod":
        return Mod(
            uuid.UUID(json["ID"]),
            json["Title"],
            json["Description"],
            json["Author"],
            json["Version"],
            json["EditorVersion"],
            json["SteamWorkshopFileID"],
            json["Timestamp"],  # datetime.datetime.fromisoformat(json["Timestamp"])
            json["IsLocalization"],
            json["Language"],
            json["HasCustomContent"],
            Fonts.from_dict(json["Fonts"]) if json["Fonts"] else None,
            database.System.from_dict(json["System"]) if json["System"] else None,
            [TreeItem.from_dict(x) for x in json["Tree"]],
            [database.Ability.from_dict(x) for x in json["Abilities"]],
            [database.Animation.from_dict(x) for x in json["Animations"]],
            [database.Biome.from_dict(x) for x in json["Biomes"]],
            [database.Difficulty.from_dict(x) for x in json["Difficulties"]],
            [database.Equipment.from_dict(x) for x in json["Equipment"]],
            [Folder.from_dict(x) for x in json["Folders"]],
            [database.Gender.from_dict(x) for x in json["Genders"]],
            [database.Item.from_dict(x) for x in json["Items"]],
            [database.Job.from_dict(x) for x in json["Jobs"]],
            [database.Monster.from_dict(x) for x in json["Monsters"]],
            [database.Passive.from_dict(x) for x in json["Passives"]],
            [database.Recipe.from_dict(x) for x in json["Recipes"]],
            [database.Spark.from_dict(x) for x in json["Sparks"]],
            [database.Status.from_dict(x) for x in json["Statuses"]],
            [database.Troop.from_dict(x) for x in json["Troops"]],
            json["Entities"],
        )

    def to_dict(self) -> database.JSONObject:
        return {
            "ID": self.id.hex,
            "Title": self.title,
            "Description": self.description,
            "Author": self.author,
            "Version": self.version,
            "EditorVersion": self.editor_version,
            "SteamWorkshopFileID": self.steam_workshop_file_id,
            "Timestamp": self.timestamp,  # self.timestamp.isoformat()
            "IsLocalization": self.is_localization,
            "Language": self.language,
            "HasCustomContent": self.has_custom_content,
            "Fonts": self.fonts.to_dict() if self.fonts else None,
            "System": self.system.to_dict() if self.system else None,
            "Tree": [x.to_dict() for x in self.tree],
            "Abilities": [x.to_dict() for x in self.abilities],
            "Animations": [x.to_dict() for x in self.animations],
            "Biomes": [x.to_dict() for x in self.biomes],
            "Difficulties": [x.to_dict() for x in self.difficulties],
            "Equipment": [x.to_dict() for x in self.equipment],
            "Folders": [x.to_dict() for x in self.folders],
            "Genders": [x.to_dict() for x in self.genders],
            "Items": [x.to_dict() for x in self.items],
            "Jobs": [x.to_dict() for x in self.jobs],
            "Monsters": [x.to_dict() for x in self.monsters],
            "Passives": [x.to_dict() for x in self.passives],
            "Recipes": [x.to_dict() for x in self.recipes],
            "Sparks": [x.to_dict() for x in self.sparks],
            "Statuses": [x.to_dict() for x in self.statuses],
            "Troops": [x.to_dict() for x in self.troops],
            "Entities": self.entities,
        }

    def __repr__(self) -> str:
        return "".join(
            (
                "Mod(",
                f"id={repr(self.id)},",
                f"title={repr(self.title)},",
                f"description={repr(self.description)},",
                f"author={repr(self.author)},",
                f"version={repr(self.version)},",
                f"editor_version={repr(self.editor_version)},",
                f"steam_workshop_file_id={repr(self.steam_workshop_file_id)},",
                f"timestamp={repr(self.timestamp)},",
                f"is_localization={repr(self.is_localization)},",
                f"language={repr(self.language)},",
                f"has_custom_content={repr(self.has_custom_content)},",
                f"fonts={repr(self.fonts)},",
                f"system={repr(self.system)},",
                f"tree={repr(self.tree)},",
                f"abilities={repr(self.abilities)},",
                f"animations={repr(self.animations)},",
                f"biomes={repr(self.biomes)},",
                f"difficulties={repr(self.difficulties)},",
                f"equipment={repr(self.equipment)},",
                f"folders={repr(self.folders)},",
                f"genders={repr(self.genders)},",
                f"items={repr(self.items)},",
                f"jobs={repr(self.jobs)},",
                f"monsters={repr(self.monsters)},",
                f"passives={repr(self.passives)},",
                f"recipes={repr(self.recipes)},",
                f"sparks={repr(self.sparks)},",
                f"statuses={repr(self.statuses)},",
                f"troops={repr(self.troops)},",
                f"entities={repr(self.entities)},",
                ")",
            )
        )


class Fonts:
    pixel: typing.Optional["Font"]
    smooth: typing.Optional["Font"]

    def __init__(
        self,
        pixel: typing.Optional["Font"],
        smooth: typing.Optional["Font"],
    ) -> None:
        self.pixel = pixel
        self.smooth = smooth

    @classmethod
    def from_dict(cls, json: database.JSONObject) -> "Fonts":
        return Fonts(
            Font.from_dict(json["FontPixel"]) if json["FontPixel"] else None,
            Font.from_dict(json["FontSmooth"]) if json["FontSmooth"] else None,
        )

    def to_dict(self) -> database.JSONObject:
        return {
            "FontPixel": self.pixel.to_dict() if self.pixel else None,
            "FontSmooth": self.smooth.to_dict() if self.smooth else None,
        }

    def __repr__(self) -> str:
        return "".join(
            (
                "Fonts(",
                f"pixel={repr(self.pixel)},",
                f"smooth={repr(self.smooth)},",
                ")",
            )
        )


class Font:
    standard: "FontStyle"
    standard_bold: "FontStyle"
    small: "FontStyle"
    small_bold: "FontStyle"
    header: "FontStyle"
    header_big: "FontStyle"

    def __init__(
        self,
        standard: "FontStyle",
        standard_bold: "FontStyle",
        small: "FontStyle",
        small_bold: "FontStyle",
        header: "FontStyle",
        header_big: "FontStyle",
    ) -> None:
        self.standard = standard
        self.standard_bold = standard_bold
        self.small = small
        self.small_bold = small_bold
        self.header = header
        self.header_big = header_big

    @classmethod
    def from_dict(cls, json: database.JSONObject) -> "Font":
        return Font(
            FontStyle.from_dict(json["Standard"]),
            FontStyle.from_dict(json["StandardBold"]),
            FontStyle.from_dict(json["Small"]),
            FontStyle.from_dict(json["SmallBold"]),
            FontStyle.from_dict(json["Header"]),
            FontStyle.from_dict(json["HeaderBig"]),
        )

    def to_dict(self) -> database.JSONObject:
        return {
            "Standard": self.standard.to_dict(),
            "StandardBold": self.standard_bold.to_dict(),
            "Small": self.small.to_dict(),
            "SmallBold": self.small_bold.to_dict(),
            "Header": self.header.to_dict(),
            "HeaderBig": self.header_big.to_dict(),
        }

    def __repr__(self) -> str:
        return "".join(
            (
                "Font(",
                f"standard={repr(self.standard)},",
                f"standard_bold={repr(self.standard_bold)},",
                f"small={repr(self.small)},",
                f"small_bold={repr(self.small_bold)},",
                f"header={repr(self.header)},",
                f"header_big={repr(self.header_big)},",
                ")",
            )
        )


class FontStyle:
    ttf_file_name: str
    size: int
    offset_y: int

    def __init__(
        self,
        ttf_file_name: str,
        size: int,
        offset_y: int,
    ) -> None:
        self.ttf_file_name = ttf_file_name
        self.size = size
        self.offset_y = offset_y

    @classmethod
    def from_dict(cls, json: database.JSONObject) -> "FontStyle":
        return FontStyle(
            json["TtfFileName"],
            json["Size"],
            json["OffsetY"],
        )

    def to_dict(self) -> database.JSONObject:
        return {
            "TtfFileName": self.ttf_file_name,
            "Size": self.size,
            "OffsetY": self.offset_y,
        }

    def __repr__(self) -> str:
        return "".join(
            (
                "FontStyle(",
                f"ttf_file_name={repr(self.ttf_file_name)},",
                f"size={repr(self.size)},",
                f"offset_y={repr(self.offset_y)},",
                ")",
            )
        )


class TreeItem:
    model_type_id: "ModelType"
    model_id: int
    sort_order: int
    children: typing.List["TreeItem"]
    is_expanded: bool

    def __init__(
        self,
        model_type_id: "ModelType",
        model_id: int,
        sort_order: int,
        children: typing.List["TreeItem"],
        is_expanded: bool,
    ) -> None:
        self.model_type_id = model_type_id
        self.model_id = model_id
        self.sort_order = sort_order
        self.children = children
        self.is_expanded = is_expanded

    @classmethod
    def from_dict(cls, json: database.JSONObject) -> "TreeItem":
        return TreeItem(
            ModelType(json["ModelTypeID"]),
            json["ModelID"],
            json["SortOrder"],
            [TreeItem.from_dict(x) for x in json["Children"]],
            json["IsExpanded"],
        )

    def to_dict(self) -> database.JSONObject:
        return {
            "ModelTypeID": self.model_type_id.value,
            "ModelID": self.model_id,
            "SortOrder": self.sort_order,
            "Children": [x.to_dict() for x in self.children],
            "IsExpanded": self.is_expanded,
        }

    def __repr__(self) -> str:
        return "".join(
            (
                "TreeItem(",
                f"model_type_id={repr(self.model_type_id)},",
                f"model_id={repr(self.model_id)},",
                f"sort_order={repr(self.sort_order)},",
                f"children={repr(self.children)},",
                f"is_expanded={repr(self.is_expanded)},",
                ")",
            )
        )


class ModelType(enum.Enum):
    ABILITY = 0
    EQUIPMENT = 2
    FOLDER = 3
    ITEM = 4
    JOB = 5
    MONSTER = 6
    PASSIVE = 7
    STATUS = 8
    SPARK = 9
    TROOP = 10
    GENDER = 11
    DIFFICULTY = 12
    BIOME = 14
    ANIMATION = 15
    RECIPE = 16


class Folder:
    id: int
    name: str

    def __init__(
        self,
        id: int,
        name: str,
    ) -> None:
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, json: database.JSONObject) -> "Folder":
        return Folder(
            json["ID"],
            json["Name"],
        )

    def to_dict(self) -> database.JSONObject:
        return {
            "ID": self.id,
            "Name": self.name,
        }

    def __repr__(self) -> str:
        return f"Folder(id={repr(self.id)}, name={repr(self.name)})"


if __name__ == "__main__":
    mod = Mod.from_dict(
        json.load(
            open(
                "../../Saved Games/Crystal Project/Mods/Test Project.json",
                encoding="UTF-8",
            )
        )
    )
    print(mod)
    print(mod.to_dict())
