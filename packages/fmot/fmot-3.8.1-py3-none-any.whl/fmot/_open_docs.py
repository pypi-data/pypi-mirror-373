import fmot
import os
import pathlib


def open_docs():
    fmot_path = pathlib.Path(fmot.__file__).parent.resolve().parent.resolve()
    doc_path = os.path.join(fmot_path, "docs")
    index_path = os.path.join(doc_path, "_build", "html", "index.html")
    cwd = os.getcwd()
    os.system(
        f"cd {doc_path}; sphinx-apidoc -f . -o .; make clean html; cd {cwd}; open {index_path}"
    )


if __name__ == "__main__":
    open_docs()
