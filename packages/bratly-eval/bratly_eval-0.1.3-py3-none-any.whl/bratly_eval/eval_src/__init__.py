import os
from itertools import compress
from typing import Optional, cast

import numpy as np
import pandas as pd
from bratly import AnnotationCollection, Document, DocumentCollection, EntityAnnotation
from bratly_io_fs import (
    copy_txt_from_collection_to_another_path,
    parse_ann_file,
    read_ann_files_from_folder,
    read_document_collection_from_folder,
    write_ann_files_in_folder,
)

from bratly_eval.agreement_types import Agreement, FragmentAgreement, MucCollection, MucTable


def compare_annotations(
    annotation_file: AnnotationCollection,
    gold_standard_file: AnnotationCollection,
    filename: str,
    comparison_style="Naive",
    original_file=None,
) -> tuple[MucTable, str]:
    """
    Compares two annotation files and returns
    * the MucTable describing the similarity between the two files
    * and a string containing the CSV lines corresponding to the comparison of files.
    Several comparison styles are to be implemented. Currently only Naive style is supported.
    * Naive: Includes every match (when there is at least 1 charcter overlap between two annotations)
    and any spurious and missing annotation.
    * Clean: Keeps only the most likely match for every annotations in the gold standard.
    * Largest: Keeps the largest scope of agreement assuming that
        annotations of the same sepearated by only whitespace in the original file might be joined.
    * Brat: Uses the definitions of the Brat standard (no related class, partial only if end matches)
    """
    annotation_entities: list[EntityAnnotation] = cast(list[EntityAnnotation], annotation_file.get_annotations(descendant_type=EntityAnnotation))
    gold_standard_entities: list[EntityAnnotation] = cast(list[EntityAnnotation], gold_standard_file.get_annotations(descendant_type=EntityAnnotation))

    if comparison_style not in ["Naive", "Clean", "Largest", "Brat"]:
        raise NotImplementedError
    if comparison_style == "Largest" and not isinstance(original_file, str):
        raise NotImplementedError

    # Getting all fragments with a tuple key (annotation number, fragment number)
    af1 = sorted(
        [(m, n, f) for m, a in enumerate(annotation_entities) for n, f in enumerate(a.fragments)],
        key=lambda x: x[2],
    )
    af2 = sorted(
        [(m, n, f) for m, a in enumerate(gold_standard_entities) for n, f in enumerate(a.fragments)],
        key=lambda x: x[2],
    )
    if not af1 and not af2:
        return MucTable(agreements=[]), ""
    fragment_agreements1 = [[] for _ in range(len(af1))]
    fragment_agreements2 = [[] for _ in range(len(af2))]
    af2_starts = [a[2].start for a in af2]
    status_af2 = [True for _ in range(len(af2))]
    status_untouched = [True for _ in range(len(af2))]
    ns = list(range(len(af2)))

    j = 0

    # For all fragments in the parallel file find any potentially related gold fragments
    for i, ann1 in enumerate(af1):
        a1 = ann1[2]
        # Restrain search for gold fragments which start before the end of the current fragm
        # but doesn't end before the end of previously processed.
        k = np.searchsorted(af2_starts, a1.end, side="left")
        potential_annotations = list(compress(af2[j:k], status_af2[j:k]))
        potential_indices = list(compress(ns[j:k], status_af2[j:k]))
        if len(potential_annotations) < 1:
            fragment_agreements1[i].append((ann1[0], -1, FragmentAgreement(gold_frag=None, parallel_frag=a1)))
        for idx, ann2 in enumerate(potential_annotations):
            a2 = ann2[2]
            # If the gold fragment ends before this one
            if a2.end < a1.start:
                if len(fragment_agreements2[potential_indices[idx]]) < 1:
                    fragment_agreements2[potential_indices[idx]].append(
                        (-1, ann2[0], FragmentAgreement(gold_frag=a2, parallel_frag=None)),
                    )
                status_af2[potential_indices[idx]] = False
            # If they intersect
            else:
                agreement = (ann1[0], ann2[0], FragmentAgreement(gold_frag=a2, parallel_frag=a1))
                fragment_agreements2[potential_indices[idx]].append(agreement)
                fragment_agreements1[i].append(agreement)
                status_untouched[potential_indices[idx]] = False
        # If all gold fragments ends before this one
        if not fragment_agreements1[i]:
            fragment_agreements1[i].append((ann1[0], -1, FragmentAgreement(gold_frag=None, parallel_frag=a1)))

        # Constrain for the next iteration
        j = np.searchsorted(status_af2, True)

    # Add missing annotation at the end of the file
    for i, ann2 in enumerate(af2[j : len(status_af2)]):
        if len(fragment_agreements2[i + j]) < 1:
            fragment_agreements2[i + j].append(
                (-1, ann2[0], FragmentAgreement(gold_frag=ann2[2], parallel_frag=None)),
            )

    tmp = []
    # Sort FragmentAgreements according the start and end of the agreement
    tmp1 = sorted(
        [fa for sub in fragment_agreements1 for fa in sub],
        key=lambda x: (x[0], x[1]),
    )

    fas = [fa[2] for fa in tmp1]
    last_different = 0
    gold_not_missing = set()
    for i, _ in enumerate(tmp1[:-1]):
        # If the next fragment agreement doesn't concern the same gold and parallel fragments
        if tmp1[i][0] != tmp1[i + 1][0] or tmp1[i][1] != tmp1[i + 1][1]:
            # not spurious
            if tmp1[i][1] != -1:
                tmp.append(
                    Agreement(
                        fragment_agreements=fas[last_different : i + 1],
                        parallel=annotation_entities[tmp1[i][0]],
                        gold=gold_standard_entities[tmp1[i][1]],
                    ),
                )
            # spurious
            else:
                tmp.append(
                    Agreement(
                        fragment_agreements=fas[last_different : i + 1],
                        parallel=annotation_entities[tmp1[i][0]],
                        gold=None,
                    ),
                )
            last_different = i + 1
            gold_not_missing.add(tmp1[i][1])

    # Process the remaining fragment agrements
    if len(tmp1) > 0:
        if tmp1[last_different][1] is not None and tmp1[last_different][1] > -1:
            tmp.append(
                Agreement(
                    fragment_agreements=fas[last_different : len(tmp1)],
                    parallel=annotation_entities[tmp1[last_different][0]],
                    gold=gold_standard_entities[tmp1[last_different][1]],
                ),
            )
        else:
            tmp.append(
                Agreement(
                    fragment_agreements=fas[last_different : len(tmp1)],
                    parallel=annotation_entities[tmp1[last_different][0]],
                    gold=None,
                ),
            )
        gold_not_missing.add(tmp1[last_different][1])
    tmp2 = sorted(
        [fa for sub in fragment_agreements2 for fa in sub],
        key=lambda x: (x[1], x[0]),
    )

    fas = [fa[2] for fa in tmp2]
    last_different = 0
    for i, _ in enumerate(tmp2[:-1]):
        if tmp2[i][1] != tmp2[i + 1][1]:
            if tmp2[i][1] not in gold_not_missing:
                tmp.append(
                    Agreement(
                        fragment_agreements=fas[last_different : i + 1],
                        parallel=None,
                        gold=gold_standard_entities[tmp2[i][1]],
                    ),
                )
            last_different = i + 1

    if len(tmp2) > 0 and tmp2[-1][1] not in gold_not_missing:
        tmp.append(
            Agreement(
                fragment_agreements=fas[last_different:],
                parallel=None,
                gold=gold_standard_entities[tmp2[-1][1]],
            ),
        )
    csv = "".join([c.to_csv(filename=filename) for c in tmp])
    mt = MucTable(agreements=tmp)
    return (mt, csv)


def write_results(
    eval_folder: str = "",
    eval_file: str = "",
    df_agreement: Optional[pd.DataFrame] = None,
    csvc: str = "",
    muc_coll: Optional[MucCollection] = None,
    comparison_type=MucTable.RELAXED_COMPARISON,
    muc_with_help: bool = False,
):
    if eval_folder != "":
        if not os.path.exists(eval_folder):
            os.makedirs(eval_folder)
        assert type(df_agreement) is pd.DataFrame

        missing_counts = df_agreement[df_agreement["eval_tag"] == "MISSING"]["gold_content"].value_counts().reset_index().rename(columns={"index": "gold_content", "gold_content": "count"})

        # 2. Filter and count for SPURIOUS
        spurious_counts = (
            df_agreement[df_agreement["eval_tag"] == "SPURIOUS"]["parallel_content"].value_counts().reset_index().rename(columns={"index": "parallel_content", "parallel_content": "count"})
        )

        with pd.ExcelWriter(os.path.join(eval_folder, eval_file + "_agreement_report.xlsx")) as writer:
            df_agreement.to_excel(writer, sheet_name="original", index=False)
            missing_counts.to_excel(writer, sheet_name="missing_counts", index=False)
            spurious_counts.to_excel(writer, sheet_name="spurious_counts", index=False)

        with open(
            os.path.join(eval_folder, eval_file + "_agreement_report.csv"),
            "w",
            encoding="utf_8",
        ) as f:
            f.write(csvc)

        # Generate the MUC (Message Understanding Conferance) Table (ref: https://github.com/savkov/bratutils)
        print("writing muc table" + os.path.join(eval_folder, eval_file + "_muc_table.txt"))
        with open(
            os.path.join(eval_folder, eval_file + "_muc_table.txt"),
            "w",
            encoding="utf_8",
        ) as f:
            assert type(muc_coll) is MucCollection
            dico_stats = muc_coll.get_global_statistics(
                comparison_type=comparison_type,
                with_help=muc_with_help,
            )
            for k, v in dico_stats.items():
                result = str(k) + "-" + str(v) + "\n"
                f.write(result)


LIST_COLUMNS = [
    "filename",
    "eval_tag",
    "parallel_id",
    "parallel_label",
    "parallel_start",
    "parallel_end",
    "parallel_fragments",
    "parallel_content",
    "gold_id",
    "gold_label",
    "gold_start",
    "gold_end",
    "gold_fragments",
    "gold_content",
    "interval_match",
]
COLUMNS = ",".join(LIST_COLUMNS)
N_COLUMNS = len(COLUMNS.split(","))


def compare_folders(
    parallel_folder: str,
    gold_folder: str,
    header: bool = True,
    eval_folder: str = "",
    eval_file: str = "",
    muc_with_help: bool = False,
    keep_specific_annotations: Optional[list[str]] = None,
    comparison_type=MucTable.RELAXED_COMPARISON,
    verbose: bool = False,
) -> tuple[MucCollection, str, pd.DataFrame]:
    """
    Compares annotation files placed in two parallel folder.
    The function compares files with the same name and returns a MucCollection
    and the content of all agreements in CSV format.
    """
    parallel_texts = read_ann_files_from_folder(parallel_folder)
    gold_texts = read_ann_files_from_folder(gold_folder)
    muc_coll = MucCollection(muc_tables=[])
    csvc = COLUMNS + "\n" if header else ""
    df_agreement = pd.DataFrame(columns=LIST_COLUMNS)

    for fname, text in parallel_texts.items():
        if verbose:
            print("fname", fname)
            print("text", text)
        if fname in gold_texts:
            # print(fname)
            anns_text = parse_ann_file(text, fname)
            anns_gold = parse_ann_file(gold_texts[fname], fname)

            if keep_specific_annotations is not None:
                anns_text.keep_specific_annotations(keep_specific_annotations)
                anns_gold.keep_specific_annotations(keep_specific_annotations)

            mt, csv = compare_annotations(anns_text, anns_gold, fname)
            muc_coll.muc_tables.append(mt)
            csvc += csv

            for line in csv.split("\n"):
                line_split = line.split(",")
                if len(line_split) == N_COLUMNS:
                    df_agreement.loc[len(df_agreement)] = line_split
                else:
                    pass
                # print("wrong number of columns" + str(len(line_split)) + line)

    write_results(
        eval_folder=eval_folder,
        eval_file=eval_file,
        df_agreement=df_agreement,
        csvc=csvc,
        muc_coll=muc_coll,
        comparison_type=comparison_type,
        muc_with_help=muc_with_help,
    )

    return (muc_coll, csvc, df_agreement)


def compare_pairs_of_folders(
    pairs: list[tuple[str, str]],  # parallel, gold
    header: bool = True,
    eval_folder: str = "",
    eval_file: str = "",
    muc_with_help: bool = False,
    keep_specific_annotations: Optional[list[str]] = None,
    comparison_type=MucTable.RELAXED_COMPARISON,
    verbose: bool = False,
) -> tuple[MucCollection, str, pd.DataFrame] | None:
    global_muc_coll = MucCollection(muc_tables=[])
    global_csvc = COLUMNS + "\n" if header else ""
    global_df_agreement = pd.DataFrame(columns=COLUMNS.split(","))

    for pair in pairs:
        print("Comparing", str(pair))
        muc_coll, csvc, df_agreement = compare_folders(
            pair[0],
            pair[1],
            header=False,
            eval_folder="",
            eval_file=eval_file,
            muc_with_help=muc_with_help,
            keep_specific_annotations=keep_specific_annotations,
            comparison_type=comparison_type,
            verbose=verbose,
        )

        global_muc_coll.muc_tables += muc_coll.muc_tables
        global_csvc += csvc
        global_df_agreement = pd.concat([global_df_agreement, df_agreement])

    write_results(
        eval_folder=eval_folder,
        eval_file=eval_file,
        df_agreement=global_df_agreement,
        muc_coll=global_muc_coll,
        csvc=global_csvc,
        comparison_type=comparison_type,
        muc_with_help=muc_with_help,
    )


def compare_many_folders(
    folders: list[str],
    basefolder: str = "",
    header: bool = True,
    eval_folder: str = "",
    muc_with_help: bool = False,
):
    """
    Do 3 comparisons
    == stats by entity types
    == F-scores
    == error types compared to gold
    """
    strout = basefolder
    strout += str(folders) + "\n"
    strout += "\n== stats by entity types\n"
    print("== stats by entity types")
    strout += count_entities_of_many_folders(folders, basefolder=basefolder)

    mc = {}
    csv = {}
    my_df = {}
    stats = {}

    for i in range(1, len(folders)):
        for j in range(i, len(folders)):
            f1 = os.path.join(basefolder, folders[i - 1])
            f2 = os.path.join(basefolder, folders[j])
            strout += f"comparing {f1} {f2}" + "\n"
            print(f"comparing {f1} {f2}")

            mc[f"{i - 1}_{j}"], csv[f"{i - 1}_{j}"], my_df[f"{i - 1}_{j}"] = compare_folders(
                f1,
                f2,
                header=header,
                eval_folder=eval_folder,
                eval_file=f"{folders[i - 1]}_{folders[j]}",
                muc_with_help=muc_with_help,
            )
            stats[f"{i - 1}_{j}"] = mc[f"{i - 1}_{j}"].get_global_statistics()

    strout += "\n== F-scores\n"
    print("== F-scores")
    for j in range(1, len(folders)):
        strout += "\t" + folders[j]
    strout += "\n"
    for i in range(1, len(folders)):
        strout += folders[i - 1]
        strout += "\t" * (i - 1)
        for j in range(i, len(folders)):
            if f"{i - 1}_{j}" in stats:
                strout += f"\t{stats[f'{i - 1}_{j}']['F1']:.2f}"
        strout += "\n"
    strout += "\n"

    print("== error types compared to gold: ", folders[0])
    strout += "\n== error types compared to gold: " + folders[0] + "\n"
    strout += "\t" + folders[0] + " vs.\t" + "\t".join(folders[1:]) + "\n"

    corrects = [str(sum(mc[f"{0}_{i}"].corrects)) for i in range(1, len(folders))]
    strout += "CORRECT\t\t" + "\t".join(corrects) + "\n"

    incorrects = [str(sum(mc[f"{0}_{i}"].incorrects)) for i in range(1, len(folders))]
    strout += "INCORRECT\t" + "\t".join(incorrects) + "\n"

    partials = [str(sum(mc[f"{0}_{i}"].partial_As + mc[f"{0}_{i}"].partial_Ss)) for i in range(1, len(folders))]
    strout += "PARTIAL\t\t" + "\t".join(partials) + "\n"

    missings = [str(sum(mc[f"{0}_{i}"].missings)) for i in range(1, len(folders))]
    strout += "MISSING\t\t" + "\t".join(missings) + "\n"

    spuriouses = [str(sum(mc[f"{0}_{i}"].spuriouses)) for i in range(1, len(folders))]
    strout += "SPURIOUS\t" + "\t".join(spuriouses) + "\n"

    return strout


def count_entities_of_folder(folder, basefolder: str = "") -> tuple[dict, int, int]:
    types = {}
    n_file = 0
    n_ann = 0
    folder = os.path.join(basefolder, folder)

    # print(folder)
    dc = read_document_collection_from_folder(folder)
    assert type(dc) is DocumentCollection
    for doc in dc.documents:
        n_file += 1
        # print(doc.filename_without_ext)
        for anncoll in doc.annotation_collections:
            for ann in anncoll.annotations:
                if isinstance(ann, EntityAnnotation):
                    n_ann += 1
                    if ann.label not in types:
                        types[ann.label] = 0
                    types[ann.label] += 1
    return types, n_file, n_ann


def count_entities_of_many_folders(folders: list[str], basefolder: str = "") -> str:
    types: dict = {}
    type_list: list = []
    n_file = {}
    n_ann = {}
    for folder in folders:
        # print(folder)
        types[folder], n_file[folder], n_ann[folder] = count_entities_of_folder(
            folder,
            basefolder=basefolder,
        )
        # print(types[folder].keys())
        type_list.extend(list(types[folder].keys()))
        # print(type_list)

    type_list = list(set(type_list))
    strout = ""

    for folder in folders:
        strout += "\t" + folder
    strout += "\n"
    for folder in folders:
        strout += f"\t{n_file[folder]}"
    strout += "\tfiles" + "\n"
    for folder in folders:
        strout += f"\t{n_ann[folder]}"
    strout += "\tannotations\n"

    for tlist_element in type_list:
        for folder in folders:
            if tlist_element in types[folder]:
                strout += "\t" + str(types[folder][tlist_element])
            else:
                strout += "\t0"
        strout += "\t" + tlist_element
        strout += "\n"

    return strout


def create_union_gold_candidate_sets(
    path_doc_col_gs: str,
    path_doc_col_auto: str,
    path_output_newgold_folder: str = "./new_goldstandard_to_fix/",
    copy_txt_files: bool = True,
) -> None:
    """CAREFUL: the changes is inplace - the folder given in input will see its annotations altered"""
    try:
        os.makedirs(path_output_newgold_folder)
    except OSError:
        print(
            "Security: The output folder already exists! Please, delete the folder, or change the output path.",
        )
        return

    # read doc cols
    colgs: DocumentCollection = cast(DocumentCollection, read_document_collection_from_folder(path_doc_col_gs))
    colcs: DocumentCollection = cast(DocumentCollection, read_document_collection_from_folder(path_doc_col_auto))

    col_new: DocumentCollection = DocumentCollection(folderpath=path_output_newgold_folder)

    for docgs in colgs.documents:
        # for each docgs, find the actual doccs
        for doccs in colcs.documents:
            if doccs.filename_without_ext != docgs.filename_without_ext:
                continue
            # now, we know the docs correspond to each other
            annotcol_gs, annotcol_cs = (
                docgs.annotation_collections[0],
                doccs.annotation_collections[0],
            )
            # get annotations
            entitesauto: list[EntityAnnotation] = cast(list[EntityAnnotation], annotcol_cs.get_annotations(descendant_type=EntityAnnotation))
            entitesgs: list[EntityAnnotation] = cast(list[EntityAnnotation], annotcol_gs.get_annotations(descendant_type=EntityAnnotation))

            # find the CORRECT annotations, add _both suffix
            for elt1 in entitesauto:
                for elt2 in entitesgs:
                    if elt1.fragments == elt2.fragments and elt1.label == elt2.label:  # same tag, and same fragments
                        elt1.label = elt1.label + "_both"
                        elt2.label = elt2.label + "_both"

            # get the labels
            labels = []
            for elt in entitesauto:
                if elt.label in labels or elt.label.endswith("_both"):
                    continue
                labels.append(elt.label)
            for elt in entitesgs:
                if elt.label in labels or elt.label.endswith("_both"):
                    continue
                labels.append(elt.label)

            # add the suffixes
            for elt in labels:
                annotcol_gs.replace_annotation_labels(
                    old_name=elt,
                    new_name=elt + "_gold",
                    specific_type=EntityAnnotation,
                )
                annotcol_cs.replace_annotation_labels(
                    old_name=elt,
                    new_name=elt + "_auto",
                    specific_type=EntityAnnotation,
                )

            # we create a new annotcol which is the union of both
            annotcol_gs.combine(annotcol_cs, with_renum=True)
            annotcol_gs.remove_duplicates()  # duplicates are the CORRECT (_both suffix)
            annotcol_gs.renum()  # renum

            # new doc to add
            doc_new = Document(
                fullpath=os.path.join(
                    path_output_newgold_folder,
                    docgs.filename_without_ext + ".txt",
                ),
                annotation_collections=[annotcol_gs],
            )
            print(doc_new)
            col_new.add_document(doc_new)

    # write new corpus
    print(col_new)
    print(f"Writing Union collection in path:{path_output_newgold_folder}")
    write_ann_files_in_folder(col_new, path_output_newgold_folder)

    # also writing the txt file
    if copy_txt_files is True:
        print(
            f"Also writing the txt files, taken from gold, to path:{path_output_newgold_folder}",
        )
        copy_txt_from_collection_to_another_path(colgs, path_output_newgold_folder)
