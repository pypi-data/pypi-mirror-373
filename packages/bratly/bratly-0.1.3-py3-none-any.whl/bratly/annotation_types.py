import re
from typing import Optional, Union

from pydantic import BaseModel, field_validator

from .exceptions import ParsingError


class Fragment(BaseModel):
    """A fragment of text within an entity annotation. Defined by starting and ending character positions"""

    start: int
    end: int

    @field_validator("start", "end")
    def validate_idx(cls, v):
        if type(v) is int and v >= 0:
            return v
        raise ParsingError(
            "Badly initialized Fragment (start and end must be non-negative integers)\n",
        )

    class Config:
        validate_assignment = True

    def __str__(self) -> str:
        return f"{self.start} {self.end}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, Fragment):
            return (self.start == other.start) and (self.end == other.end)
        return False

    def __hash__(self):
        return hash((self.start, self.end))

    def __le__(self, other) -> bool:
        if isinstance(other, Fragment):
            return (self.start, self.end) <= (other.start, other.end)
        if isinstance(other, (int, float)):
            return (self.start <= other) and (self.end <= other)
        raise NotImplementedError

    def __lt__(self, other) -> bool:
        if isinstance(other, Fragment):
            return (self.start, self.end) < (other.start, other.end)
        if isinstance(other, (int, float)):
            return (self.start < other) and (self.end < other)
        raise NotImplementedError


class Annotation(BaseModel):
    """
    A generic type of annotation. Can be EntityAnnotation, RelationAnnotation, AttributeAnnotation, NormalizationAnnotation, NoteAnnotation, EquivalenceAnnotation. Defined by its id
    """

    id: str
    label: str

    @field_validator("id")
    def validate_id(cls, v):
        if type(v) is str and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized Annotation (id must be a non-empty string)\n",
        )

    @field_validator("label")
    def validate_label(cls, v):
        if type(v) is str and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized Annotation (label must be a non-empty string)\n",
        )

    class Config:
        validate_assignment = True

    def __eq__(self, other) -> bool:
        if isinstance(other, Annotation):
            return self.id == other.id and self.label == other.label
        return False

    def __hash__(self):
        return hash((self.id, self.label))


class EntityAnnotation(Annotation):
    r"""
    A type of Annotation, annotation of a text segment. Defined by a list of fragments (usually 1), the text content, and the label (category), as in ann file. e.g T1\tName 34 55\tPère Noël
    """

    fragments: list[Fragment]
    content: str

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        # check if id starts with T
        pattern: re.Pattern = re.compile(pattern=r"^T\d+$")
        if pattern.match(string=v):
            return v
        if v.isdigit():
            v = "T" + v
        else:
            raise ParsingError(
                "Badly initialized EntityAnnotation (the id should start with T, or it must exclusively contains digits)\n",
            )
        return v

    @field_validator("fragments")
    def validate_fragments(cls, v: list[Fragment]) -> list[Fragment]:
        if isinstance(v, list) and all(isinstance(f, Fragment) for f in v):
            return v
        raise ParsingError(
            "Badly initialized EntityAnnotation (fragments must be a list of Fragment objects)\n",
        )

    @field_validator("content")
    def validate_content(cls, v: str) -> str:
        if type(v) is str and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized EntityAnnotation (content must be a non-empty string)\n",
        )

    @classmethod
    def from_line(cls, line: str) -> "EntityAnnotation":
        if not re.match(r"^T\d+\t[\w\_/-]+ \d+ \d+(;\d+ \d+)*\t.*", line):
            msg = f"Badly formed annotation (An entity with a space ?)\n{line}"
            raise ParsingError(msg)
        items = line.split("\t")
        subitems = items[1].split(" ", 1)
        fragments = [Fragment(start=int(s.split(" ")[0]), end=int(s.split(" ")[1])) for s in subitems[1].split(";")]
        content = items[2]
        return cls(id=items[0], label=subitems[0], fragments=fragments, content=content)

    def get_start(self) -> int:
        return self.fragments[0].start

    def get_end(self) -> int:
        return self.fragments[-1].end

    def __str__(self) -> str:
        return f"{self.id}\t{self.label} {';'.join([str(s) for s in self.fragments])}\t{self.content}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, EntityAnnotation):
            return self.id == other.id and self.fragments == other.fragments and self.label == other.label and self.content == other.content
        return False

    def __hash__(self):
        # list being immutable, list of Fragment objects cannot be hashed, so we convert it to tuple beforehand
        fragments_hash = hash(tuple(hash(f) for f in self.fragments))
        return hash((self.id, fragments_hash, self.label, self.content))

    def __le__(self, other) -> bool:
        if isinstance(other, EntityAnnotation):
            if len(self.fragments) == 1 and len(other.fragments) == 1:
                return (self.get_start(), self.get_end()) <= (
                    other.get_start(),
                    other.get_end(),
                )
                # If 1st list has n fragments, the 2nd has m fragments
                # only min(m,n) fragments are compared.
            return all((fr.start, fr.end) <= (o.start, o.end) for fr, o in zip(self.fragments, other.fragments))
        if isinstance(other, Annotation):
            return self.id <= other.id
        if isinstance(other, (float, int)):
            return self.get_start() <= other
        raise NotImplementedError

    def __lt__(self, other) -> bool:
        if isinstance(other, EntityAnnotation):
            if len(self.fragments) == 1 and len(other.fragments) == 1:
                return (self.get_start(), self.get_end()) < (
                    other.get_start(),
                    other.get_end(),
                )
            return all((fr.start, fr.end) < (o.start, o.end) for fr, o in zip(self.fragments, other.fragments))
        if isinstance(other, Annotation):
            return self.id < other.id
        if isinstance(other, (float, int)):
            return self.get_start() < other
        raise NotImplementedError


class RelationAnnotation(Annotation):
    """A type of Annotation, a relation between two EntityAnnotations."""

    # tuple str (Optional), EntityAnnotation because Relation follows these formats:
    # - R1  Negation str1:T1 str2:T2
    argument1: tuple[str, EntityAnnotation]
    argument2: tuple[str, EntityAnnotation]

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        # check if id starts with T
        pattern: re.Pattern = re.compile(r"^R\d+$")
        if pattern.match(string=v):
            return v
        if v.isdigit():
            v = "R" + v
        else:
            raise ParsingError(
                "Badly initialized EntityAnnotation (the id should start with R, or it must exclusively contains digits)\n",
            )
        return v

    @field_validator("argument1", "argument2")
    def validate_argument(cls, v):
        if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], EntityAnnotation):
            return v
        raise ParsingError(
            "Badly initialized RelationAnnotation (the argument must be either an EntityAnnotation or a tuple of (str, EntityAnnotation))\n",
        )

    @classmethod
    def from_line(
        cls,
        line: str,
        entities: dict[str, EntityAnnotation],
    ) -> "RelationAnnotation":
        if not re.match(r"^R\d+\t[\w\_/-]+ \w+:T\d+ \w+:T\d+", line):
            raise ParsingError(f"Badly formed relation annotation\n{line}")
        items = line.split("\t")
        subitems = items[1].split(" ")
        # ---- Argument 1 ----
        arg1 = subitems[1].split(":")
        role1, ent1_id = arg1[0], arg1[1]

        if ent1_id in entities:
            ent1 = entities[ent1_id]
        else:
            raise ParsingError(f"The referenced entity {ent1_id} doesn't exist")

        # ---- Argument 2 ----
        arg2 = subitems[2].split(":")
        role2, ent2_id = arg2[0], arg2[1]

        if ent2_id in entities:
            ent2 = entities[ent2_id]
        else:
            raise ParsingError(f"The referenced entity {ent2_id} doesn't exist")

        return cls(
            id=items[0],
            label=subitems[0],
            argument1=(role1, ent1),
            argument2=(role2, ent2),
        )

    def __str__(self) -> str:
        arg1_str = f"{self.argument1[0]}:{self.argument1[1].id}"
        arg2_str = f"{self.argument2[0]}:{self.argument2[1].id}"
        return f"{self.id}\t{self.label} {arg1_str} {arg2_str}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, RelationAnnotation):
            return self.id == other.id and self.label == other.label and self.argument1 == other.argument1 and self.argument2 == other.argument2
        return False

    def __hash__(self):
        return hash((self.id, self.label, self.argument1, self.argument2))


class EquivalenceAnnotation(Annotation):
    id: str = "*"
    label: str = "Equiv"
    entities: list[EntityAnnotation]

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        if v != "*":
            print("Badly initialized EquivalenceAnnotation (the id has been converted to '*')\n")
            v = "*"
        return v

    @field_validator("label")
    def validate_label(cls, v: str) -> str:
        if v != "Equiv":
            print("Badly initialized EquivalenceAnnotation (the label has been converted to 'Equiv')\n")
            v = "Equiv"
        return v

    @field_validator("entities")
    def validate_entities(cls, v: list[EntityAnnotation]) -> list[EntityAnnotation]:
        if not all(isinstance(e, EntityAnnotation) for e in v):
            print("Badly initialized EquivalenceAnnotation (all entities must be EntityAnnotation instances)\n")
            v = [e for e in v if isinstance(e, EntityAnnotation)]
        return v

    @classmethod
    def from_line(
        cls,
        line: str,
        entities: dict[str, EntityAnnotation],
    ) -> "EquivalenceAnnotation":
        if not re.match(r"^\*\t[\w\_/-]+( T\d)+", line):
            raise ParsingError(f"Badly formed equivalence annotation\n{line}")
        items = line.split("\t")
        entity_refs = items[1].split(" ")[1:]
        ents = [entities[ref] for ref in entity_refs if ref in entities]
        if len(ents) < 2:
            raise ParsingError(
                "There were less than 2 entities references correctly",
            )
        if len(ents) < len(entity_refs):
            pass  # Not all the entity referenceres could be parsed
        return cls(entities=ents)

    def __str__(self) -> str:
        return f"*\tEquiv {' '.join([e.id for e in self.entities])}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, EquivalenceAnnotation):
            return self.entities == other.entities
        return False

    def __hash__(self):
        # list being immutable, list of Entities objects cannot be hashed, so we convert it to tuple beforehand
        entities_hash = hash(tuple(hash(e) for e in self.entities))
        return hash(entities_hash)


class EventAnnotation(Annotation):
    event_trigger: EntityAnnotation
    args: dict[str, EntityAnnotation]

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        # check if id starts with E
        pattern: re.Pattern = re.compile(r"^E\d+$")
        if pattern.match(string=v):
            return v
        if v.isdigit():
            v = "E" + v
        else:
            raise ParsingError(
                "Badly initialized EventAnnotation (the id should start with E, or it must exclusively contains digits)\n",
            )
        return v

    @field_validator("event_trigger")
    def validate_event_trigger(cls, v: EntityAnnotation) -> EntityAnnotation:
        if not isinstance(v, EntityAnnotation):
            raise ParsingError(
                "Badly initialized EventAnnotation (the event_trigger must be an EntityAnnotation instance)\n",
            )
        return v

    @field_validator("args")
    def validate_args(cls, v: dict[str, EntityAnnotation]) -> dict[str, EntityAnnotation]:
        if not all(isinstance(e, EntityAnnotation) for e in v.values()):
            raise ParsingError(
                "Badly initialized EventAnnotation (all args must be EntityAnnotation instances)\n",
            )
        return v

    @classmethod
    def from_line(
        cls,
        line: str,
        entities: dict[str, EntityAnnotation],
    ) -> "EventAnnotation":
        if not re.match(r"^E\d+\t[\w\_/-]+:[TE]\d+( \w+:[TE]\d+)+", line):
            raise ParsingError(f"Badly formed event annotation\n{line}")
        items = line.split("\t")
        subitems = items[1].split(" ")
        subsubitems = subitems[0].split(":")
        if subsubitems[1] not in entities:
            raise ParsingError(
                f"Event referencing a non-existing entity/event\n{line}",
            )
        args = {s.split(":")[0]: entities[s.split(":")[1]] for s in subitems[1:] if s.split(":")[1] in entities}
        if len(args) < len(subitems[1:]):
            raise ParsingError(
                f"Some arguments reference non-existing entiites/events\n{line}\nParsed: {len(args)} out of {len(subitems[1:])}",
            )
        return cls(id=items[0], label=subsubitems[0], event_trigger=entities[subsubitems[1]], args=args)

    def __str__(self) -> str:
        args_string = " ".join([f"{k}:{self.args[k].id}" for k in self.args])
        return f"{self.id}\t{self.label}:{self.event_trigger.id} {args_string}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, EventAnnotation):
            return self.id == other.id and self.label == other.label and self.event_trigger == other.event_trigger and self.args == other.args
        return False

    def __hash__(self):
        return hash((self.id, self.label, self.event_trigger, self.args))


class AttributeAnnotation(Annotation):
    """A type of Annotation, an attribute linked to an EntityAnnotation"""

    component: Annotation
    values: Optional[list[str]] = None

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        # check if id starts with A or M
        pattern: re.Pattern = re.compile(r"^[AM]\d+$")
        if pattern.match(string=v):
            return v
        if v.isdigit():
            v = "A" + v
        else:
            raise ParsingError(
                "Badly initialized AttributeAnnotation (the id should start with A or M, or it must exclusively contains digits)\n",
            )
        return v

    @field_validator("component")
    def validate_component(cls, v: Annotation) -> Annotation:
        if not isinstance(v, Annotation):
            raise ParsingError(
                "Badly initialized AttributeAnnotation (the component must be an Annotation instance)\n",
            )
        return v

    @field_validator("values")
    def validate_values(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return []
        if not all(isinstance(item, str) for item in v):
            raise ParsingError(
                "Badly initialized AttributeAnnotation (the values must be a list of strings)\n",
            )
        return v

    @classmethod
    def from_line(
        cls,
        line: str,
        entities: dict[str, Annotation],
    ) -> "AttributeAnnotation":
        if not re.match(r"^[AM]\d+\t[\w\_/-]+( \w+)+", line):
            raise ParsingError(f"Badly formed attribute annotation\n{line}")
        items = line.split("\t")
        subitems = items[1].split(" ")
        if subitems[1] not in entities:
            raise ParsingError("The referenced entity does not exist")
        subitems = items[1].split(" ")
        if len(subitems) > 2:
            return cls(id=items[0], label=subitems[0], component=entities[subitems[1]], values=subitems[2:])
        return cls(id=items[0], label=subitems[0], component=entities[subitems[1]], values=[])

    def __str__(self) -> str:
        if self.values:
            return f"{self.id}\t{self.label} {self.component.id} {' '.join(self.values)}"
        return f"{self.id}\t{self.label} {self.component.id}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, AttributeAnnotation):
            if self.id == other.id and self.label == other.label and self.component == other.component:
                if self.values is None:
                    return True
                return self.values == other.values
            return False
        return False

    def __hash__(self):
        if self.values is not None and isinstance(self.values, list):
            # list being immutable, list of str objects cannot be hashed, so we convert it to tuple beforehand
            values_hash = hash(tuple(hash(v) for v in self.values))
            return hash((self.id, self.label, self.component, values_hash))
        return hash((self.id, self.label, self.component, self.values))


class NormalizationAnnotation(Annotation):
    component: Annotation
    external_resource: tuple[str, str]
    content: str

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        # check if id starts with N
        pattern: re.Pattern = re.compile(r"^N\d+$")
        if pattern.match(string=v):
            return v
        if v.isdigit():
            v = "N" + v
        else:
            raise ParsingError(
                "Badly initialized NormalizationAnnotation (the id should start with N, or it must exclusively contains digits)\n",
            )
        return v

    @field_validator("component")
    def validate_component(cls, v: Annotation) -> Annotation:
        if not isinstance(v, Annotation):
            raise ParsingError(
                "Badly initialized NormalizationAnnotation (the component must be an Annotation instance)\n",
            )
        return v

    @field_validator("external_resource")
    def validate_external_resource(cls, v: tuple[str, str]) -> tuple[str, str]:
        if not isinstance(v, tuple) or len(v) != 2:
            raise ParsingError(
                "Badly initialized NormalizationAnnotation (the external_resource must be a tuple of two strings)\n",
            )
        return v

    @field_validator("content")
    def validate_content(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ParsingError(
                "Badly initialized NormalizationAnnotation (the content must be a string)\n",
            )
        return v

    @classmethod
    def from_line(
        cls,
        line: str,
        annotations: dict[str, Annotation],
    ) -> "NormalizationAnnotation":
        if not re.match(r"^N\d+\t[\w\_/-]+ \w+ \w+:\w+\t.+", line):
            raise ParsingError(f"Badly formed normalization annotation\n{line}")
        items = line.split("\t")
        subitems = items[1].split(" ")
        if subitems[1] not in annotations:
            raise ParsingError("The referenced entity does not exist")
        e_resource = subitems[2].split(":")
        return cls(
            id=items[0],
            label=subitems[0],
            component=annotations[subitems[1]],
            external_resource=(e_resource[0], e_resource[1]),
            content=items[2],
        )

    def __str__(self) -> str:
        return f"{self.id}\t{self.label} {self.component.id} {self.external_resource[0]}:{self.external_resource[1]}\t{self.content}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, NormalizationAnnotation):
            return (
                self.id == other.id and self.label == other.label and self.component == other.component and self.external_resource == other.external_resource and self.content == other.content
            )
        return False

    def __hash__(self):
        return hash(
            (self.id, self.label, self.component, self.external_resource, self.content),
        )


class NoteAnnotation(Annotation):
    component: Optional[Union[Annotation, str]]
    value: str

    @field_validator("id")
    def validate_id(cls, v: str) -> str:
        # check if id starts with #
        pattern: re.Pattern = re.compile(r"^#\d+$")
        if pattern.match(string=v):
            return v
        if v.isdigit():
            v = "#" + v
        else:
            raise ParsingError(
                "Badly initialized NoteAnnotation (the id should start with #, or it must exclusively contains digits)\n",
            )
        return v

    @field_validator("component")
    def validate_component(cls, v: Union[Annotation, str]) -> Union[Annotation, str]:
        if not isinstance(v, (Annotation, str)):
            raise ParsingError(
                "Badly initialized NoteAnnotation (the component must be an Annotation instance or a string)\n",
            )
        return v

    @field_validator("value")
    def validate_value(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ParsingError(
                "Badly initialized NoteAnnotation (the value must be a string)\n",
            )
        return v

    @classmethod
    def from_line(cls, line: str, annotations: dict[str, Annotation]) -> "NoteAnnotation":
        if not re.match(r"^#\d*\t[\w\_/\.-]+ \w+\t.*", line):
            raise ParsingError(f"Badly formed note annotation\n{line}")
        items = line.split("\t")
        subitems = items[1].split(" ")
        if len(subitems) > 1:
            if subitems[1] in annotations:
                return cls(id=items[0], label=subitems[0], value=items[2], component=annotations[subitems[1]])
            return cls(id=items[0], label=subitems[0], value=items[2], component=subitems[1])
        return cls(id=items[0], label=subitems[0], value=items[2], component=None)

    def __str__(self) -> str:
        if type(self.component) is str:
            return f"{self.id}\t{self.label} {self.component}\t{self.value}"
        assert isinstance(self.component, Annotation)
        return f"{self.id}\t{self.label} {self.component.id}\t{self.value}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if isinstance(other, NoteAnnotation):
            if self.id == other.id and self.label == other.label and self.value == other.value:
                if self.component is None:
                    return True
                return self.component == other.component
            return False
        return False

    def __hash__(self):
        return hash((self.id, self.label, self.value, self.component))
