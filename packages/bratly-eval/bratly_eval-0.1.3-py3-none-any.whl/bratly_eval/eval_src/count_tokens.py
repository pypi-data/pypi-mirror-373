"""
Provide functions to count tokens and annotations in document collections and to collect statistics about annotated categories.

Functions:
    - count_tokens_and_anns(folder: Path) -> tuple:
        Counts the total number of tokens and annotated tokens in a document collection.

    - stat_ann_categories(paths: list[Path|str], stats: dict = None, depth: int = 0) -> dict:
        Collects and prints statistics about annotated categories in documents, including the number of tokens,
        annotated tokens, annotations, and documents, as well as the occurrences of each annotation type.
"""

from pathlib import Path

import pandas as pd
from bratly import DocumentCollection, EntityAnnotation
from bratly_io_fs import read_document_collection_from_folder
from tqdm import tqdm


def count_tokens_and_anns(folder: Path):
    """
    Count the number of tokens and annotated tokens in documents within a specified folder.

    Args:
        folder (Path): The path to the folder containing the documents.

    Returns:
        tuple: A tuple containing:
            - int: The number of documents.
            - int: The total number of tokens.
            - int: The total number of annotated tokens.

    """
    n_ann_tokens, n_tokens = 0, 0
    doc_coll: DocumentCollection | None = read_document_collection_from_folder(str(folder))
    if doc_coll is None:
        return 0, 0, 0
    print("counting tokens and annotated token")

    doc_coll.replace_annotation_labels("", "label", specific_type=None, all_labels=True)
    for i_doc, doc in enumerate(doc_coll.documents):
        print(i_doc + 1, "/", len(doc_coll.documents), end="\r")
        doc_coll.documents[i_doc].annotation_collections[0].remove_contained_annotations()
        doc_coll.documents[i_doc].annotation_collections[0].remove_duplicates()
        for ann in doc_coll.documents[i_doc].annotation_collections[0].annotations:
            if isinstance(ann, EntityAnnotation):
                n_ann_tokens += len(ann.content.replace("\n", " ").replace("\t", " ").split())

        n_tokens += len(doc.text.replace("\n", " ").replace("\t", " ").split())
    print()
    return len(doc_coll.documents), n_tokens, n_ann_tokens


def stat_ann_categories(paths: list[Path | str], stats: dict | None = None, depth: int = 0, max_depth: int = 0) -> dict:
    """
    Collects and prints statistics about annotated categories in documents.
    """
    if stats is None:
        stats = {
            "n_tokens": 0,
            "n_annotated_tokens": 0,
            "n_annotations": 0,
            "n_documents": 0,
            "ann_types": {},
        }

    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        if isinstance(path, str):
            path = Path(path)  # noqa: PLW2901

        items = list(path.iterdir())
        if depth < max_depth:
            print("iterating", len(items), "items in", path)
            for item in tqdm(items):
                if item.is_dir():
                    stats = stat_ann_categories([item], stats=stats, depth=depth + 1)

        doc_coll: DocumentCollection | None = read_document_collection_from_folder(str(path))
        if doc_coll is not None:
            for doc in doc_coll.documents:
                for ann in doc.annotation_collections[0].annotations:
                    stats["ann_types"][ann.label] = stats["ann_types"].get(ann.label, 0) + 1
                stats["n_tokens"] += len(doc.text.replace("\n", " ").replace("\t", " ").split())
                stats["n_annotated_tokens"] += sum(
                    [len(ann.content.replace("\n", " ").replace("\t", " ").split()) for ann in doc.annotation_collections[0].annotations if isinstance(ann, EntityAnnotation)],
                )
                stats["n_annotations"] += len(doc.annotation_collections[0].annotations)
                stats["n_documents"] += 1

    if depth == 0:
        # remove 'text_spurious' from the statistics
        if "text_spurious" in stats["ann_types"]:
            del stats["ann_types"]["text_spurious"]

        my_df = pd.DataFrame(stats["ann_types"].items(), columns=["label", "count"])
        my_df["percentage"] = 100 * my_df["count"] / my_df["count"].sum()
        my_df = my_df.sort_values("count", ascending=False)
        del stats["ann_types"]
        print(my_df)
        print(stats)
        print("Percentage of annotated tokens: ", 100 * stats["n_annotated_tokens"] / stats["n_tokens"])

    return stats
