# Overview

Running `main.py` collects all notes from given PDFs and creates a .tex file. This .tex file can e.g. be copied into Overleaf and compiled immediately.

# Setup
Easiest:
1. Clone repository.
2. Create directory "literature" in the same directory as where this repository was cloned into.
3. Fill directory "literature" with your literature*.
4. Run `main.py`.
5. Compile the created "collected.tex", e.g. by copying it into Overleaf.

Read [Current limitations](#known-current-limitations).

# Known current limitations

* [ ] a dictionary can only contain dictionaries or .pdfs, not a mix
* [ ] notes that only specify a category but are empty otherwise throw errors (completely empty notes probably, too)
* [ ] only works with notes created in PDF viewers that are in English/German (at least Adobe Acrobat annotates their notes based on the language settings)
* [ ] publication dates in the metadata must be of a specific format
* [ ] a general note (note without category) cannot contain ":" 

# Note extraction and sorting; create .json

- [X] extract notes from one .pdf
- [X] extract notes from the whole "library"
- [X] support incorporating external metadata
- [X] support note categories
- [X] support note subcategories
- [X] support question-answer pairs that are not a note-and-note-answer
- [X] add special categories: general, question, answered
- [ ] create second .json in which all notes for a certain category or subcategory are combined
  - [ ] sort notes by year
- [ ] restructuring of code; adding comments
- [ ] write all existing categroies & subcategories to categories.json
- [ ] allow categories.json to map categories to one another
- [ ] allow multiple categories per note
- [ ] test for comments added in other suites than Adobe Acrobat Reader
- [ ] discard and collect (to read later) PDFs that have no notes 
  - [ ] add a "read later" category that adds this PDF to the list of PDFs that should still be read 
- [ ] add logging

# Creating the .tex file

- [X] create section structure based on .json structure
- [X] add paper name, author, date, doi
- [X] method to create tables for general, question, answered, "all others"
- [X] adjust table creation to adhere to maximum width (class LimitTabular)
- [ ] turn author(s), date, doi, into single row three column table
- [ ] add the "summary" as a block of text below the paper definition
- [ ] create .tex for the second .json (see Note extraction and sorting)
- [ ] restructuring of code; adding comments
- [ ] sort category tables by "key", "general", then the rests
- [ ] add logging
- [ ] support latex commands in notes
  - [ ] for the creation of .tex
  - [ ] for the creation of .md

# Ideas to consider

- [ ] use of longtable instead of table
- [ ] support for .md files; possibly:
  - [ ] each paper gets it's own .md (take folder structure, too?)
  - [ ] create MOC from it (add MOC-category comment, MOC could additionally be taken from folder structure)
