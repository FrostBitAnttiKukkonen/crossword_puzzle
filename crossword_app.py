import random
import tkinter as tk
from tkinter import ttk

# Only pick variables and functions we actually use
from wordbank import (
    WORD_BANK,
    MIN_WORDS,
    MAX_WORDS,
    MIN_LEN,
    MAX_LEN,
    pick_words,
    filter_valid_words
)

# grid = {(row, col): letter}
def letter_at(grid, row, col):
    return grid.get((row, col))

def fits(grid, size, word, row, col, direction):
    if direction == "across":
        dr, dc = (0, 1)
    else:
        dr, dc = (1, 0)

    if not (0 <= row < size and 0 <= col < size):
        return False
    
    end_row = row + dr * (len(word) - 1)
    end_col = col + dc * (len(word) - 1)

    if not (0 <= end_row < size and 0 <= end_col < size):
        return False

    for i, letter in enumerate(word):
        existing = letter_at(grid, row + dr * i, col + dc * i)
        if existing is not None and existing != letter:
            return False  # would overwrite a different letter
            
    before = letter_at(grid, row - dr, col - dc)
    after = letter_at(grid, row + dr * len(word), col + dc * len(word))

    if before is not None or after is not None:
        return False
    
    return True

def place_word(grid, placements,
               word, row, col, direction):
    """Write all letters of `word` into the grid and log the placement.

    The one function allowed to MUTATE the grid: because callers
    checked fits() first. placements grows one entry:
        (word, row, col, direction)
    Direction is stored as the STEP of the walk: across moves
    (0, +1) per letter, down moves (+1, 0)
    """
    dr, dc = (0, 1) if direction == "across" else (1, 0)
    for i, letter in enumerate(word):
        grid[(row + dr * i, col + dc * i)] = letter
    placements.append((word, row, col, direction))

def build_grid(words, size):
    """Make a crossword: return (grid, placements).

    Returns TWO values: normal in Python:
        grid, placements = build_grid(my_words, 30)
    """
    grid: dict = {}
    placements: list = []
    words = sorted(words, key=len, reverse=True)

    first = words[0]
    start = size // 2 - len(first) // 2
    place_word(grid, placements, first, start, start, "across")

    for word in words[1:]:
        placed = False
        # random.sample shuffles the attempt order so two runs
        # with the same words can look different.
        for placed_word, p_row, p_col, p_dir in random.sample(
            placements, len(placements)
        ):
            # A new word crosses an across-word going DOWN,
            # and a down-word going ACROSS. same-direction
            # overlap would just sit on top of the other word.
            for direction in ("down", "across"):
                if direction == p_dir:
                    continue
                # Find every position i in `word` whose letter
                # also exists in placed_word, and try to put
                # that letter exactly onto the placed letter.
                for i, letter in enumerate(word):
                    if letter not in placed_word:
                        continue
                    j = placed_word.index(letter)
                    if p_dir == "across":
                        row, col = p_row - i, p_col + j
                    else:
                        row, col = p_row + j, p_col - i
                    if fits(grid, size, word, row, col, direction):
                        place_word(grid, placements,
                                   word, row, col, direction)
                        placed = True
                        break              # leave the LETTER loop
                if placed:                 # leave the DIRECTION loop
                    break
            if placed:                     # leave the PLACEMENTS loop
                break
        if not placed:
            # Fallback: park the word on the left edge.
            # BUG WARNING: such a word is in the grid
            # but NOT connected to the rest of the puzzle —
            # solvers see a floating island of letters.
            for row in range(size):
                if fits(grid, size, word, row, 0, "across"):
                    place_word(grid, placements, word, row, 0, "across")
                    break
    return grid, placements

def grid_bounds(grid):
    """(min_row, min_col, max_row, max_col) actually used."""
    rows = [r for r, _ in grid]
    cols = [c for _, c in grid]
    return min(rows), min(cols), max(rows), max(cols)

def make_clues(placements, fun_facts):
    """One clue line per word, numbered like a real puzzle.

    Real crossword numbering is more complex (by grid position),
    but "1. Across ..." per placement is fine.
    The fun_facts dict lets you supply real definitions later:
        make_clues(placements, {"GARDEN": "plants grow here"})
    """
    lines = []
    for n, (word, row, col, direction) in enumerate(placements, 1):
        kind = "Across" if direction == "across" else "Down"
        hint = (fun_facts or {}).get(
            word, f"a {len(word)}-letter word meaning... {word}!")
        lines.append(f"{n}. {kind} ({len(word)} letters): {hint}")
    return lines

# GUI side
PUZZLE = {"entries": {}, "solution": {}, "layout": None, "root": None}


def new_puzzle():
    """Callback of the "New puzzle" button: build everything fresh."""
    widgets = PUZZLE["widgets"]
    try:
        how_many = int(widgets["count_var"].get())
    except ValueError:
        how_many = 15

    valid_words = filter_valid_words(WORD_BANK)
        
    words = pick_words(how_many, valid_words)              # console logic, reused!

    size = max(len(w) for w in words) + 8
    grid, placements = build_grid(words, size) 

    PUZZLE["solution"] = dict(grid)          # <-remember the answer
    PUZZLE["layout"] = (grid, placements)
    draw_grid(grid)                           # <-but show blanks
    fill_clues(placements)
    widgets["status"].config(text="New puzzle ready — start typing!", fg="blue")


def draw_grid(grid):
    """Create one small Entry per filled cell.

    Subtlety: layout coordinates can be anywhere in the size x
    size area (even far from 0,0 after crossings). grid_bounds()
    gives the really-used rectangle, and (row - min_r) slides the
    whole puzzle nicely to the top-left corner of the window
    """
    entries = PUZZLE["entries"]
    for entry in entries.values():
        entry.destroy()          # forget the OLD puzzle before
    entries.clear()               # drawing the new one, or both
                                  # would overlap in the frame
    grid_frame = PUZZLE["widgets"]["grid_frame"]
    min_r, min_c, max_r, max_c = grid_bounds(grid)
    grid_frame.pack_propagate(False)

    for (row, col), letter in sorted(grid.items()):
        r, c = row - min_r, col - min_c
        e = tk.Entry(
            grid_frame, width=1, justify="center",
            font=("Arial", 14, "bold"),
            relief="solid", bd=1,
            exportselection=False,  # let tkinter keep focus
        )                           # per-box: otherwise typing
        e.grid(row=r, column=c, ipadx=2, ipady=2)
        e.bind("<KeyRelease>", on_key)
        entries[(row, col)] = e


def fill_clues(placements):
    clue_list = PUZZLE["widgets"]["clue_list"]
    clue_list.delete(0, tk.END)     # same "clear first!" rule
    for line in make_clues(placements, {}):
        clue_list.insert(tk.END, line)


# event handlers
def on_key(event):
    """After typing a letter, jump to the next cell.

    Simple version: walk cells in reading order (top row,
    then second row...)
    """
    if not event.char.isalpha():
        return
    # find which grid position the event happened in, then hop
    # to the next entry in (row, col) order: sorted() gives us
    # reading order for free because tuples compare nicely.
    entries = PUZZLE["entries"]
    order = sorted(entries)
    current = [k for k in entries if entries[k] is event.widget]
    if current:
        idx = order.index(current[0])
        if idx + 1 < len(order):
            entries[order[idx + 1]].focus_set()


def check_answers():
    """Count cells whose typed letter equals the solution."""
    entries = PUZZLE["entries"]
    correct = sum(
        1 for pos, letter in PUZZLE["solution"].items()
        if entries[pos].get().lower() == letter
    )
    total = len(PUZZLE["solution"])
    status = PUZZLE["widgets"]["status"]
    if correct == total:
        status.config(text="All letters correct — well done!", fg="green")
    else:
        status.config(text=f"{correct}/{total} letters correct", fg="blue")


def reveal_letter():
    """Help button: fill in one still-wrong cell.

    BUG WARNING: insert(0, ...) PUTS the letter in
    front of whatever is already there. If the user typed a
    wrong guess "x", the box ends up holding "?x": two
    characters in a one-letter box, and the check button
    then grades a wrong answer.
    """
    entries = PUZZLE["entries"]
    wrong = [pos for pos, letter in PUZZLE["solution"].items()
             if entries[pos].get().lower() != letter]
    if wrong:
        pos = random.choice(wrong)
        entries[pos].insert(0, PUZZLE["solution"][pos])
        entries[pos].config(fg="dark orange")


def show_solution():
    """Fill every cell with its letter (this one clears first)."""
    for pos, letter in PUZZLE["solution"].items():
        entry = PUZZLE["entries"][pos]
        entry.delete(0, tk.END)      # <- the clear-first pattern
        entry.insert(0, letter)     #    reveal_letter forgets
        entry.config(fg="red")
    PUZZLE["widgets"]["status"].config(
        text="Solution revealed — try a new puzzle!", fg="red")


# building the window
def build_window(root):
    """Create every widget; store the ones callbacks need later."""
    widgets: dict = {}
    PUZZLE["widgets"] = widgets
    PUZZLE["root"] = root
    root.title("Crossword builder — full edition")

    # toolbar row:
    bar = tk.Frame(root)
    bar.pack(fill="x", padx=8, pady=5)

    tk.Label(bar, text="Words:").pack(side="left")
    widgets["count_var"] = tk.StringVar(value="12")
    # ttk.Spinbox: an Entry WITH up/down arrows AND built-in.
    # bounds: tkinter enforcing our 10-20 rule
    spin = ttk.Spinbox(bar, from_=MIN_WORDS, to=MAX_WORDS, width=4,
                       textvariable=widgets["count_var"])
    spin.pack(side="left", padx=4)

    tk.Button(bar, text="New puzzle", command=new_puzzle).pack(side="left", padx=4)
    tk.Button(bar, text="Check answers", command=check_answers).pack(side="left", padx=4)
    tk.Button(bar, text="Reveal one letter", command=reveal_letter).pack(side="left", padx=4)
    tk.Button(bar, text="Solution", command=show_solution).pack(side="left", padx=4)

    widgets["status"] = tk.Label(bar, text="Ready", fg="blue")
    widgets["status"].pack(side="right")

    # puzzle area + clue list with a draggable divider
    # PanedWindow = a divider the USER can drag: polite interfaces
    # let people widen the clues themselves for bigger fonts.
    panes = tk.PanedWindow(root, orient="horizontal")
    panes.pack(fill="both", expand=True, padx=8, pady=5)
    widgets["grid_frame"] = tk.Frame(panes)
    widgets["clue_list"] = tk.Listbox(panes, width=48)
    panes.add(widgets["grid_frame"], minsize=360)
    panes.add(widgets["clue_list"])

    # And fill it immediately, like build_window did in skeleton earlier
    new_puzzle()


def main():
    root = tk.Tk()               # 1. create the main window
    build_window(root)           # 2. fill it
    root.mainloop()               # 3. hand control to the user


if __name__ == "__main__":
    main()