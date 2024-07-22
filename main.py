from collect_from_pdfs import collect_notes
from collected_to_tex import collected_json_to_tex

if __name__ == "__main__":
    collect_notes(write_json=True)
    collected_json_to_tex()