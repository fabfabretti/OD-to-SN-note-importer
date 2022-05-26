import dateparser
import json
import sys
import os

class NoteEntry:
  title = ""
  body = ""
  created = ""
  updated = ""


# TODO: add TOKEN separator function

def load_raw_notes(filename:str) -> list:
  with open(filename,encoding="utf8") as f:
    raw_text = f.read()
    raw_notes = raw_text.split("[TOKEN]")
    print("[✓] Loading raw OD notes: {} notes found...".format(len(raw_notes)))
    return raw_notes

def parse_raw_notes(raw_notes:list) -> list:

  parsed_notes = []
  for raw_note in raw_notes:
    curr_note = NoteEntry()
    curr_note.title, rest_of_note = raw_note.split("\n", 1)
    curr_note.created, rest_of_note = rest_of_note.split("\n", 1)
    if "Updated: " in rest_of_note:
      curr_note.updated, rest_of_note = rest_of_note.split("\n", 1)
    curr_note.body = rest_of_note;
    parsed_notes.append(curr_note)
  print("\t[✓] Notes parsed into objects...")

  note_id = 0;
  for note in parsed_notes:
    note.created = dateparser.parse(note.created[9:])
    note.updated = dateparser.parse(note.updated[9:])
    if note.updated is None:
      print("! No update date found in entry {} !".format(note_id))
      note.updated = note.created
    note_id += 1
  print("\t[✓] Dates string parsed into date objects...")
  return parsed_notes

def load_SN_importfile() -> map:
  if not os.path.exists("sntools-output"):
    os.makedirs("sntools-output")
  with open('sntools-output/sn-import-file.txt', 'r', encoding="utf-8") as f:
    json_notes = json.load(f)
  print("[✓] Loaded SN Import file as json")
  return json_notes

########################################## SCRIPT

print("\n---- Part 1: OD file -> Plain Text files\n")

if not os.path.exists("od-output"):
  os.makedirs("od-output")

# Loads notes and saves them as strings
raw_notes = load_raw_notes(sys.argv[1])

# Parses strings into NoteEntry objects.
parsed_notes = parse_raw_notes(raw_notes)

# Writes plaintext placeholder files to give to the SN tools page
note_id = 0;

if not os.path.exists("sntools-input"):
  os.makedirs("sntools-input")

for note in parsed_notes:
    f = open("sntools-input/{}.txt".format(note_id), "w", encoding="utf8")
    f.write(note.body)
    note_id += 1
print("[✓] Input files generated...")


# TODO: selenium to get sn-import-file automatically

#input("Upload contents of sntools-input to https://standardnotes.com/tools and save resulting file in this folder. Then press enter.\n\n...")


print("---- Part 2: SN Import file -> Injected SN Import file\n")

# Load SN Import File as json
json_notes = load_SN_importfile();

# For each note, inject data into map/json
note_id = 1
for i in range(1, len(parsed_notes)+1):
  json_notes["items"][i]["created_at"] = parsed_notes[i-1].created.isoformat() + ".000Z"
  json_notes["items"][i]["updated_at"] = parsed_notes[i-1].updated.isoformat()  + ".000Z"
  json_notes["items"][i]["content"]["title"] = parsed_notes[i - 1].title
  json_notes["items"][i]["content"]["text"] = parsed_notes[i - 1].body

# Save injected file as txt
if not os.path.exists("RESULT"):
  os.makedirs("RESULT")

with open ('RESULT/sn-import-file-INJECTED.txt','w',encoding='utf-8') as f:
  json.dump(json_notes,f, indent=4)
print("[✓] Saved the injected file")


print("\nDone!")