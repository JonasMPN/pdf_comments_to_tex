# Overview
Running `main.py` collects all notes from given PDFs and creates a .tex file. This .tex file can, e.g., be copied into Overleaf and be compiled immediately. 

# Setup
Todo.

# Note extraction and sorting; create .json
- [x] extract notes from one .pdf
- [x] extract notes from the whole "library"
- [x] support incorporating external metadata
- [x] support note categories
- [x] support note subcategories
- [x] support question-answer pairs that are not a note-and-note-answer
- [x] add special categories: general, question, answered
- [ ] create second .json in which all notes for a certain category or subcategory are combined
- [ ] restructuring of code; adding comments
- [ ] write all existing categroies & subcategories to categories.json
- [ ] allow categories.json to map categories to one another
- [ ] allow multiple categories per note

# Creating the .tex file
- [x] create section structure based on .json structure
- [x] add papername, author, date, doi
- [x] method to create tables for general, question, answered, "all others"
- [x] adjust table creation to adhere to maximum width (class LimitTabular)
- [ ] turn author(s), date, doi, into single row three column table 
- [ ] add the "summary" as a block of text below the paper definition   
- [ ] create .tex for the second .json (see Note extraction and sorting)
- [ ] restructuring of code; adding comments
- [ ] sort category tables by "key", "general", then the rests

# Ideas to consider
- [ ] None yet
