import tkinter as tk

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

# Holds tkinters widgets
UI_STATE = {
    "widgets": {}, # For example a label, textbox, etc
    "words": [], # Currenly picked words
}

# Callbacks
def on_pick_words() -> None:
    """  
    """

    widgets = UI_STATE["widgets"]

    try:
        # Try to get integer from user through UI
        how_many = int(widgets["count_entry"].get())
    except ValueError:
        how_many = 15   # exactly step 1's "not a number" fallback —
                        # same rule, different interface

    valid_words = filter_valid_words(WORD_BANK)

    UI_STATE["words"] = pick_words(how_many, valid_words)

    word_listbox = UI_STATE["widgets"]["word_listbox"]
    word_listbox.delete(0, tk.END)

    for word in UI_STATE["words"]:
        word_listbox.insert(tk.END, word)

    UI_STATE["widgets"]["status"].config(
        text=f"Picked {len(UI_STATE['words'])} words. "
             "Puzzle grid comes in step 3!"
    )

def build_window(root: tk.Tk) -> None:
    """ Create every widget """

    widgets = UI_STATE["widgets"]

      # A Label is just text on the screen.
    widgets["title"] = tk.Label(
        root,
        text=f"Pick {MIN_WORDS}-{MAX_WORDS} words for your puzzle",
        font=("Arial", 14, "bold"),
    )
    widgets["title"].pack(pady=10)

    widgets["count_label"] = tk.Label(root, text="How many words?")
    widgets["count_label"].pack()

    # An Entry is a one-line typing box (the GUI's input()).
    widgets["count_entry"] = tk.Entry(root, justify="center", width=5)
    widgets["count_entry"].insert(0, "12")   # pre-fill a default,
    widgets["count_entry"].pack(pady=5)      #  like step 1's fallback

    # A Button needs two things: text and a CALLBACK.
    # Note we pass the FUNCTION itself (no parentheses!)
    # "call on_pick_words later" not "call it right now".
    widgets["pick_button"] = tk.Button(
        root, text="Pick words", command=on_pick_words
    )
    widgets["pick_button"].pack(pady=5)

    # A Listbox = a scrollable list of lines (the GUI's print()).
    widgets["word_listbox"] = tk.Listbox(root, width=30, height=MAX_WORDS)
    widgets["word_listbox"].pack(padx=10, pady=10)

    # A status Label: the polite way to tell the user things
    # succeeded or failed, instead of print() in a terminal
    # they may not even be looking at.
    widgets["status"] = tk.Label(root, text="Ready.")
    widgets["status"].pack(pady=5)
    widgets["status"].config(
        text=f"Word bank holds {len(filter_valid_words(WORD_BANK))} words."
    )

def main():
    root = tk.Tk()
    build_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()
