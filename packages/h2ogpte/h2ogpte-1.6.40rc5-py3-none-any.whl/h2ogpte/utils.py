import io
from pathlib import Path
from typing import Any
import json


from pydantic import BaseModel, ByteSize
import filetype


class SizeConfig(BaseModel):
    size: ByteSize

    def get_val(self) -> int:
        return int(self.size)


def import_pymupdf():
    try:
        import pymupdf
    except:
        raise RuntimeError(
            "This operation requires PyMuPDF (not installed by default).\n"
            "Please manually install PyMuPDF with 'pip install pymupdf' (might require newer versions of setuptools and/or pip).\n"
        )
    return pymupdf


def decrypt_pdf(file_name: str, file: Any, password: str = "") -> Any:
    file_name_path = Path(file_name)
    ext = file_name_path.suffix.lower()
    try:
        guess_ext = "." + filetype.guess_extension(file_name_path)
        if guess_ext in [".pdf"] or ext not in [".pdf"]:
            ext = guess_ext
    except (TypeError, FileNotFoundError):
        pass

    if ext == ".pdf":
        pymupdf = import_pymupdf()
        doc = pymupdf.open(file)
        if doc.needs_pass:
            rc = doc.authenticate(password)
            if rc not in (1, 4, 6):  # authorization levels including ownership
                raise RuntimeError("Invalid PDF password.")

            file.close()
            # Create a BytesIO object to hold the unencrypted PDF
            file = io.BytesIO()

            # Save the unencrypted PDF to the BytesIO object
            doc.save(file, encryption=pymupdf.PDF_ENCRYPT_NONE, garbage=4, deflate=True)
            doc.close()  # Close the document now that we've finished with it

            # Reset the pointer of the BytesIO object to the start
            file.seek(0)

    return file


def _create_polygon_annotation(page, selection):
    points = [(coord["x"], coord["y"]) for coord in selection["polygons"]]
    annot = page.add_polygon_annot(points)
    annot.set_colors(stroke=(1, 1, 1), fill=(1.0, 1.0, 0.0))
    annot.set_opacity(0.4)
    annot.update()


def _process_pdf_with_annotations(
    pdf_document,
    markers: list,
    destination_directory: str,
    doc_id: str,
    output_type: str = "combined",
):
    destination_directory = Path(destination_directory)
    out_filepaths = []
    for i, marker in enumerate(markers):
        marker = json.loads(marker)
        chunk_id = marker["chunk_id"]
        selections = json.loads(marker["pages"])["selections"]
        for selection in selections:
            page_number = selection["page"] - 1
            page = pdf_document.load_page(page_number)
            page.set_rotation(0)
            _create_polygon_annotation(page, selection)

        if output_type == "split":
            destination_file_name = f"{doc_id}_{chunk_id}.pdf"
            destination_file = destination_directory / destination_file_name
            pdf_document.save(destination_file)
            out_filepaths.append(destination_file)

    if output_type == "combined":
        destination_file_name = f"{doc_id}.pdf"
        destination_file = destination_directory / destination_file_name
        pdf_document.save(destination_file)
        out_filepaths.append(destination_file)

    pdf_document.close()
    return out_filepaths
