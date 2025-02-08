import tkinter as tk


class EditableFormattedListbox:
    def __init__(self, parent):
        self.text_widget = tk.Text(parent)
        self.items = [
            ("Apple", "bold"),
            ("Banana", "italic"),
            ("Cherry", "underline"),
            ("Date", "normal")
        ]

        self.draw_items()

    def draw_items(self):
        self.text_widget.delete(1.0, tk.END)  # Clear previous content

        for text, style in self.items:
            if style == "bold":
                self.text_widget.insert(tk.END, text + "\n", "bold")
            elif style == "italic":
                self.text_widget.insert(tk.END, text + "\n", "italic")
            elif style == "underline":
                self.text_widget.insert(tk.END, text + "\n", "underline")
            else:
                self.text_widget.insert(tk.END, text + "\n")

        self.text_widget.tag_configure("bold", font=("Arial", 12, "bold"))
        self.text_widget.tag_configure("italic", font=("Arial", 12, "italic"))
        self.text_widget.tag_configure(
            "underline", font=("Arial", 12, "underline"))

    def pack(self, **kwargs):
        """Überladene Pack-Methode für das Text-Widget."""
        self.text_widget.pack(**kwargs)

    def on_click(self, event):
        """Handle click on text to edit the item."""
        index = self.text_widget.index(f"@{event.x},{event.y}")
        # Get line number of clicked text
        line_number = int(index.split('.')[0]) - 1

        if line_number < len(self.items):
            current_text = self.items[line_number][0]
            self.edit_item(line_number, current_text)

    def edit_item(self, line_number, current_text):
        """Edit the selected item in the Text widget."""
        self.text_widget.delete(
            f"{line_number + 1}.0", f"{line_number + 1}.end")
        self.text_widget.insert(
            f"{line_number + 1}.0", current_text, "editable")

        # Create a popup to allow text modification
        popup = tk.Toplevel()
        popup.geometry("200x100")
        entry = tk.Entry(popup)
        entry.insert(tk.END, current_text)
        entry.pack(pady=20)
        entry.bind("<Return>", lambda event: self.save_edited_item(
            popup, entry, line_number))

    def save_edited_item(self, popup, entry, line_number):
        """Save the edited text."""
        edited_text = entry.get()
        self.items[line_number] = (edited_text, self.items[line_number][1])
        self.draw_items()
        popup.destroy()
