import os
import json

def get_nb_source_cells(nb_as_json):
  source_cells = []
  for cell in nb_as_json["cells"]:
    assert "cell_type" in cell.keys()
    if cell["cell_type"] == "markdown":
        continue
    
    # It would be great if we could return the cell ID for every cell,
    # but it's not available. So, callers have to use the index
    # as a unique id.

    # Here `<=` means subset
    assert {"source"} <= cell.keys()
    # Apparently every line is a different list element even in JSON.
    # I think this will just create problems so I'm joining them.
    source_as_list_of_lines = cell["source"]
    # Apparently, some cells can be null
    if source_as_list_of_lines is None:
      continue
    source = "".join(source_as_list_of_lines)
    source_cells.append(source)
  
  return source_cells

def open_and_get_source_cells(nb_path):
  f = open(nb_path)
  nb_as_json = json.load(f)
  f.close()
  return get_nb_source_cells(nb_as_json)

def extract_json_cell_stats(s: str):
  # Yes, I know I can use regular expressions but the
  # code becomes totally unreadable.
  lines = s.split('\n')
  into = False
  buf = ""
  cells = []
  for l in lines:
    if "[IREWRITE JSON]" in l:
      assert into == False
      into = True
      continue
    if "[IREWRITE END JSON]" in l:
      assert into == True
      into = False
      cells.append(buf)
      buf = ""
      continue
    if into:
      buf = buf + l + "\n"
  
  return cells

def ns_to_ms(ns):
  return ns / 1_000_000

def write_to_file(filename, txt):
  f = open(filename, 'w')
  f.write(txt + "\n")
  f.close()