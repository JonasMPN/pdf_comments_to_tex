import json
import pylatex as tex


def paper_notes_to_tex_paragraph(tex_document: tex.document, paper_data: dict):
    """
    """


def collected_json_to_tex(ff_json: str, save_as: str="collected"):
    idx_to_section = {0: tex.Section, 1: tex.Subsection, 2: tex.Subsubsection, 
                      3: tex.section.Paragraph}
    def loop_notes(tex_document: tex.Document, dir_data: dict, level_idx: int):
        for child, child_data in dir_data.items():
            if not child.startswith("f_"):
                with tex_document.create(idx_to_section[level_idx](child)):
                    level_idx += 1
                    level_idx = loop_notes(tex_document, child_data, level_idx)
            else:
                with tex_document.create(idx_to_section[3](child[2:-4])):
                    paper_notes_to_tex_paragraph(tex_document, child_data)
        return level_idx-1
    
    doc = tex.Document(documentclass="article", document_options="a4paper")
    doc.packages.append(tex.NoEscape(r'\usepackage{booktabs}'))
    doc.packages.append(tex.NoEscape(r'\usepackage{hyperref}'))
    
    with open(ff_json, "r") as file_notes:
        notes = json.load(file_notes)
    level_idx = 0
    loop_notes(doc, notes, level_idx)
    doc.generate_tex(save_as)