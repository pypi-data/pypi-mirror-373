from pathlib import Path
from typing import List
from pyconverters_pyexcel.pyexcel import PyExcelConverter, PyExcelParameters, PyCSVConverter, PyCSVParameters
from pymultirole_plugins.v1.schema import Document, DocumentList
from starlette.datastructures import UploadFile


def test_pyexcel():
    converter = PyExcelConverter()
    parameters = PyExcelParameters(text_cols="Verbatim")
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/Echantion_dataverse.xlsx')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'application/octet-stream'), parameters)
        assert len(docs) == 1
        assert len(docs[0].sentences) == 871
        assert docs[0].identifier
        assert docs[0].text
    json_file = source.with_suffix(".json")
    dl = DocumentList(__root__=docs)
    with json_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def test_pyexcel_dtv():
    converter = PyCSVConverter()
    parameters = PyCSVParameters(text_cols="Verbatim")
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/Feedback_client.dtv')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'application/octet-stream'), parameters)
        assert len(docs) == 1
        assert len(docs[0].sentences) == 1624
        assert docs[0].identifier
        assert docs[0].text
    json_file = source.with_suffix(".json")
    dl = DocumentList(__root__=docs)
    with json_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)

    source = Path(testdir, 'data/Echantion_dataverse 29072025.csv')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'application/octet-stream'), parameters)
        assert len(docs) == 1
        assert docs[0].identifier
        assert len(docs[0].sentences) == 871
        assert docs[0].text
    json_file = source.with_suffix(".json")
    dl = DocumentList(__root__=docs)
    with json_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
