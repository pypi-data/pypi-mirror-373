<a id="__init__"></a>

# \_\_init\_\_

<a id="__init__.FragmentAgreement"></a>

## FragmentAgreement Objects

```python
class FragmentAgreement(BaseModel)
```

Object describing the similarity between two fragments (gold_frag, parallel_frag).
Flag is correct if ends and starts are the same,
partial if there is a non-empty intersection between the fragments, but either start or end or both differ.
For partial 8 cases exist (see readme)
Flag is spurious if there is no corresponding gold for parallel,
missing if there is no corresponding parallel for gold.

<a id="__init__.FragmentAgreement.flag"></a>

#### flag

0: correct, `1`-8: partial 1-8, `9`: spurious, `10`: missing

<a id="__init__.FragmentAgreement.__init__"></a>

#### \_\_init\_\_

```python
def __init__(gold_frag: Fragment = None,
             parallel_frag: Fragment = None) -> None
```

Init: Either gold or parallel fragment have to be specified

<a id="__init__.FragmentAgreement.tag_from_flag"></a>

#### tag\_from\_flag

```python
def tag_from_flag() -> str
```

Returns the str name of the flag stored as an integer

<a id="__init__.FragmentAgreement.contains"></a>

#### contains

```python
def contains(other: "FragmentAgreement") -> bool
```

Returns whether the the scope of current agreement is larger then that of the other.

<a id="__init__.FragmentAgreement.is_distinct"></a>

#### is\_distinct

```python
def is_distinct(others: list["FragmentAgreement"]) -> bool
```

Returns whether it is distinct from any other agreements in the list.

<a id="__init__.FragmentAgreement.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

For printing: returns the flag of the agreement and the two fragmentes compared

<a id="__init__.FragmentAgreement.__lt__"></a>

#### \_\_lt\_\_

```python
def __lt__(other: Any) -> bool
```

Returns whether the scope of the current FragmentAgreement is occuring earlier than that of the others.
The scope occurs earlier if it starts earlier, or - in case of same start - it ends earlier.
For missing and spurious agreements, the scope is defined here as the scope of the missing or spurious fragment.

<a id="__init__.Agreement"></a>

## Agreement Objects

```python
class Agreement(BaseModel)
```

Object describing the similiraty between two entity annotations (gold, parallel).
Flag is correct if ends and starts are the same and the two annotations have the same type;
Incorrect if ends and starts are the same but the types are different;
Partial if there is a non-empty intersection between the fragments, but either start or end or both differ and the type is the same,
Related if the match is partial but the types are different.
There are 2 cases for partial and for related flags, if there is partial/correct match between all fragments or when only between some of them.
Flag is spurious if there is no corresponding gold for parallel,
missing if there is no corresponding parallel for gold.

<a id="__init__.Agreement.flag"></a>

#### flag

0: correct, 1: incorrect, 2: missing, 3: spurious

<a id="__init__.Agreement.merge_inclusive"></a>

#### merge\_inclusive

```python
@staticmethod
def merge_inclusive(fr1: Fragment, fr2: Fragment) -> Fragment
```

Helper function returning the maximum scope (union) of two intersecting fragments

<a id="__init__.Agreement.merge_exclusive"></a>

#### merge\_exclusive

```python
@staticmethod
def merge_exclusive(fr1: Fragment, fr2: Fragment) -> Union[Fragment, None]
```

Helper function returning the minimum scope (intersection) of two intersecting fragments

<a id="__init__.Agreement.union"></a>

#### union

```python
@staticmethod
def union(fragments: list[FragmentAgreement]) -> list[Fragment]
```

Helper function returning the union of FragmentAgreements (i.e. eliminating duplicates)

<a id="__init__.Agreement.intersect"></a>

#### intersect

```python
@staticmethod
def intersect(fragments: list[FragmentAgreement]) -> list[Fragment]
```

Helper function returning the intersection of FragmentAgreements (contained by all of them)

<a id="__init__.Agreement.flag_in_str"></a>

#### flag\_in\_str

```python
def flag_in_str() -> str
```

Helper function converting the flag to the corresponding string

<a id="__init__.Agreement.annotation_to_csv"></a>

#### annotation\_to\_csv

```python
@staticmethod
def annotation_to_csv(ann: EntityAnnotation, filename="")
```

Converts one line of annotation to CSV format (part of one line)

<a id="__init__.Agreement.to_csv"></a>

#### to\_csv

```python
def to_csv(filename: str = None) -> str
```

Converts an agreement to one line of CSV file

<a id="__init__.MucTable"></a>

## MucTable Objects

```python
class MucTable(BaseModel)
```

Data structure object reflecting the parameters of MUC-7 scoring scheme.
Extended with some additional parameters

<a id="__init__.MucTable.get_statistics"></a>

#### get\_statistics

```python
def get_statistics(
        comparison_type: int = RELAXED_COMPARISON) -> dict[str, float]
```

Returns the most importantant statistics values for the comparison
as a dictionary.

<a id="__init__.MucCollection"></a>

## MucCollection Objects

```python
class MucCollection(BaseModel)
```

Class describing the comparison between several pairs of files.
A collection of MucTables

<a id="count_tokens"></a>

# count\_tokens

This module provides functions to count tokens and annotations in document collections and to collect statistics about annotated categories.

Functions:
    - count_tokens_and_anns(folder: Path) -> tuple:
        Counts the total number of tokens and annotated tokens in a document collection.

    - stat_ann_categories(paths: list[Path|str], stats: dict = None, depth: int = 0) -> dict:
        Collects and prints statistics about annotated categories in documents, including the number of tokens, annotated tokens, annotations, and documents, as well as the occurrences of each annotation type.

<a id="count_tokens.count_tokens_and_anns"></a>

#### count\_tokens\_and\_anns

```python
def count_tokens_and_anns(folder: Path, max_n: int = -1)
```

Count the number of tokens and annotated tokens in documents within a specified folder.

**Arguments**:

- `folder` _Path_ - The path to the folder containing the documents.
  

**Returns**:

- `tuple` - A tuple containing:
  - int: The number of documents.
  - int: The total number of tokens.
  - int: The total number of annotated tokens.

<a id="count_tokens.stat_ann_categories"></a>

#### stat\_ann\_categories

```python
def stat_ann_categories(paths: list[Path | str],
                        max_n: int = -1,
                        stats: dict = None,
                        depth: int = 0,
                        max_depth: int = 0) -> dict
```

Collects and prints statistics about annotated categories in documents.

<a id="compare_batch"></a>

# compare\_batch

<a id="compare_batch.compare_batch"></a>

#### compare\_batch

```python
def compare_batch(batch: dict, write_files: bool = True, max_n: int = -1)
```

both folders must be flat

<a id="__init__"></a>

# \_\_init\_\_

<a id="__init__.FragmentAgreement"></a>

## FragmentAgreement Objects

```python
class FragmentAgreement(BaseModel)
```

Object describing the similarity between two fragments (gold_frag, parallel_frag).
Flag is correct if ends and starts are the same,
partial if there is a non-empty intersection between the fragments, but either start or end or both differ.
For partial 8 cases exist (see readme)
Flag is spurious if there is no corresponding gold for parallel,
missing if there is no corresponding parallel for gold.

<a id="__init__.FragmentAgreement.flag"></a>

#### flag

0: correct, `1`-8: partial 1-8, `9`: spurious, `10`: missing

<a id="__init__.FragmentAgreement.__init__"></a>

#### \_\_init\_\_

```python
def __init__(gold_frag: Fragment = None,
             parallel_frag: Fragment = None) -> None
```

Init: Either gold or parallel fragment have to be specified

<a id="__init__.FragmentAgreement.tag_from_flag"></a>

#### tag\_from\_flag

```python
def tag_from_flag() -> str
```

Returns the str name of the flag stored as an integer

<a id="__init__.FragmentAgreement.contains"></a>

#### contains

```python
def contains(other: "FragmentAgreement") -> bool
```

Returns whether the the scope of current agreement is larger then that of the other.

<a id="__init__.FragmentAgreement.is_distinct"></a>

#### is\_distinct

```python
def is_distinct(others: list["FragmentAgreement"]) -> bool
```

Returns whether it is distinct from any other agreements in the list.

<a id="__init__.FragmentAgreement.__str__"></a>

#### \_\_str\_\_

```python
def __str__() -> str
```

For printing: returns the flag of the agreement and the two fragmentes compared

<a id="__init__.FragmentAgreement.__lt__"></a>

#### \_\_lt\_\_

```python
def __lt__(other: Any) -> bool
```

Returns whether the scope of the current FragmentAgreement is occuring earlier than that of the others.
The scope occurs earlier if it starts earlier, or - in case of same start - it ends earlier.
For missing and spurious agreements, the scope is defined here as the scope of the missing or spurious fragment.

<a id="__init__.Agreement"></a>

## Agreement Objects

```python
class Agreement(BaseModel)
```

Object describing the similiraty between two entity annotations (gold, parallel).
Flag is correct if ends and starts are the same and the two annotations have the same type;
Incorrect if ends and starts are the same but the types are different;
Partial if there is a non-empty intersection between the fragments, but either start or end or both differ and the type is the same,
Related if the match is partial but the types are different.
There are 2 cases for partial and for related flags, if there is partial/correct match between all fragments or when only between some of them.
Flag is spurious if there is no corresponding gold for parallel,
missing if there is no corresponding parallel for gold.

<a id="__init__.Agreement.flag"></a>

#### flag

0: correct, 1: incorrect, 2: missing, 3: spurious

<a id="__init__.Agreement.merge_inclusive"></a>

#### merge\_inclusive

```python
@staticmethod
def merge_inclusive(fr1: Fragment, fr2: Fragment) -> Fragment
```

Helper function returning the maximum scope (union) of two intersecting fragments

<a id="__init__.Agreement.merge_exclusive"></a>

#### merge\_exclusive

```python
@staticmethod
def merge_exclusive(fr1: Fragment, fr2: Fragment) -> Union[Fragment, None]
```

Helper function returning the minimum scope (intersection) of two intersecting fragments

<a id="__init__.Agreement.union"></a>

#### union

```python
@staticmethod
def union(fragments: list[FragmentAgreement]) -> list[Fragment]
```

Helper function returning the union of FragmentAgreements (i.e. eliminating duplicates)

<a id="__init__.Agreement.intersect"></a>

#### intersect

```python
@staticmethod
def intersect(fragments: list[FragmentAgreement]) -> list[Fragment]
```

Helper function returning the intersection of FragmentAgreements (contained by all of them)

<a id="__init__.Agreement.flag_in_str"></a>

#### flag\_in\_str

```python
def flag_in_str() -> str
```

Helper function converting the flag to the corresponding string

<a id="__init__.Agreement.annotation_to_csv"></a>

#### annotation\_to\_csv

```python
@staticmethod
def annotation_to_csv(ann: EntityAnnotation, filename="")
```

Converts one line of annotation to CSV format (part of one line)

<a id="__init__.Agreement.to_csv"></a>

#### to\_csv

```python
def to_csv(filename: str = None) -> str
```

Converts an agreement to one line of CSV file

<a id="__init__.MucTable"></a>

## MucTable Objects

```python
class MucTable(BaseModel)
```

Data structure object reflecting the parameters of MUC-7 scoring scheme.
Extended with some additional parameters

<a id="__init__.MucTable.get_statistics"></a>

#### get\_statistics

```python
def get_statistics(
        comparison_type: int = RELAXED_COMPARISON) -> dict[str, float]
```

Returns the most importantant statistics values for the comparison
as a dictionary.

<a id="__init__.MucCollection"></a>

## MucCollection Objects

```python
class MucCollection(BaseModel)
```

Class describing the comparison between several pairs of files.
A collection of MucTables

