# general imports
import json
from datetime import date
import pylatex as tex  # general fits-all import

# pylatex imports for convenience
from pylatex import Document, Section, Subsection, Subsubsection, Table, Tabular

# pylatex imports that are a bit hidden in the package
from pylatex.section import Paragraph
from pylatex.base_classes import Command


def texstr(string: str, indent_string: str="", all_new_line: bool=False, is_link: bool=False):
    if "," in string and not is_link:
        string = " ".join(string.split()) 
        string = string.replace("\n", "")
        string = string.replace("\t", "")  # needed if editor uses \t
        split = string.split(",")
        string = split[0] if not all_new_line else f"%\n{' '*len(indent_string)}{split[0]}"
        # the "tmp" bit of the next line is needed because the splits have a leading " "
        string += f",%\n{' '*len(indent_string)}".join(tmp[1:] for tmp in [""]+split[1:])
    return tex.NoEscape(string)


def use_packages(tex_document: Document):
    tex_document.packages.append(tex.Package("booktabs"))
    tex_document.packages.append(tex.Package("geometry"))
    hyperref_options = texstr("""colorlinks=true, 
                              linkcolor=red, 
                              urlcolor=blue, 
                              citecolor=blue, 
                              anchorcolor=black""", 
                              r"\usepackage[")
    tex_document.packages.append(tex.Package("hyperref", hyperref_options))
    return tex_document


def redefine(tex_document: Document):
    tex_document.preamble.append(texstr("\n% redefining parameters"))
    geometry_options = texstr("""a4paper, 
                              left=0.15\paperwidth, 
                              right=0.15\paperwidth, 
                              top=0.12\paperheight, 
                              bottom=0.18\paperheight""", "\geometry{")
    tex_document.preamble.append(Command("geometry", arguments=geometry_options))
    tex_document.preamble.append(Command("setcounter", arguments="tocdepth", extra_arguments="4"))
    return tex_document


def newcommands(tex_document: Document):
    tex_document.preamble.append(texstr("\n% defining new commands"))
    tex_document.preamble.append(Command("newcommand", 
                                         arguments=texstr("\contents"),
                                         extra_arguments=texstr(r"\tableofcontents\newpage")))
    return tex_document


class LimitTabular(Tabular):
    def __init__(self, 
                 table_spec, 
                 data=None, 
                 pos=None, 
                 *, 
                 row_height=None, 
                 col_space=None, 
                 width=None, 
                 booktabs=None, 
                 column_widths: dict={},
                 max_width_characters: int=80,
                 **kwargs):
        super().__init__(table_spec, data, pos, row_height=row_height, col_space=col_space, width=width, 
                         booktabs=booktabs, **kwargs)
        self.__class__.__name__ = "tabular"
        self.column_widths = column_widths
        self.max_width_characters = max_width_characters
        if sum(self.column_widths.values()) > self.max_width_characters:
            raise ValueError("The sum of the widths of the maximum allowable size per columns must not "
                             "be larger than the maximum allowable size of the table.")
        
    def limited_rows(self, data: list[tuple[str, ...]], n_cols: int=None, header: tuple[str, ...]=None):
        n_cols = n_cols if n_cols is not None else self.width
        col_chars = self._get_column_widths(data)
        if len(self.data) != 0 or header is not None:
            header = header if header is not None else self.data[0].split("&")
            col_chars = self._adjust_max_to_header(col_chars, header)
        max_chars = [col_chars[i] for i in range(n_cols)]
        return [self._fit_row(max_chars, [entry.split(" ") for entry in row], []) for row in data]
        
    def fill(self, data: list[tuple[str, ...]], n_cols: int=None):
        for sub_row in self.limited_rows(data, n_cols):
            self.add_row(*sub_row)

    def _get_column_widths(self, data: list[tuple[str, ...]], max_iter: int=1e3):
        # max_characters has the maximum number of characters present in each column.
        # The column index can directly be used for max_characters
        max_characters = [max(list(map(lambda x: len(x), row))) for row in zip(*data)]
        max_capped = {}
        columns_open = {}
        for col_idx, chars in enumerate(max_characters):
            if col_idx in self.column_widths:
                max_capped[col_idx] = min(self.column_widths[col_idx], len(chars))
            else:
                try: 
                     columns_open[chars].append(col_idx)
                except KeyError:
                     columns_open[chars] = [col_idx]

        chars_used = sum(max_capped)
        for iter_idx in range(int(max_iter)):
            n_cols_open = sum([len(col_ids) for col_ids in columns_open.values()])
            if n_cols_open == 0:
                break
            smallest = min(columns_open.keys())
            for col_idx in columns_open[smallest]:
                max_per_col = int((self.max_width_characters-chars_used)/n_cols_open)
                col_gets = min(max_per_col, smallest)
                chars_used += col_gets
                max_capped[col_idx] = col_gets
                n_cols_open -= 1
            columns_open.pop(smallest)
        if iter_idx == max_iter:
            raise RuntimeError("Max iteration reached before being able to assign column widths.")
        return max_capped

    def _fit_row(self, max_chars_per_col: list, data_to_split: tuple[str, ...], subrows: list[list[str]]):
        new_row = []
        left = []
        done = []
        for max_chars, words in zip(max_chars_per_col, data_to_split):
            if words == [""]:
                left.append([""])
                done.append(True)
                new_row.append("")
                continue
            col_entry = []
            used = 0
            for word in words:
                n_chars = len(word)
                if n_chars > max_chars:
                    raise ValueError(f"Word '{word}' is longer than maximum allowed column width {max_chars}.")
                used += n_chars+1  # +1 because of the blank space between words
                if used > max_chars+1:  # +1 because the last blank space is left out 
                    break
                col_entry.append(word)
            
            n_used_words = len(col_entry)
            new_row.append(" ".join(col_entry)) 
            if len(words) > n_used_words:
                left.append(words[n_used_words:])
                done.append(False)
            else:
                left.append([""])
                done.append(True)
        subrows.append(new_row)
        if not all(done):
            self._fit_row(max_chars_per_col, left, subrows)
        return subrows

    @staticmethod
    def _adjust_max_to_header(max_capped: dict, header_row: tuple[str, ...]):
        for col_idx, heading in enumerate(header_row):
            max_capped[col_idx] = max(max_capped[col_idx], len(heading))
        return max_capped
    

def create_latex_table(
            doc,
            category: str, 
            data: dict[str, list[tuple[int, str]]]|dict[str, list[tuple[int, str, int, str]]]|list[tuple[int, str]]):
        table = Table(position='h!')
        table.add_caption(category)

        if category == "general":
            with table.create(LimitTabular('ll', booktabs=True)) as tabular:
                tabular.add_row("Page", "Note")
                tabular.append(Command("midrule"))
                for split_rows in tabular.limited_rows(data):
                    for row in split_rows:
                        tabular.add_row(*row)
                    
        else:
            with table.create(LimitTabular('lll', booktabs=True)) as tabular:
                tabular.add_row("Subcategory", "Page", "Note")
                tabular.append(Command("midrule"))

                if category == "answered":
                    for subcat, entries in data.items():
                        two_cols = []
                        for entry in entries:
                            two_cols.append(entry[:2])
                            two_cols.append(entry[2:])
                        lrows = tabular.limited_rows(two_cols, n_cols=2, header=("Page", "Note"))
                        for i, (questions, answers) in enumerate(zip(lrows[::2], lrows[1::2])):
                            for question, answer in zip(questions, answers):
                                tabular.add_row((subcat if i==0 else '', question[0], tex.utils.italic(question[1])))
                                tabular.add_row(('', *answer))
                else:
                    for subcat, entries in data.items():
                        split_rows = tabular.limited_rows(entries, n_cols=2, header=("Page", "Note"))
                        for i, split_rows in enumerate(split_rows):
                            for j, row in enumerate(split_rows):
                                tabular.add_row((subcat if i==0 and j==0 else '', *row))
        doc.append(table)


def paper_notes_to_tex_paragraph(tex_document: tex.document, paper_data: dict):
    """
    """
    if paper_data["date"] == "missing":
        date_formatted = "date missing"
    else:
        date_formatted = date(day=1, month=paper_data['date'][0], year=paper_data['date'][1]).strftime("%m-%Y")
    tex_document.append(tex.utils.bold(paper_data['author']))
    tex_document.append(date_formatted)
    tex_document.append(Command("href", f"https://doi.org/{paper_data['doi']}", extra_arguments=paper_data['doi']))

    for category, subcat_dict in paper_data["notes"].items():
        create_latex_table(tex_document, category, subcat_dict)


def collected_notes_to_tex(collected_notes: dict=None, ff_json: str=None, save_as: str="collected"):
    if (collected_notes is None and ff_json is None) or (collected_notes is not None and ff_json is not None):
        raise ValueError("Either 'collected_notes' or 'ff_json' must be set using 'collected_json_to_tex()', not both "
                         "or neither.")
    idx_to_section = {0: Section, 1: Subsection, 2: Subsubsection, 3: Paragraph}
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
                if child_data != {}:
                    with tex_document.create(idx_to_section[3](child[2:-4])):
                        paper_notes_to_tex_paragraph(tex_document, child_data)
        return level_idx-1
    
    doc = Document(documentclass="article", document_options="a4paper")
    for apply in [use_packages, redefine, newcommands]:
        doc = apply(doc)
    
    doc.append(texstr("\contents"))
    
    if ff_json is not None:
        with open(ff_json, "r") as file_notes:
            collected_notes = json.load(file_notes)
    
    level_idx = 0
    loop_notes(doc, collected_notes, level_idx)
    doc.generate_tex(save_as)


