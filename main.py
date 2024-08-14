from collect_from_pdfs import collect_notes
from collected_to_tex import collected_notes_to_tex

if __name__ == "__main__":
    collected_notes = "collected_notes.json"
    # collected_notes = collect_notes(write_json=collected_notes)
    # collected_notes_to_tex(collect_notes)
    collected_notes_to_tex(ff_json=collected_notes)