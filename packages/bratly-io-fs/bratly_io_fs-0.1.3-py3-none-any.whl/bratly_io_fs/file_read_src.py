import glob
import re
from os import scandir
from os.path import basename, isfile, join, sep, split, splitext
from pathlib import Path
from typing import Optional

from bratly import (
    Annotation,
    AnnotationCollection,
    AttributeAnnotation,
    Document,
    DocumentCollection,
    EntityAnnotation,
    EquivalenceAnnotation,
    EventAnnotation,
    NormalizationAnnotation,
    NoteAnnotation,
    ParsingError,
    RelationAnnotation,
)


def list_files_from_folder(path: str) -> list[str]:
    """Deprecated"""
    with scandir(path) as entries:
        return [entry.name for entry in entries]


def parse_and_fix_ann_grammar(ann_content: str) -> str:
    r"""
    Parse ann file to check:
    - if each line matches with one of our Annotations regex properly (raise Exception if no match !)
    - in the same time: check the appropriateness of the Fragment indices wrt the content
    - if not coherent, check if there's the \n issue and fix the ann accordingly
    - if there is no such line, raise Exception
    - returns the fixed ann file, if everything is good.
    """
    regex_dico = {
        "T": r"^T\d+\t[\w\_/-]+ \d+ \d+(;\d+ \d+)*\t.*",  # Entity
        "R": r"^R\d+\t[\w\_/-]+ \w+:T\d+ \w+:T\d+",  # Relation
        "A": r"^A\d+\t[\w\_/-]+( \w+)+",  # Attribute
        "M": r"^M\d+\t[\w\_/-]+( \w+)+",  # Attribute
        "#": r"^#\d*\t[\w\_/\.-]+ \w+\t.*",  # Note
        "N": r"^N\d+\t[\w\_/-]+ \w+ \w+:\w+\t.+",  # Normalization
        "*": r"^\*\t[\w\_/-]+( T\d)+",  # Equivalence
        "E": r"^E\d+\t[\w\_/-]+:[TE]\d+( \w+:[TE]\d+)+",  # Event
    }
    # Check if CRLF exists first (\r\n) else LF by default
    ann_contents = ann_content.split("\r\n") if "\r\n" in ann_content else ann_content.split("\n")

    for i, line in enumerate(ann_contents):
        if line == "":
            continue
        appropriate_regex = None
        if line[0] in regex_dico:
            appropriate_regex = regex_dico[line[0]]
            if re.match(appropriate_regex, line):
                # we got a match, check appropriateness of indices if it is Entity
                if line[0] != "T":  # Not an entity - no check
                    continue
                # indices checking
                items = line.split("\t")
                content = items[2]
                len_content = len(content)
                all_indices = items[1].split(" ", 1)
                fragments = [(int(s.split(" ")[0]), int(s.split(" ")[1])) for s in all_indices[1].split(";")]
                expected_length = len(fragments) - 1
                for fstart, fend in fragments:
                    expected_length += fend - fstart
                if len_content == expected_length:
                    # all good, correct indices and content !
                    continue
                # not correct indices, maybe fixable?
                final_content = content + " " + ann_contents[i + 1]
                if len(final_content) == expected_length:
                    # fix ann content
                    ann_contents[i] = ann_contents[i] + " " + ann_contents[i + 1]
                    ann_contents[i + 1] = ""
                    continue
                # not fixable, raise Exception !
                raise ParsingError(f"Badly formed annotation\n{line}")
            # not a match, raise Exception
            raise ParsingError(f"Badly formed annotation\n{line}")
        # not a match, raise Exception
        raise ParsingError(f"Badly formed annotation\n{line}")

    # Make the new fixed ann_content
    ann_contents_noempty = [item for item in ann_contents if item]
    ann_content_res = "\n".join(ann_contents_noempty)

    return ann_content_res


def read_from_file(path: str) -> str:
    """Read any file (txt, ann) and returns the str"""
    with open(path, encoding="utf_8", newline="") as fread:
        # using io.open instead of io to preserve newlines as is  (LF, or CRLF)
        text = fread.read()
    return text


def read_texts_from_folder(path: str) -> dict[str, str]:
    """Returns a dictionary containing the content for each filename (texts)"""
    filenames = glob.glob(path + "/*.txt")
    return {basename(filename): read_from_file(filename) for filename in filenames}


def read_ann_files_from_folder(path: str, verbose: bool = False) -> dict[str, str]:
    """Returns a dictionary containing the content for each filename (annotations)"""
    filenames = glob.glob(path + "/*.ann")
    ret = {}
    if verbose:
        print("Reading folder", path, ":")
    for i, filename in enumerate(filenames):
        ret[basename(filename)] = read_from_file(filename)
        if verbose:
            print(i, "/", len(filenames), end="\r")
    return ret


def read_and_load_ann_file(
    path: str,
    no_duplicates: bool = True,
    sorting: bool = True,
    renumerotize: bool = True,
    grammar_check: bool = True,
    version: str = "0.0.1",
    comment: str = "Empty comment",
) -> Optional[AnnotationCollection]:
    """Read ann file and returns the corresponding Annotation Collection"""
    # check if a correct path has been given
    if not path:
        print("Error: you should give the path of your ann file!")
        return None
    if not isinstance(path, str):
        print("Error: the path of your ann file should be a str!")
        return None
    exists = isfile(path)
    if not exists:
        print("Error: the ann file located in:", path, "does not exists!")
        return None
    ann_str = read_from_file(path)
    if grammar_check:
        ann_str = parse_and_fix_ann_grammar(ann_str)
    output = parse_ann_file(
        annstr=ann_str,
        filepath=path,
        sorting=sorting,
        no_duplicates=no_duplicates,
        renumerotize=renumerotize,
        version=version,
        comment=comment,
    )
    if output is None:
        print(f"Warning: AnnotationCollection associated to {path} is None.")
    return output


def read_and_load_txt_file(
    txtpath: str,
    annpath: str = "",
    ann_no_duplicates: bool = True,
    ann_sorting: bool = True,
    ann_renumerotize: bool = True,
    ann_grammar_check: bool = True,
    ann_version: str = "0.0.1",
    doc_version: str = "0.0.1",
    ann_comment: str = "Empty comment",
    doc_comment: str = "Empty comment",
) -> Optional[Document]:
    """Read document file and its associated annotation, then returns a Document instance"""
    # check if a correct txtpath has been given
    if not txtpath:
        print("Error: you should give the path of your txt file!")
        return None
    if not isinstance(txtpath, str):
        print("Error: the path of your txt file should be a str!")
        return None
    exists = isfile(txtpath)
    if not exists:
        print("Error: the txt file located in:", txtpath, "does not exists!")
        return None

    # now that we found the txtpath, tries to find annpath
    if not isinstance(annpath, str):
        print(
            "No valid ann file for txt:",
            txtpath,
            "- making a Document instance without AnnCollection.",
        )
        # return Document with Empty ann collection.
        return Document(fullpath=txtpath, version=doc_version, comment=doc_comment)
    if annpath == "" or annpath is None:
        # first attempt: replace the extension of txtpath (.txt) using .ann (same directory)
        annpath = splitext(txtpath)[0] + ".ann"
        print("Attempt to find ann file through the path: ", annpath)
        if not isfile(annpath):
            # second attempt: replace a subdirectory (if any!) called txt by ann
            # split the path into a list of directories and the filename
            folderpath, filename = split(annpath)
            dirs = folderpath.split(sep)
            if "txt" in dirs:
                # find the index of the latest occurrence of the "txt" directory
                txt_index = len(dirs) - dirs[::-1].index("txt") - 1
                # replace the "txt" directory with "ann"
                dirs[txt_index] = "ann"
                # join the new path
                annpath = join(*dirs, filename)
                print("Attempt to find ann file through the path: ", annpath)
                if not isfile(annpath):
                    # both not working? return Document with Empty ann collection.
                    print(
                        "No corresponding ann file found for txt:",
                        txtpath,
                        "- making a Document instance without AnnCollection.",
                    )
                    return Document(fullpath=txtpath, version=doc_version, comment=doc_comment)
            else:
                print(
                    "No corresponding ann file found for txt:",
                    txtpath,
                    "- making a Document instance without AnnCollection.",
                )
                return Document(fullpath=txtpath, version=doc_version, comment=doc_comment)

    # being there means we have a valid annpath
    annotation_collection = read_and_load_ann_file(
        path=annpath,
        sorting=ann_sorting,
        no_duplicates=ann_no_duplicates,
        renumerotize=ann_renumerotize,
        grammar_check=ann_grammar_check,
        version=ann_version,
        comment=ann_comment,
    )
    if isinstance(annotation_collection, AnnotationCollection):
        return Document(fullpath=txtpath, version=doc_version, comment=doc_comment, annotation_collections=[annotation_collection])
    print(f"Warning: AnnotationCollection is not included in Document {txtpath}")
    return Document(fullpath=txtpath, version=doc_version, comment=doc_comment, annotation_collections=[])


def parse_ann_line(
    line: str,
    entities: dict[str, EntityAnnotation],
    annotations: dict[str, Annotation],
    txtpath: str,
) -> Optional[Annotation]:
    """Parses a line, identifies the type of annotation in the line, and returns a parsed Annotation with the corresponding class"""
    if not line:
        return None
    match line[0]:
        case "T":
            try:
                return EntityAnnotation.from_line(line)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with T (EntityAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "A":
            try:
                return AttributeAnnotation.from_line(line, annotations)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with A (AttributeAnnotation): {e.args[0]}.  Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "M":
            try:
                return AttributeAnnotation.from_line(line, annotations)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with M (AttributeAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "R":
            try:
                return RelationAnnotation.from_line(line, entities)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with R (RelationAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "E":
            try:
                return EventAnnotation.from_line(line, entities)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with E (EventAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "N":
            try:
                return NormalizationAnnotation.from_line(line, annotations)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with N (NormalizationAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "*":
            try:
                return EquivalenceAnnotation.from_line(line, entities)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with * (EquivalenceAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case "#":
            try:
                return NoteAnnotation.from_line(line, annotations)
            except ParsingError as e:
                print(
                    f"Issue with parsing the line starting with # (NoteAnnotation): {e.args[0]}. Returning None.",
                )
                print("The line is:", line)
                print("The txt file is:", txtpath)
                return None
        case _:
            print("Issue with parsing one line. Returning None. The line is:", line)
            return None


def parse_ann_file(
    annstr: str,
    filepath: str,
    no_duplicates: bool = True,
    sorting: bool = True,
    renumerotize: bool = True,
    version: str = "0.0.1",
    comment: str = "Empty comment",
) -> AnnotationCollection:
    """
    Parses a whole annotation file. Returns a tuple containing:
    * A dictionary of annotations containing the
    * one list for each annotation type (i.e., a list for EntityAnnotations, one for RelationAnnotations, etc.)
    """
    # Keeping track of annotations during parsing
    entities_dict: dict[str, EntityAnnotation] = {}
    annotations_dict: dict[str, Annotation] = {}
    # Parsing annotations
    annotations: list[Annotation] = []
    for line in annstr.splitlines():
        ann = parse_ann_line(line, entities_dict, annotations_dict, filepath)
        if ann is None:
            continue
        # We keep track of all annotations that have an ID, EquivalenceAnnotation does not have one.
        if not isinstance(ann, EquivalenceAnnotation):
            annotations_dict.update({ann.id: ann})
        if isinstance(ann, EntityAnnotation):
            entities_dict.update({ann.id: ann})
        annotations.append(ann)

    # Create AnnotationCollection
    ann_collection = AnnotationCollection(
        annotations=annotations,
        version=version,
        comment=comment,
    )
    if no_duplicates:
        ann_collection.remove_duplicates()
    if sorting:
        ann_collection.sort_annotations()
    if renumerotize:
        ann_collection.renum()
    return ann_collection


def read_document_collection_from_folder(
    path: str,
    no_duplicates_ann: bool = True,
    sort_ann: bool = True,
    renumerotize_ann: bool = True,
    grammar_check_ann: bool = True,
    version: str = "0.0.1",
    comment: str = "Empty comment",
) -> Optional[DocumentCollection]:
    """
    Reads txt and ann from a folder and builds a DocumentCollection from that.

    Args:
        path (str): The path to the folder containing the documents.
        no_duplicates_ann (bool): Whether to remove duplicate annotations.
        sort_ann (bool): Whether to sort annotations.
        renumerotize_ann (bool): Whether to renumerotize annotations.
        grammar_check_ann (bool): Whether to perform grammar check on annotations.
        version (str): The version of the document collection.
        comment (str): A comment for the document collection.

    Returns:
        Optional[DocumentCollection]: The constructed DocumentCollection or None if an error occurred.

    """
    dico_txt = read_texts_from_folder(path)
    dico_ann = read_ann_files_from_folder(path)
    ann_filenames = list(dico_ann.keys())
    docs: list[Document] = []
    txt_name = ""
    try:
        for txt_name in dico_txt:
            if txt_name.endswith(".txt"):
                ann_name = ".ann".join(txt_name.rsplit(".txt", 1))
            elif txt_name.endswith(".TXT"):
                ann_name = ".ann".join(txt_name.rsplit(".TXT", 1))
            else:
                print(
                    "It should never happen, but a supposed-to-be txt file does not end with txt. The involved file is:",
                    path,
                    txt_name,
                )
                continue
            if ann_name not in ann_filenames:
                print(
                    "The file",
                    path,
                    txt_name,
                    "does not contain the corresponding ann file !",
                )
                continue
            full_txt_path = join(path, txt_name)
            ann_collect = read_and_load_ann_file(
                join(path, ann_name),
                sorting=sort_ann,
                no_duplicates=no_duplicates_ann,
                renumerotize=renumerotize_ann,
                grammar_check=grammar_check_ann,
            )
            txtfile = Path(path) / txt_name
            text = ""
            if txt_name != "" and txtfile.is_file():
                with open(txtfile, encoding="utf8") as f:
                    text = f.read()
            if isinstance(ann_collect, AnnotationCollection):
                docs.append(
                    Document(
                        fullpath=full_txt_path,
                        annotation_collections=[ann_collect],
                        text=text,
                    ),
                )
            else:
                print(f"Warning: AnnotationCollection is not included in Document {full_txt_path}")
                docs.append(
                    Document(
                        fullpath=full_txt_path,
                        annotation_collections=[],
                        text=text,
                    ),
                )
    except Exception as my_exception:
        print("Exception occurred:", str(my_exception))
        print("File:", str(txt_name))
        print("Returned None instead of DocumentCollection.")
        return None

    doc_coll = DocumentCollection(
        folderpath=path,
        version=version,
        comment=comment,
        documents=docs,
    )
    return doc_coll
