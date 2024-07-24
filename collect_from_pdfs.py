import fitz 
from os.path import join, abspath, dirname, isdir, isfile
from os import listdir
import json
from datetime import datetime

subject_translation = {  # since the annotation data in the PDF is dependent on the language settings of the PDF reader 
    # that was used to add the annotations
    "Kommentar zu Text": "note",
    "Comment on Text": "note",
    "Notiz": "reply",
    "Sticky Note": "reply"
}


def extract_year_month(date_str):
    if date_str.startswith("D:"):
        date_str = date_str[2:]
    
    date_time_str = date_str[:14]
    date_time = datetime.strptime(date_time_str, "%Y%m%d%H%M%S")
    return date_time.month, date_time.year


def extract_doi(subject: str):
    if "doi" in subject:
        return subject[subject.find("doi"):].replace(" ", "")
    else:
        return "missing"


def _merge_extracted_and_additional(
        add_to: dict, 
        metadata: dict, 
        overwrite: dict, 
        missing: dict, 
        extracted: tuple[str, str], 
        apply=None):
    value_name, value = extracted
    
    if value_name in overwrite:
        add_to[value_name] = overwrite[value_name]
    elif value_name in missing:
        add_to[value_name] = missing[value_name]
        if missing[value_name] != "missing":
            metadata[value_name] = missing[value_name]
            missing.pop(value_name)
    elif value != "":
        add_to[value_name] = value if apply is None else apply(value)
        if add_to[value_name] == "missing":
            missing[value_name] = "missing"
    else:
        add_to[value_name]  = "missing"
        missing[value_name] = "missing"
    return add_to, missing


def process_note(note: dict[str, str]):
    content = note["content"]

    info_data = content.split(":")
    if len(info_data) == 1:
        note_type = "general"
        note_category = [None]
        note = info_data[0]
    else:
        note_type_data = info_data[0].split("_")
        note_type = note_type_data[0]
        if len(note_type_data) > 1:
            note_category = note_type_data[1:]
        else:
            note_category = ["general"]
        note = info_data[1]
        while note[0] == " ":
            note = note[1:]
    return note_type, note_category, note


def add_note_to_notes(notes: dict, note_type: str, note_category: str|None, note: str, page_number: int,
                      note_answer: str=None, page_number_answer: int=None):
    if note_type not in notes:
        notes[note_type] = {} if note_category is not None else []

    append = (page_number, note)
    if page_number_answer is not None and note_answer is not None:
                append = append + (page_number_answer, note_answer)

    if note_category is not None:
        if note_category not in notes[note_type]:
            notes[note_type][note_category] = []
        notes[note_type][note_category].append(append)
    else:
        notes[note_type].append(append)
    return notes


def process_notes(pdf: fitz.Document):
    questions = {}
    answers = {}
    notes = {}
    last_subject = ""
    last_question = ()
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        annotations = page.annots()

        if annotations:
            for i_annot, annot in enumerate(annotations):
                note_type, note_category, note = process_note(annot.info)
                if note_type != "question" and note_type != "answer":
                    # standalone note that is neither a question nor an answer
                    last_was_question = False
                    notes = add_note_to_notes(notes, note_type, note_category[0], note, page_num+1)
                elif note_type == "answer":
                    if last_subject != subject_translation[annot.info["subject"]]:
                        if last_was_question:
                            # if the answer-question pair is written as a note-answer pair in the pdf
                            notes = add_note_to_notes(notes, "answered", *last_question, note, page_num+1)
                            last_question = ()
                        else:
                            pdf_name = pdf.name.replace("\\", "/").split("/")[-1]
                            raise NotImplementedError(f"Answer '{note}' in '{pdf_name}' is replying to a note that is "
                                                      "not specified as a question.")
                    else:
                        if not any([True if cat.isdigit() else False for cat in note_category]):
                            pdf_name = pdf.name.replace("\\", "/").split("/")[-1]
                            raise ValueError(f"Answer '{note}' in '{pdf_name}' is not connected to a question but it "
                                             "must. The note specifer should end in '_idx'.")
                        category = "_".join(str(cat) for cat in note_category)
                        answers[category] = (note, page_num+1)

                if last_question != ():
                    notes = add_note_to_notes(notes, "question", *last_question)
                    last_question = ()

                if note_type == "question": 
                    if not any([True if cat.isdigit() else False for cat in note_category]):
                        # questions that have directly replied answers should not contain '_idx' specifiers in their
                        # category defintion
                        last_was_question = True
                        last_question = (note_category[0], note, page_num+1)
                    else:
                        category = "_".join(str(cat) for cat in note_category)
                        questions[category] = (note, page_num+1)                

                last_subject = subject_translation[annot.info["subject"]]
                
    for cat, question in questions.items():
        cat_split = cat.split("_")
        if len(cat_split) == 1:
            display_cat = "general"
        else:
            display_cat = cat_split[0]

        if cat in answers:
            notes = add_note_to_notes(notes, "answered", display_cat, *question, *answers[cat])
        else:
            notes = add_note_to_notes(notes, "question", display_cat, *question)
    return notes


def pdf_extract_info(pdf_path: str, paper_overwrite: dict[str, str], paper_misses: dict[str, str]):
    with fitz.open(pdf_path) as pdf:
        data = {}
        notes = {}

        metadata = pdf.metadata
        data, missing = _merge_extracted_and_additional(data, metadata, paper_overwrite, paper_misses, 
                                                        ("author", metadata["author"]))
        data, missing = _merge_extracted_and_additional(data, metadata, paper_overwrite, paper_misses, 
                                                        ("date", metadata["creationDate"]), extract_year_month)
        data, missing = _merge_extracted_and_additional(data, metadata, paper_overwrite, paper_misses, 
                                                        ("doi", metadata["subject"]), extract_doi)
        notes = process_notes(pdf)
    return {**data, "notes": notes}, missing


def add_pdf_info_to_collection(collection: dict, ff_paper: str, paper_overwrite: dict, paper_misses: dict):
    split_path = ff_paper.replace("\\", "/").split("/")
    idx_file = len(split_path)-1
    info_to_set = collection
    for i, subdir in enumerate(split_path):
        if subdir in info_to_set:
            info_to_set = info_to_set[subdir]
        else:
            if i < idx_file:
                info_to_set[subdir] = {}
                info_to_set = info_to_set[subdir]
            else:
                info_to_set["f_"+subdir], paper_misses = pdf_extract_info(ff_paper, paper_overwrite, paper_misses)
    return collection, paper_misses


def collect_notes(
        root: str="",
        dirname_literature: str="literature",
        write_json: bool=False,
        ff_output: str="collected_notes.json"
):
    """Collects all notes from the PDFs present in an arbitrary directory structure that lies in the 'root' 
    directory. 

    :param root: Root/parent directory of the literature, defaults to None which presupposes that this file 
    (transfer.py) is inside the first level of the literature root directory.
    :type root: str, optional
    :param write_json: Whether or not the collected notes are saved as a .json, defaults to False
    :type write_json: bool, optional
    :param ff_output: The name of the .json file with the collect notes, defaults to "collected_notes.json"
    :type ff_output: str, optional
    :param additional_information: _description_, defaults to None
    :type additional_information: str, optional
    :return: _description_
    :rtype: _type_
    """
    dir_lit = join(root, dirname_literature)
    ff_output = ff_output if ff_output is not None else join(root, ff_output)
    ff_missing = join(root, "missing.json")
    if not isfile(ff_missing):
        missing = {}
    else:
        with open(ff_missing, "r") as f_additional:
            missing = json.load(f_additional)

    ff_overwrite = join(root, "overwrite.json")
    if not isfile(ff_overwrite):
        overwrite = {}
    else:
        with open(ff_overwrite, "r") as f_overwrite:
            overwrite = json.load(f_overwrite)
            
    for paper_overwrite_field, overwrite_info in overwrite.items():
        if paper_overwrite_field in missing:
            for overwrite_field in overwrite_info:
                if overwrite_field in missing[paper_overwrite_field]:
                    raise ValueError(f"The field '{overwrite_field}' for paper {paper_overwrite_field} is tried to "
                                     "be set from 'missing.json' and 'overwrite.json'. It must only be set by one.")

    def iter_dirs(root_directory: str, current_path: str, collected_info: dict):
        for child_dir in listdir(root_directory):
            directory = join(current_path, child_dir)
            if not isdir(directory) and isfile(directory):
                if child_dir[-4:] != ".pdf":
                    raise RuntimeError(f"Found file '{child_dir}' in directory '{root_directory}'. There must only be "
                                       ".pdf files here.")
                filename = child_dir[:-4]
                paper_overwrite = overwrite[filename] if filename in overwrite else {}
                paper_misses = missing[filename] if filename in missing else {}
                collected_info, paper_misses = add_pdf_info_to_collection(collected_info, directory, paper_overwrite, 
                                                                          paper_misses)
                missing[filename] = paper_misses
                if paper_misses == {}:
                    missing.pop(filename)
                continue
            current_path = directory
            current_path, collected_info = iter_dirs(directory, current_path, collected_info)
        idx_root_until = current_path.replace("\\", "/").rfind("/")
        idx_root_until = idx_root_until if idx_root_until != -1 else 0
        return current_path[:idx_root_until], collected_info

    collected_info = {}
    current_path = dir_lit
    _, collected_info = iter_dirs(dir_lit, current_path, collected_info)

    for directory in join(root, dir_lit).replace("\\", "/").split("/"):
        collected_info = collected_info[directory]

    with open(ff_missing, "w") as f_missing:
        json.dump(missing, f_missing, indent=4)

    if write_json:
        with open(ff_output, "w") as f_notes:
            json.dump(collected_info, f_notes, indent=4)
    return collected_info

