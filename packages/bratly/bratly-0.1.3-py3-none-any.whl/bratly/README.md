<a id="collection_types"></a>

# collection\_types

<a id="collection_types.AnnotationCollection"></a>

## AnnotationCollection Objects

```python
class AnnotationCollection(BaseModel)
```

A set of Annotations, one txt file can be linked to one or multiple AnnotationCollection (multiple versions, different annot types...)

<a id="collection_types.AnnotationCollection.get_annotations"></a>

#### get\_annotations

```python
def get_annotations(
    descendant_type=None
) -> Union[
        list[Annotation],
        list[EntityAnnotation],
        list[RelationAnnotation],
        list[EventAnnotation],
        list[EquivalenceAnnotation],
        list[NormalizationAnnotation],
        list[NoteAnnotation],
]
```

Getter method for annotations, two use cases:
1- Gives all annotations by default
2- Gives a list of a particular type of annotation if the descendant_type argument os used

<a id="collection_types.AnnotationCollection.remove_orphan_notes"></a>

#### remove\_orphan\_notes

```python
def remove_orphan_notes()
```

Delete Notes, Relations, Events, Equivalences, Normalizations and Attributes if they link towards a non-existant Entity

<a id="collection_types.AnnotationCollection.remove_duplicates"></a>

#### remove\_duplicates

```python
def remove_duplicates() -> None
```

Remove duplicates annotation

<a id="collection_types.AnnotationCollection.replace_annotation_labels"></a>

#### replace\_annotation\_labels

```python
def replace_annotation_labels(old_name: str,
                              new_name: str,
                              specific_type: str = None,
                              all_labels: bool = False) -> None
```

Replace annotations label by another one

<a id="collection_types.AnnotationCollection.remove_contained_annotations"></a>

#### remove\_contained\_annotations

```python
def remove_contained_annotations() -> None
```

Remove contained annotations, that is, annotations that are contained in another one, with the same tag
Notes: multi-fragment entities are ignored

<a id="collection_types.AnnotationCollection.renum"></a>

#### renum

```python
def renum(renum_start: int = 0) -> None
```

Renumerotize Annotations

<a id="collection_types.AnnotationCollection.combine"></a>

#### combine

```python
def combine(anns: "AnnotationCollection", with_renum=False) -> None
```

Extends self.annotations

<a id="collection_types.AnnotationCollection.keep_specific_annotations"></a>

#### keep\_specific\_annotations

```python
def keep_specific_annotations(labels: list[str],
                              annot_type=EntityAnnotation) -> None
```

Delete all annotations that are not EntityAnnotation (or another type) associated with one of the labels in the list
this function is useful when you want to transform ann files which contains multiple labels (anatomie, substance, etc.)
to another which contains only one of those labels.

<a id="collection_types.AnnotationCollection.remove_annotations_given_label"></a>

#### remove\_annotations\_given\_label

```python
def remove_annotations_given_label(targeted_label) -> None
```

Remove all annotations that have a specific label

<a id="collection_types.AnnotationCollection.stats_annotation_types"></a>

#### stats\_annotation\_types

```python
def stats_annotation_types(verbose: bool = False) -> dict[type, int]
```

Counts types of annotation (Entities count, Relations count, etc)

<a id="collection_types.AnnotationCollection.stats_labels_given_annot_type"></a>

#### stats\_labels\_given\_annot\_type

```python
def stats_labels_given_annot_type(descendant_type: type = EntityAnnotation,
                                  verbose: bool = False) -> dict[str, int]
```

Gives labels statistics count, for a given AnnotationType

<a id="collection_types.AnnotationCollection.stats_entity_contents_given_label"></a>

#### stats\_entity\_contents\_given\_label

```python
def stats_entity_contents_given_label(label: str = "",
                                      verbose: bool = False) -> dict[str, int]
```

Gives entity content statistics count, for a given label, or for all entities if label is not given

<a id="collection_types.AnnotationCollection.to_json"></a>

#### to\_json

```python
def to_json(path_json_file: str = "") -> dict[str, dict[str, List[Any]]]
```

Save ann data as json file

<a id="collection_types.Document"></a>

## Document Objects

```python
class Document(BaseModel)
```

A document (usually a txt file), which can be linked to one or multiple AnnotationCollection

<a id="collection_types.Document.add_annotation_collection"></a>

#### add\_annotation\_collection

```python
def add_annotation_collection(ann_collect: AnnotationCollection,
                              version: str = "",
                              comment: str = "") -> None
```

Add an Annotation Collection, with optional metadata options

<a id="collection_types.Document.remove_contained_annotations"></a>

#### remove\_contained\_annotations

```python
def remove_contained_annotations() -> None
```

Apply AnnCollection's remove_contained_annotations in all of our annotations

<a id="collection_types.Document.replace_annotation_labels"></a>

#### replace\_annotation\_labels

```python
def replace_annotation_labels(old_name: str,
                              new_name: str,
                              specific_type=None,
                              all_labels: bool = False) -> None
```

Apply AnnCollection's remove_annotation_labels in all of our annotations

<a id="collection_types.Document.get_txt_content"></a>

#### get\_txt\_content

```python
def get_txt_content(encoding="UTF-8",
                    split_lines=False,
                    untranslated_crlf=False) -> Union[str, list[str]]
```

Open txt file present in fullpath argument and return its content

<a id="collection_types.Document.check_ann_compatibility_with_txt"></a>

#### check\_ann\_compatibility\_with\_txt

```python
def check_ann_compatibility_with_txt() -> bool
```

Check whether the ann files is compatible with the txt file (i.e. the indices and their corresponding contents are found in the txt)

<a id="collection_types.Document.fix_ann_encoded_with_crlf"></a>

#### fix\_ann\_encoded\_with\_crlf

```python
def fix_ann_encoded_with_crlf(anncol_indice=0) -> None
```

Function which consists in fixing the ann indices in case it has been written while taking the CRLF as two characters

<a id="collection_types.Document.stats_annotation_types"></a>

#### stats\_annotation\_types

```python
def stats_annotation_types(verbose: bool = False) -> dict[type, int]
```

Counts types of annotation (Entities count, Relations count, etc) in the list of annotation collections

<a id="collection_types.Document.stats_labels_given_annot_type"></a>

#### stats\_labels\_given\_annot\_type

```python
def stats_labels_given_annot_type(descendant_type: type = EntityAnnotation,
                                  verbose: bool = False) -> dict[str, int]
```

Gives labels statistics count, for a given AnnotationType in the list of annotation collections

<a id="collection_types.Document.stats_entity_contents_given_label"></a>

#### stats\_entity\_contents\_given\_label

```python
def stats_entity_contents_given_label(label: str = "",
                                      verbose: bool = False) -> dict[str, int]
```

Gives entity content statistics count, for a given label, or for all entities if label is not given, in the list of annotation collection

<a id="collection_types.Document.remove_annotations_given_label"></a>

#### remove\_annotations\_given\_label

```python
def remove_annotations_given_label(targeted_label) -> None
```

Remove all annotations that have a specific label, for the whole document

<a id="collection_types.DocumentCollection"></a>

## DocumentCollection Objects

```python
class DocumentCollection(BaseModel)
```

A set of documents (usually a set of txt file stored in a folder)

<a id="collection_types.DocumentCollection.add_document"></a>

#### add\_document

```python
def add_document(document: Document) -> None
```

Add a document in the list

<a id="collection_types.DocumentCollection.remove_contained_annotations"></a>

#### remove\_contained\_annotations

```python
def remove_contained_annotations() -> None
```

Apply AnnCollection's remove_contained_annotations in all of our documents

<a id="collection_types.DocumentCollection.replace_annotation_labels"></a>

#### replace\_annotation\_labels

```python
def replace_annotation_labels(old_name: str,
                              new_name: str,
                              specific_type=None,
                              all_labels: bool = False) -> None
```

Apply AnnCollection's remove_annotation_labels in all of our documents

<a id="collection_types.DocumentCollection.check_ann_compatibility_with_txt"></a>

#### check\_ann\_compatibility\_with\_txt

```python
def check_ann_compatibility_with_txt() -> bool
```

Check whether the ann files is compatible with the txt files, for each Document

<a id="collection_types.DocumentCollection.fix_ann_encoded_with_crlf"></a>

#### fix\_ann\_encoded\_with\_crlf

```python
def fix_ann_encoded_with_crlf() -> None
```

Function which consists in fixing the ann indices in case it has been written while taking the CRLF as two characters, for each document

<a id="collection_types.DocumentCollection.stats_annotation_types"></a>

#### stats\_annotation\_types

```python
def stats_annotation_types(verbose: bool = False) -> dict[type, int]
```

Counts types of annotation (Entities count, Relations count, etc) in the list of documents

<a id="collection_types.DocumentCollection.stats_labels_given_annot_type"></a>

#### stats\_labels\_given\_annot\_type

```python
def stats_labels_given_annot_type(descendant_type: type = EntityAnnotation,
                                  verbose: bool = False) -> dict[str, int]
```

Gives labels statistics count, for a given AnnotationType in the list of documents

<a id="collection_types.DocumentCollection.stats_entity_contents_given_label"></a>

#### stats\_entity\_contents\_given\_label

```python
def stats_entity_contents_given_label(label: str = "",
                                      verbose: bool = False) -> dict[str, int]
```

Gives entity content statistics count, for a given label, or for all entities if label is not given, in the list of documents

<a id="collection_types.DocumentCollection.remove_annotations_given_label"></a>

#### remove\_annotations\_given\_label

```python
def remove_annotations_given_label(targeted_label) -> None
```

Remove all annotations that have a specific label, for the whole document collection

<a id="annotation_types"></a>

# annotation\_types

<a id="annotation_types.Fragment"></a>

## Fragment Objects

```python
class Fragment(BaseModel)
```

A fragment of text within an entity annotation. Defined by starting and ending character positions

<a id="annotation_types.Annotation"></a>

## Annotation Objects

```python
class Annotation(BaseModel)
```

A generic type of annotation. Can be EntityAnnotation, RelationAnnotation, AttributeAnnotation, NormalizationAnnotation, NoteAnnotation, EquivalenceAnnotation. Defined by its id

<a id="annotation_types.EntityAnnotation"></a>

## EntityAnnotation Objects

```python
class EntityAnnotation(Annotation)
```

A type of Annotation, annotation of a text segment. Defined by a list of fragments (usually 1), the text content, and the label (category), as in ann file. e.g T1	Name 34 55	Père Noël

<a id="annotation_types.RelationAnnotation"></a>

## RelationAnnotation Objects

```python
class RelationAnnotation(Annotation)
```

A type of Annotation, a relation between two EntityAnnotations.

<a id="annotation_types.AttributeAnnotation"></a>

## AttributeAnnotation Objects

```python
class AttributeAnnotation(Annotation)
```

A type of Annotation, an attribute linked to an EntityAnnotation

<a id="__init__"></a>

# \_\_init\_\_

