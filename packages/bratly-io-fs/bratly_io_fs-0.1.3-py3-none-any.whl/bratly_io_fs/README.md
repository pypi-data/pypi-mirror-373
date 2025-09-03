<a id="tools"></a>

# tools

<a id="tools.duplicate_document_collection_with_specific_annotations"></a>

#### duplicate\_document\_collection\_with\_specific\_annotations

```python
def duplicate_document_collection_with_specific_annotations(
        doccol_input_path: str,
        doccol_output_path: str,
        labels_to_keep: list[str],
        involved_annot_type=EntityAnnotation) -> DocumentCollection
```

Copy an existing document collection, while keeping only a specific subset of annotations given their labels

<a id="ann_write_src"></a>

# ann\_write\_src

<a id="ann_write_src.write_ann_file"></a>

#### write\_ann\_file

```python
def write_ann_file(annotations: AnnotationCollection, path: str) -> None
```

Writes the content of a list of annotations to the file specified in path

<a id="ann_write_src.write_ann_files_in_folder"></a>

#### write\_ann\_files\_in\_folder

```python
def write_ann_files_in_folder(doc_collection: DocumentCollection,
                              path: str) -> None
```

Writes the ann content of a document collection to the folder specified in path

<a id="ann_write_src.copy_txt_from_collection_to_another_path"></a>

#### copy\_txt\_from\_collection\_to\_another\_path

```python
def copy_txt_from_collection_to_another_path(
        doc_collection: DocumentCollection, path_to_folder: str) -> None
```

Copies the txt files from the current collection to another, useful when you're creating a new collection from this one

<a id="__init__"></a>

# \_\_init\_\_

<a id="file_read_src"></a>

# file\_read\_src

<a id="file_read_src.list_files_from_folder"></a>

#### list\_files\_from\_folder

```python
def list_files_from_folder(path: str) -> list[str]
```

Deprecated

<a id="file_read_src.parse_and_fix_ann_grammar"></a>

#### parse\_and\_fix\_ann\_grammar

```python
def parse_and_fix_ann_grammar(ann_content: str) -> str
```

Parse ann file to check:
   - if each line matches with one of our Annotations regex properly (raise Exception if no match !)
   - in the same time: check the appropriateness of the Fragment indices wrt the content
   - if not coherent, check if there's the 
issue and fix the ann accordingly
   - if there is no such line, raise Exception
   - returns the fixed ann file, if everything is good.

<a id="file_read_src.read_from_file"></a>

#### read\_from\_file

```python
def read_from_file(path: str) -> str
```

Read any file (txt, ann) and returns the str

<a id="file_read_src.read_texts_from_folder"></a>

#### read\_texts\_from\_folder

```python
def read_texts_from_folder(path: str) -> dict[str, str]
```

Returns a dictionary containing the content for each filename (texts)

<a id="file_read_src.read_ann_files_from_folder"></a>

#### read\_ann\_files\_from\_folder

```python
def read_ann_files_from_folder(path: str) -> dict[str, str]
```

Returns a dictionary containing the content for each filename (annotations)

<a id="file_read_src.read_and_load_ann_file"></a>

#### read\_and\_load\_ann\_file

```python
def read_and_load_ann_file(
        path: str,
        no_duplicates: bool = True,
        sorting: bool = True,
        renumerotize: bool = True,
        grammar_check: bool = True,
        version: str = "0.0.1",
        comment: str = "Empty comment") -> AnnotationCollection
```

Read ann file and returns the corresponding Annotation Collection

<a id="file_read_src.read_and_load_txt_file"></a>

#### read\_and\_load\_txt\_file

```python
def read_and_load_txt_file(txtpath: str,
                           annpath: str = "",
                           ann_no_duplicates: bool = True,
                           ann_sorting: bool = True,
                           ann_renumerotize: bool = True,
                           ann_grammar_check: bool = True,
                           ann_version: str = "0.0.1",
                           doc_version: str = "0.0.1",
                           ann_comment: str = "Empty comment",
                           doc_comment: str = "Empty comment") -> Document
```

Read document file and its associated annotation, then returns a Document instance

<a id="file_read_src.parse_ann_line"></a>

#### parse\_ann\_line

```python
def parse_ann_line(line: str, entities: dict[str, EntityAnnotation],
                   annotations: dict[str, Annotation]) -> Annotation
```

Parses a line, identifies the type of annotation in the line, and returns a parsed Annotation with the corresponding class

<a id="file_read_src.parse_ann_file"></a>

#### parse\_ann\_file

```python
def parse_ann_file(annstr: str,
                   no_duplicates: bool = True,
                   sorting: bool = True,
                   renumerotize: bool = True,
                   version: str = "0.0.1",
                   comment: str = "Empty comment") -> AnnotationCollection
```

Parses a whole annotation file. Returns a tuple containing:
* A dictionary of annotations containing the
* one list for each annotation type (i.e., a list for EntityAnnotations, one for RelationAnnotations, etc.)

<a id="file_read_src.read_document_collection_from_folder"></a>

#### read\_document\_collection\_from\_folder

```python
def read_document_collection_from_folder(
        path: str,
        no_duplicates_ann: bool = True,
        sort_ann: bool = True,
        renumerotize_ann: bool = True,
        grammar_check_ann: bool = True,
        version: str = "0.0.1",
        comment: str = "Empty comment") -> DocumentCollection
```

Reads txt and ann from a folder and builds a DocumentCollection from that

