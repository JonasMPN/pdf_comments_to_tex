from collect_from_pdfs import collect_notes
from collected_to_tex import collected_notes_to_tex

if __name__ == "__main__":
    file_collected_notes = "collected_notes.json"
    collected_notes = collect_notes(file_json=file_collected_notes)
    collected_notes_to_tex(collected_notes)