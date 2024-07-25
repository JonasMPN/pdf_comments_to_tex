import json
import pylatex as tex
from datetime import date


def paper_notes_to_tex_paragraph(tex_document: tex.document, paper_data: dict):
    """
    """
    formatted_doi = tex.utils.escape_latex(paper_data["doi"])
    date_ = date(day=1, month=paper_data['date'][0], year=paper_data['date'][1]).strftime("%m-%Y")
    tex_document.append(tex.utils.bold(paper_data['author']))
    tex_document.append(date_)
    tex_document.append(tex.NoEscape(r'DOI: \href{https://doi.org/' + formatted_doi + '}{' + formatted_doi + '}'))
    
    def create_latex_table(
            doc,
            category: str, 
            data: dict[str, list[tuple[int, str]]]|dict[str, list[tuple[int, str, int, str]]]|list[tuple[int, str]]):
        table = tex.Table(position='h!')
        table.add_caption(category)

        if category == "general":
            with table.create(tex.Tabular('ll')) as tabular:
                tabular.add_hline()
                tabular.add_row((tex.utils.bold('Page'), tex.utils.bold('Note')))
                tabular.add_hline()
                for page_number, note in data:
                    tabular.add_row((page_number, note))
                    # add lines here
                    # each line gets the page number in the first column and the note in the second column
                    # font stays the same (normal) throughout the table
                    # good luck solider :D
                tabular.add_hline()
        else:
            with table.create(tex.Tabular('lll')) as tabular:
                tabular.add_hline()
                tabular.add_row((tex.utils.bold('Subcategory'), tex.utils.bold('Page'), tex.utils.bold('Note')))
                tabular.add_hline()

                for subcat, entries in data.items():
                    for i, entry in enumerate(entries):
                        if category == "answered":
                            tabular.add_row((subcat if i==0 else '', entry[0], tex.utils.italic(entry[1])))
                            tabular.add_row(('', entry[2], entry[3]))
                        else:
                            tabular.add_row((subcat if i==0 else '', entry[0], entry[1]))
        doc.append(table)

    for category, subcat_dict in paper_data["notes"].items():
        create_latex_table(tex_document, category, subcat_dict)



def collected_json_to_tex(ff_json: str, save_as: str="collected"):
    idx_to_section = {0: tex.Section, 1: tex.Subsection, 2: tex.Subsubsection, 
                      3: tex.section.Paragraph}
    def loop_notes(tex_document: tex.Document, dir_data: dict, level_idx: int):
        for child, child_data in dir_data.items():
            if not child.startswith("f_"):
                with tex_document.create(idx_to_section[level_idx](child)):
                    level_idx += 1
                    if level_idx > 2:
                        raise NotImplementedError("Currently, only 3-level nested directories are supported but "
                                                  f"directory '{child}' is on the fourth.")
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


