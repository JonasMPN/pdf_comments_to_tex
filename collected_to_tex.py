def directory_to_section(name: str, level_idx: int):
    """
    >> match level_idx:
        >> case 0:
            >> create section with name
        >> case 1:
            >> create subsection with name
        >> case 2: 
            >> create subsubsection with name
        >> case 3: 
            >> raise error
    """


def paper_notes_to_tex_paragraph():
    """
    
    """


def collected_json_to_tex():
    """
    >> notes = load json (dict)
    >> idx_to_section = {0: Section, 1: Subsection, 2: Subsubsection}
    >> level_idx = 0
    >> define recursive function loop_notes(dir_data, level_idx) that loops over child, child_data in dir_data.items()
        >> for child, child_data in dir_data.items():
            >> if not child.startswith("f_"):
                This means the key is still a directory
                >> create section/subsection/subsubsection with idx_to_section[level_idx]
                >> directory_to_section(level_idx)
                >> level_idx += 1
                >> level_idx = loop_notes(child_data, level_idx)
            >> else:
                This means the key is now the name of a paper
                >> paper_name = child[1:] (skip the "f_")
                Use method paper_notes_to_tex_paragraph to create the paragraph
                >> paper_notes_to_tex_paragraph(child_data)
        return level_idx-1
    """
    