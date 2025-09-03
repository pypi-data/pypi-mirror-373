import json
from operator import itemgetter
from os.path import basename, dirname, splitext
from typing import Any, Optional, Union

from pydantic import BaseModel, field_validator, model_validator

from .annotation_types import (
    Annotation,
    AttributeAnnotation,
    EntityAnnotation,
    EquivalenceAnnotation,
    EventAnnotation,
    Fragment,
    NormalizationAnnotation,
    NoteAnnotation,
    RelationAnnotation,
)
from .exceptions import ParsingError


class AnnotationCollection(BaseModel):
    """A set of Annotations, one txt file can be linked to one or multiple AnnotationCollection (multiple versions, different annot types...)"""

    # metadata
    version: str = "0.0.1"
    comment: str = "Empty comment"
    # actual data
    annotations: list[Annotation] = []

    class Config:
        validate_assignment = True

    @field_validator("version", "comment")
    def validate_acol_metadata(cls, v):
        if type(v) is str and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized AnnotationCollection (version and comment must be non-empty strings)\n",
        )

    @field_validator("annotations")
    def validate_annotations(cls, v):
        if isinstance(v, list):
            if len(v) == 0:
                return []
            if all(isinstance(item, Annotation) for item in v):
                return v
        raise ParsingError(
            "Badly initialized AnnotationCollection (annotations must be a list of Annotation instances)\n",
        )

    def get_annotations(
        self,
        descendant_type=None,
    ) -> Union[
        list[Annotation],
        list[EntityAnnotation],
        list[RelationAnnotation],
        list[EventAnnotation],
        list[EquivalenceAnnotation],
        list[NormalizationAnnotation],
        list[NoteAnnotation],
    ]:
        """
        Getter method for annotations, two use cases:
        1- Gives all annotations by default
        2- Gives a list of a particular type of annotation if the descendant_type argument os used
        """
        if descendant_type is None:
            return self.annotations
        result = [instance for instance in self.annotations if isinstance(instance, descendant_type)]
        return result

    def add_annotation(self, ann: Annotation) -> None:
        if ann is None:
            raise TypeError(
                "An Annotation instance is expected as an argument of the method add_annotation.",
            )
        if not isinstance(ann, Annotation):
            raise TypeError("The expected argument is an Annotation instance.")
        self.annotations.append(ann)

    def extend_annotation(self, anns: list[Annotation]) -> None:
        if anns is None:
            raise TypeError(
                "A list[Annotation] instance is expected as an argument of the method extend_annotation.",
            )
        if len(anns) != 0:
            if not isinstance(anns, list) and not all(isinstance(ann, Annotation) for ann in anns):
                raise TypeError("The expected argument is a list[Annotation] instance.")
            self.annotations.extend(anns)

    def remove_orphan_notes(self):
        """Delete Notes, Relations, Events, Equivalences, Normalizations and Attributes if they link towards a non-existant Entity"""
        anns_to_delete = []

        notes = self.get_annotations(descendant_type=NoteAnnotation)
        for note in notes:
            assert isinstance(note, NoteAnnotation)
            if issubclass(type(note.component), Annotation):
                if note.component not in self.annotations:
                    anns_to_delete.append(note)
            elif isinstance(note.component, str):
                str_list = [ann.id for ann in self.annotations]
                if note.component not in str_list:
                    anns_to_delete.append(note)

        relations = self.get_annotations(descendant_type=RelationAnnotation)
        for relation in relations:
            assert isinstance(relation, RelationAnnotation)
            if relation.argument1[1] not in self.annotations or relation.argument2[1] not in self.annotations:
                anns_to_delete.append(relation)

        events = self.get_annotations(descendant_type=EventAnnotation)
        for event in events:
            assert isinstance(event, EventAnnotation)
            if event.event_trigger not in self.annotations:
                anns_to_delete.append(event)
            else:
                for ann_ev in event.args.values():
                    if ann_ev not in self.annotations:
                        anns_to_delete.append(event)
                        continue

        attributes = self.get_annotations(descendant_type=AttributeAnnotation)
        for attribute in attributes:
            assert isinstance(attribute, AttributeAnnotation)
            if attribute.component not in self.annotations:
                anns_to_delete.append(attribute)
        equivalences = self.get_annotations(descendant_type=EquivalenceAnnotation)
        for equivalence in equivalences:
            assert isinstance(equivalence, EquivalenceAnnotation)
            for ann_eq in equivalence.entities:
                if ann_eq not in self.annotations:
                    anns_to_delete.append(equivalence)
                    break

        normalizations = self.get_annotations(descendant_type=NormalizationAnnotation)
        for normalization in normalizations:
            assert isinstance(normalization, NormalizationAnnotation)
            if normalization.component not in self.annotations:
                anns_to_delete.append(normalization)

        # now delete orphan anns
        for i in anns_to_delete:
            while i in self.annotations:
                self.annotations.remove(i)

    def sort_annotations(self) -> None:
        (
            entities,
            relations,
            attributes,
            events,
            equivalences,
            normalizations,
            notes,
            other_annot,
        ) = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        for ann in self.annotations:
            if isinstance(ann, EntityAnnotation):
                entities.append(ann)
            elif isinstance(ann, RelationAnnotation):
                relations.append(ann)
            elif isinstance(ann, AttributeAnnotation):
                attributes.append(ann)
            elif isinstance(ann, EquivalenceAnnotation):
                equivalences.append(ann)
            elif isinstance(ann, EventAnnotation):
                events.append(ann)
            elif isinstance(ann, NormalizationAnnotation):
                normalizations.append(ann)
            elif isinstance(ann, NoteAnnotation):
                notes.append(ann)
            elif isinstance(ann, Annotation):
                other_annot.append(ann)
            else:
                raise ParsingError(
                    f"Unknown type, it is supposed to be an Annotation:\n{type(ann)}",
                )

        # sort entities
        entities = sorted(entities, key=lambda x: (x.get_start(), x.get_end()))
        # TODO: if others __lt__ are implemented, do the same things for the other types of annotation

        # new list in the following order of annotation types: entity, relation, attribute, event, normalization, note and other annotations
        new_list: list[Annotation] = []
        new_list.extend(entities)
        new_list.extend(relations)
        new_list.extend(attributes)
        new_list.extend(equivalences)
        new_list.extend(events)
        new_list.extend(normalizations)
        new_list.extend(notes)
        new_list.extend(other_annot)
        # sorted list is updated
        self.annotations = new_list

    def remove_duplicates(self) -> None:
        """Remove duplicates annotation"""
        entities: list[EntityAnnotation] = []
        relations: list[RelationAnnotation] = []
        notes: list[NoteAnnotation] = []
        equivalences: list[EquivalenceAnnotation] = []
        attributes: list[AttributeAnnotation] = []
        events: list[EventAnnotation] = []
        normalizations: list[NormalizationAnnotation] = []

        res: list[Annotation] = []
        for ann in self.annotations:
            if isinstance(ann, EntityAnnotation):
                for added_entitie in entities:
                    if ann.fragments == added_entitie.fragments and ann.label == added_entitie.label and ann.content == added_entitie.content:
                        break
                else:
                    res.append(ann)
                    entities.append(ann)
            elif isinstance(ann, RelationAnnotation):
                for added_relation in relations:
                    if ann.label == added_relation.label and ann.argument1 == added_relation.argument1 and ann.argument2 == added_relation.argument2:
                        break
                else:
                    res.append(ann)
                    relations.append(ann)
            elif isinstance(ann, NoteAnnotation):
                for added_note in notes:
                    if ann.label == added_note.label and ann.value == added_note.value and ann.component == added_note.component:
                        break
                else:
                    res.append(ann)
                    notes.append(ann)
            elif isinstance(ann, AttributeAnnotation):
                for added_attribute in attributes:
                    if ann.label == added_attribute.label and ann.component == added_attribute.component and ann.values == added_attribute.values:
                        break
                else:
                    res.append(ann)
                    attributes.append(ann)
            elif isinstance(ann, EquivalenceAnnotation):
                for added_equivalence in equivalences:
                    if ann.entities == added_equivalence.entities:
                        break
                else:
                    res.append(ann)
                    equivalences.append(ann)
            elif isinstance(ann, EventAnnotation):
                for added_event in events:
                    if ann.label == added_event.label and ann.event_trigger == added_event.event_trigger and ann.args == added_event.args:
                        break
                else:
                    res.append(ann)
                    events.append(ann)
            elif isinstance(ann, NormalizationAnnotation):
                for added_normalization in normalizations:
                    if (
                        ann.label == added_normalization.label
                        and ann.component == added_normalization.component
                        and ann.external_resource == added_normalization.external_resource
                        and ann.content == added_normalization.content
                    ):
                        break
                else:
                    res.append(ann)
                    normalizations.append(ann)
            else:
                raise ValueError("Unsupported type. Should be an annotation type.")

        self.annotations = res

        # remove orphan annotations
        self.remove_orphan_notes()

    def replace_annotation_labels(
        self,
        old_name: str,
        new_name: str,
        specific_type: Optional[type] = None,
        all_labels: bool = False,
    ) -> None:
        """Replace annotations label by another one"""
        if all_labels is False and (old_name == "" or old_name is None or new_name == "" or new_name is None):
            print(
                "replace_annotation_labels: You should give a non-empty old_name and new_name argumeents.",
            )
            return
        if specific_type is None:
            for annot in self.annotations:
                if annot.label == old_name or all_labels is True:
                    annot.label = new_name
        else:
            for annot in self.annotations:
                if isinstance(annot, specific_type) and (annot.label == old_name or all_labels is True):
                    annot.label = new_name

    def remove_contained_annotations(self, of_same_label_only: bool = True) -> None:
        """
        Remove contained annotations, that is, annotations that are contained in another one, with the same tag
        Notes: multi-fragment entities are ignored
        """
        # get only uni_fragged entities
        entities_unifrag = [ann for ann in self.annotations if isinstance(ann, EntityAnnotation) if len(ann.fragments) == 1]
        # get only multi_fragged entities
        entities_multifrag = [ann for ann in self.annotations if isinstance(ann, EntityAnnotation) if len(ann.fragments) > 1]
        # get non entities
        annot_others = [ann for ann in self.annotations if not isinstance(ann, EntityAnnotation)]
        sorted_entities = sorted(
            entities_unifrag,
            key=lambda ann: ann.fragments[0].end - ann.fragments[0].start,
            reverse=True,
        )
        # prepare the final annotations
        filtered_annotations: list[Annotation] = []

        # remove contained entities
        for i, current_ann in enumerate(sorted_entities):
            is_contained = False
            for _, other_ann in enumerate(sorted_entities, start=i + 1):
                if (
                    (current_ann.label == other_ann.label or of_same_label_only is False)
                    and other_ann.fragments[0].start <= current_ann.fragments[0].start
                    and other_ann.fragments[0].end > current_ann.fragments[0].end
                ) or (
                    (current_ann.label == other_ann.label or of_same_label_only is False)
                    and other_ann.fragments[0].start < current_ann.fragments[0].start
                    and other_ann.fragments[0].end >= current_ann.fragments[0].end
                ):
                    is_contained = True
                    break
            if not is_contained:
                filtered_annotations.append(current_ann)

        # add other annotations along with the cleaned uni-fragged entities
        filtered_annotations.extend(entities_multifrag)
        filtered_annotations.extend(annot_others)
        # apply the change to the annotation collection
        self.annotations = filtered_annotations

        # remove orphan annotations
        self.remove_orphan_notes()

        # run final sorting
        self.sort_annotations()

    def renum(self, renum_start: int = 0) -> None:
        """Renumerotize Annotations"""
        # This dictionary keeps track of the count of each annotation type
        dico_count: dict[str, int] = {
            "T": 1,
            "R": 1,
            "A": 1,
            "M": 1,
            "N": 1,
            "E": 1,
            "#": 1,
        }

        for annot in self.annotations:
            if annot.id[0] in dico_count:
                annot.id = f"{annot.id[0]}{dico_count[annot.id[0]] + renum_start}"
                dico_count[annot.id[0]] += 1
            elif annot.id[0] == "*":
                pass  # no number associated with EquivalenceAnnotation objects
            else:
                message = "Badly formed annotation id, annotation being: " + str(annot) + " and its id: " + annot.id
                raise ParsingError(message)

    def __str__(self) -> str:
        return f"Annotation Collection\n version: {self.version}\n description: {self.comment}\n number of annotations: {len(self.annotations)}"

    def combine(self, anns: "AnnotationCollection", with_renum=False) -> None:
        """Extends self.annotations"""
        self.extend_annotation(anns.annotations)
        if with_renum:
            self.renum()

    def keep_specific_annotations(self, labels: list[str], annot_type=None) -> None:
        """
        Delete all annotations that are not EntityAnnotation (or another type) associated with one of the labels in the list
        this function is useful when you want to transform ann files which contains multiple labels (anatomie, substance, etc.)
        to another which contains only one of those labels.
        """
        res: list[Annotation] = []
        try:
            for ann in self.annotations:
                if (annot_type is None or isinstance(ann, annot_type)) and ann.label in labels:
                    res.append(ann)  # noqa: PERF401
        except Exception as general_exception:
            print("Exception occurred:", str(general_exception))
            print(
                "No modification have been done on the AnnotationCollection instance.",
            )
            return
        self.annotations = res

    def remove_annotations_given_label(self, targeted_label) -> None:
        """Remove all annotations that have a specific label"""
        new_list: list[Annotation] = [ann for ann in self.annotations if ann.label != targeted_label]
        self.annotations = new_list

    def stats_annotation_types(self, verbose: bool = False) -> dict[type, int]:
        """Counts types of annotation (Entities count, Relations count, etc)"""
        types = [
            EntityAnnotation,
            RelationAnnotation,
            EquivalenceAnnotation,
            EventAnnotation,
            AttributeAnnotation,
            NormalizationAnnotation,
            NoteAnnotation,
        ]
        dico: dict[type, int] = {}
        for t in types:
            dico[t] = len(self.get_annotations(descendant_type=t))
            if verbose:
                print("Type:", str(t), ":", str(dico[t]), "annotations.")
        return dico

    def stats_labels_given_annot_type(
        self,
        descendant_type: type = EntityAnnotation,
        verbose: bool = False,
    ) -> dict[str, int]:
        """Gives labels statistics count, for a given AnnotationType"""
        annotations = self.get_annotations(descendant_type=descendant_type)
        dico: dict[str, int] = {}
        for ann in annotations:
            if ann.label not in dico:
                dico[ann.label] = 1
            else:
                dico[ann.label] += 1
        if verbose:
            print("For the following type:", descendant_type, ", we have:")
            for k, value in dico.items():
                print(str(value), "annotations with label:", k)
        return dico

    def stats_entity_contents_given_label(
        self,
        label: str = "",
        verbose: bool = False,
    ) -> dict[str, int]:
        """Gives entity content statistics count, for a given label, or for all entities if label is not given"""
        dico: dict[str, int] = {}
        annotations = self.get_annotations(descendant_type=EntityAnnotation)
        if label != "":
            for ann in annotations:
                if ann.label == label and isinstance(ann, EntityAnnotation):
                    if ann.content not in dico:
                        dico[ann.content] = 1
                    else:
                        dico[ann.content] += 1
        else:  # case where the label argument is not given: we go through all entities
            for ann in annotations:
                if isinstance(ann, EntityAnnotation):
                    if ann.content not in dico:
                        dico[ann.content] = 1
                    else:
                        dico[ann.content] += 1
        if verbose:
            # sort dico in descending order
            dico = dict(sorted(dico.items(), key=itemgetter(1), reverse=True))
            if label == "":
                print("Among all entities, we have:")
                for k, value in dico.items():
                    print(str(value), "annotations with content:", k)
            else:
                print("Among entities with label", label, ", we have:")
                for k, value in dico.items():
                    print(str(value), "annotations with content:", k)
        return dico

    def to_json(self, path_json_file: str = "") -> dict[str, dict[str, list[Any]]]:
        """Save ann data as json file"""
        # create dict
        dic_res: dict[str, dict[str, list[Any]]] = {}

        # get stats of entity_ann labels
        dico_label = self.stats_labels_given_annot_type(
            descendant_type=EntityAnnotation,
        )

        # adding unique texts
        for label in dico_label:
            dico_text = self.stats_entity_contents_given_label(label=label)
            mytexts = dico_text.keys()
            mylabeltexts: dict[str, list[Any]] = {txt: [] for txt in mytexts}
            dic_res[label] = mylabeltexts

        # add associated notes
        notes = self.get_annotations(descendant_type=NoteAnnotation)
        for note in notes:
            if isinstance(note, NoteAnnotation):
                if isinstance(note.component, EntityAnnotation):
                    if note.component in self.annotations:
                        label, text, note_value = (
                            note.component.label,
                            note.component.content,
                            note.value,
                        )
                        list_txts = dic_res[label].keys()
                        if text in list_txts and note_value not in dic_res[label][text]:
                            dic_res[label][text].append(note_value)
                else:
                    for ann in self.annotations:
                        if isinstance(ann, EntityAnnotation) and note.component == ann.id:
                            label, text, note_value = (
                                ann.label,
                                ann.content,
                                note.value,
                            )
                            list_txts = dic_res[label].keys()
                            if text in list_txts and note_value not in dic_res[label][text]:
                                dic_res[label][text].append(note_value)

        # sort dict
        sorted_dict = dict(sorted(dic_res.items()))

        if path_json_file != "":
            # Writing to my_json_file.json
            with open(path_json_file, "w", encoding="utf8") as outfile:
                json.dump(sorted_dict, outfile, indent=4, ensure_ascii=False)

        return sorted_dict


class Document(BaseModel):
    """A document (usually a txt file), which can be linked to one or multiple AnnotationCollection"""

    # Class arguments
    fullpath: str  # absolute path to the txt file
    version: str = "0.0.1"
    comment: str = "Empty comment"
    annotation_collections: list[AnnotationCollection] = []

    # Other arguments determined by the validators
    text: str = ""  # text content
    folderpath: str = ""  # absolute path to the directory which contains the txt file
    filename_without_ext: str = ""
    extension: str = ""

    class Config:
        validate_assignment = True

    @field_validator("fullpath", "version", "comment")
    def validate_doc_str_input(cls, v):
        if type(v) is str and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized Document (fullpath, version and comment must be non-empty strings)\n",
        )

    @field_validator("annotation_collections")
    def validate_annotation_collections(cls, v):
        if isinstance(v, list):
            if len(v) == 0:
                return []
            if all(isinstance(item, AnnotationCollection) for item in v):
                return v
        raise ParsingError(
            "Badly initialized Document (annotation_collections must be a list of AnnotationCollection instances)\n",
        )

    @field_validator("text")
    def validate_text(cls, v):
        if isinstance(v, str) and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized Document (text must be a non-empty string)\n",
        )

    @model_validator(mode="after")
    def prepare_other_metadata(self):
        # we use object.__setattr_ to bypass the validation process after assignment using self
        # which avoids unlimited recursion
        object.__setattr__(self, "folderpath", dirname(self.fullpath))
        filename_without_ext, extension = splitext(basename(self.fullpath))
        object.__setattr__(self, "filename_without_ext", filename_without_ext)
        object.__setattr__(self, "extension", extension)
        return self

    def add_annotation_collection(
        self,
        ann_collect: AnnotationCollection,
    ) -> None:
        """Add an Annotation Collection, with optional metadata options"""
        self.annotation_collections.append(ann_collect)

    def __str__(self) -> str:
        return f"Document\n fullpath: {self.fullpath}\n version: {self.version}\n description: {self.comment}\n number of annotation sets: {len(self.annotation_collections)}"

    def remove_contained_annotations(self) -> None:
        """Apply AnnCollection's remove_contained_annotations in all of our annotations"""
        for acol in self.annotation_collections:
            acol.remove_contained_annotations()

    def replace_annotation_labels(
        self,
        old_name: str,
        new_name: str,
        specific_type=None,
        all_labels: bool = False,
    ) -> None:
        """Apply AnnCollection's remove_annotation_labels in all of our annotations"""
        for acol in self.annotation_collections:
            acol.replace_annotation_labels(
                old_name,
                new_name,
                specific_type,
                all_labels=all_labels,
            )

    def get_txt_content(
        self,
        encoding="UTF-8",
        split_lines=False,
        untranslated_crlf=False,
    ) -> Union[str, list[str]]:
        """Open txt file present in fullpath argument and return its content"""
        fread = open(self.fullpath, encoding=encoding) if not untranslated_crlf else open(self.fullpath, encoding=encoding, newline="")  # noqa: SIM115
        content: Union[str, list[str]] = fread.readlines() if split_lines else fread.read()
        fread.close()
        return content

    def check_ann_compatibility_with_txt(self) -> bool:
        """Check whether the ann files is compatible with the txt file (i.e. the indices and their corresponding contents are found in the txt)"""
        content = self.get_txt_content()
        assert isinstance(content, str)
        for ann_collect in self.annotation_collections:
            entities = ann_collect.get_annotations(descendant_type=EntityAnnotation)
            for ent in entities:
                # sanity check, but should never happen
                if not isinstance(ent, EntityAnnotation):
                    raise TypeError(
                        "It should never happen because it should contain only entities.",
                    )
                if len(ent.fragments) == 1:
                    subcontent = content[ent.fragments[0].start : ent.fragments[0].end]
                    subcontent = subcontent.replace("\n", " ")
                    if subcontent != ent.content:
                        print(
                            "The annotation is not matching with the file",
                            self.fullpath,
                        )
                        print("The issue is the following annotation:", ent.id)
                        return False
                else:
                    buffer = 0
                    for frag in ent.fragments:
                        length_exp = frag.end - frag.start
                        subcontent = content[frag.start : frag.end]
                        subcontent = subcontent.replace("\n", " ")
                        if subcontent != ent.content[buffer : buffer + length_exp]:
                            print(
                                "The annotation is not matching with the file",
                                self.fullpath,
                            )
                            print("The issue is the following annotation:", ent.id)
                            return False
                        # update the buffer
                        buffer += length_exp
                        # also add the space because next fragment
                        buffer += 1
        return True

    def fix_ann_encoded_with_crlf(self, anncol_indice=0) -> None:
        """Function which consists in fixing the ann indices in case it has been written while taking the CRLF as two characters"""
        if not self.annotation_collections:
            print("Ann file is empty - no clean to do there.")
            return
        if len(self.annotation_collections) == 0:
            print("Ann file is empty - no clean to do there.")
            return
        if anncol_indice >= len(self.annotation_collections):
            print(
                "Index out of bounds: there is no annotation collection at index",
                anncol_indice,
            )
        else:
            my_ann_col = self.annotation_collections[anncol_indice]
            fixed_ann_col = AnnotationCollection(annotations=[])
            content_crlf = self.get_txt_content(untranslated_crlf=True)
            assert isinstance(content_crlf, str)
            for annot in my_ann_col.get_annotations():
                if isinstance(annot, EntityAnnotation):
                    # fix
                    new_fragments: list[Fragment] = []
                    for frag in annot.fragments:
                        fixed_start = frag.start - content_crlf.count(
                            "\r",
                            0,
                            frag.start,
                        )
                        fixed_end = frag.end - content_crlf.count("\r", 0, frag.end)
                        new_fragments.append(Fragment(start=fixed_start, end=fixed_end))
                    annot.fragments = new_fragments
                fixed_ann_col.add_annotation(annot)
            # fixed
            self.annotation_collections[anncol_indice] = fixed_ann_col

    def stats_annotation_types(self, verbose: bool = False) -> dict[type, int]:
        """Counts types of annotation (Entities count, Relations count, etc) in the list of annotation collections"""
        dico: dict[type, int] = {}

        dico_anns: list[dict[type, int]] = [ac.stats_annotation_types(verbose=False) for ac in self.annotation_collections]

        for dico_ann in dico_anns:
            for k in dico_ann:
                if k not in dico:
                    dico[k] = dico_ann[k]
                else:
                    dico[k] += dico_ann[k]

        if verbose:
            for k, value in dico.items():
                print("Type:", str(k), ":", str(value), "annotations.")
        return dico

    def stats_labels_given_annot_type(
        self,
        descendant_type: type = EntityAnnotation,
        verbose: bool = False,
    ) -> dict[str, int]:
        """Gives labels statistics count, for a given AnnotationType in the list of annotation collections"""
        dico: dict[str, int] = {}

        dico_anns: list[dict[str, int]] = [
            ac.stats_labels_given_annot_type(
                verbose=False,
                descendant_type=descendant_type,
            )
            for ac in self.annotation_collections
        ]

        for dico_ann in dico_anns:
            for k in dico_ann:
                if k not in dico:
                    dico[k] = dico_ann[k]
                else:
                    dico[k] += dico_ann[k]

        if verbose:
            print("For the following type:", descendant_type, ", we have:")
            for k, value in dico.items():
                print(str(value), "annotations with label:", k)
        return dico

    def stats_entity_contents_given_label(
        self,
        label: str = "",
        verbose: bool = False,
    ) -> dict[str, int]:
        """Gives entity content statistics count, for a given label, or for all entities if label is not given, in the list of annotation collection"""
        dico: dict[str, int] = {}

        dico_anns: list[dict[str, int]] = [ac.stats_entity_contents_given_label(verbose=False, label=label) for ac in self.annotation_collections]

        for dico_ann in dico_anns:
            for k in dico_ann:
                if k not in dico:
                    dico[k] = dico_ann[k]
                else:
                    dico[k] += dico_ann[k]

        if verbose:
            # sort dico in descending order
            dico = dict(sorted(dico.items(), key=itemgetter(1), reverse=True))
            if label == "":
                print("Among all entities, we have:")
                for k, value in dico.items():
                    print(str(value), "annotations with content:", k)
            else:
                print("Among entities with label", label, ", we have:")
                for k, value in dico.items():
                    print(str(value), "annotations with content:", k)
        return dico

    def remove_annotations_given_label(self, targeted_label) -> None:
        """Remove all annotations that have a specific label, for the whole document"""
        for acol in self.annotation_collections:
            acol.remove_annotations_given_label(targeted_label)


class DocumentCollection(BaseModel):
    """A set of documents (usually a set of txt file stored in a folder)"""

    # metadata
    folderpath: str = ""
    version: str = "0.0.1"
    comment: str = "Empty comment"
    # actual data
    documents: list[Document] = []

    class Config:
        validate_assignment = True

    @field_validator("folderpath", "version", "comment")
    def validate_doccol_str_input(cls, v):
        if type(v) is str and len(v) > 0:
            return v
        raise ParsingError(
            "Badly initialized DocumentCollection (folderpath, version and comment must be non-empty strings)\n",
        )

    @field_validator("documents")
    def validate_doccol_docs_input(cls, v):
        if isinstance(v, list):
            if len(v) == 0:
                return []
            if all(isinstance(doc, Document) for doc in v):
                return v
        raise ParsingError(
            "Badly initialized DocumentCollection (documents must be a list of Document instances)\n",
        )

    def __len__(self):
        return len(self.documents)

    def add_document(self, document: Document) -> None:
        """Add a document in the list"""
        self.documents.append(document)

    def __str__(self) -> str:
        return f"Document Collection\n folderpath: {self.folderpath}\n version: {self.version}\n description: {self.comment}\n number of documents: {len(self.documents)}"

    def remove_contained_annotations(self) -> None:
        """Apply AnnCollection's remove_contained_annotations in all of our documents"""
        for doc in self.documents:
            doc.remove_contained_annotations()

    def replace_annotation_labels(
        self,
        old_name: str,
        new_name: str,
        specific_type=None,
        all_labels: bool = False,
    ) -> None:
        """Apply AnnCollection's remove_annotation_labels in all of our documents"""
        for doc in self.documents:
            doc.replace_annotation_labels(
                old_name,
                new_name,
                specific_type,
                all_labels=all_labels,
            )

    def check_ann_compatibility_with_txt(self) -> bool:
        """Check whether the ann files is compatible with the txt files, for each Document"""
        return all(d.check_ann_compatibility_with_txt() is not False for d in self.documents)

    def fix_ann_encoded_with_crlf(self) -> None:
        """Function which consists in fixing the ann indices in case it has been written while taking the CRLF as two characters, for each document"""
        for d in self.documents:
            d.fix_ann_encoded_with_crlf(anncol_indice=0)

    def stats_annotation_types(self, verbose: bool = False) -> dict[type, int]:
        """Counts types of annotation (Entities count, Relations count, etc) in the list of documents"""
        dico: dict[type, int] = {}

        dico_docs: list[dict[type, int]] = [doc.stats_annotation_types(verbose=False) for doc in self.documents]

        for dico_doc in dico_docs:
            for k in dico_doc:
                if k not in dico:
                    dico[k] = dico_doc[k]
                else:
                    dico[k] += dico_doc[k]

        if verbose:
            for k, value in dico.items():
                print("Type:", str(k), ":", str(value), "annotations.")
        return dico

    def stats_labels_given_annot_type(
        self,
        descendant_type: type = EntityAnnotation,
        verbose: bool = False,
    ) -> dict[str, int]:
        """Gives labels statistics count, for a given AnnotationType in the list of documents"""
        dico: dict[str, int] = {}

        dico_docs: list[dict[str, int]] = [
            doc.stats_labels_given_annot_type(
                verbose=False,
                descendant_type=descendant_type,
            )
            for doc in self.documents
        ]

        for dico_doc in dico_docs:
            for k in dico_doc:
                if k not in dico:
                    dico[k] = dico_doc[k]
                else:
                    dico[k] += dico_doc[k]

        if verbose:
            print("For the following type:", descendant_type, ", we have:")
            for k, value in dico.items():
                print(str(value), "annotations with label:", k)
        return dico

    def stats_entity_contents_given_label(
        self,
        label: str = "",
        verbose: bool = False,
    ) -> dict[str, int]:
        """Gives entity content statistics count, for a given label, or for all entities if label is not given, in the list of documents"""
        dico: dict[str, int] = {}

        dico_docs: list[dict[str, int]] = [doc.stats_entity_contents_given_label(verbose=False, label=label) for doc in self.documents]

        for dico_doc in dico_docs:
            for k in dico_doc:
                if k not in dico:
                    dico[k] = dico_doc[k]
                else:
                    dico[k] += dico_doc[k]

        if verbose:
            # sort dico in descending order
            dico = dict(sorted(dico.items(), key=itemgetter(1), reverse=True))
            if label == "":
                print("Among all entities, we have:")
                for k, value in dico.items():
                    print(str(value), "annotations with content:", k)
            else:
                print("Among entities with label", label, ", we have:")
                for k, value in dico.items():
                    print(str(value), "annotations with content:", k)
        return dico

    def remove_annotations_given_label(self, targeted_label) -> None:
        """Remove all annotations that have a specific label, for the whole document collection"""
        for doc in self.documents:
            doc.remove_annotations_given_label(targeted_label)
