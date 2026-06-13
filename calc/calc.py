import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#2c3e50")
        self.root.title("Calculator")
        self.root.geometry("300x400")
        self.root.resizable(False, False)

        self.equation = ""
        self.display_var = tk.StringVar()

        # Display screen
        self.entry = tk.Entry(root, textvariable=self.display_var, font=("Arial", 24), 
                              borderwidth=5, relief="flat", justify="right", 
                              bg="#ecf0f1", fg="#2c3e50")
        self.entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=20)

        # Button labels
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]

        # Create and place buttons
        row_val = 1
        col_val = 0
        for button in buttons:
            action = lambda x=button: self.on_button_click(x)
            
            # Determine button colors
            if button == '=':
                bg_color, fg_color = "#2ecc71", "white"
            elif button == 'C':
                bg_color, fg_color = "#e74c3c", "white"
            elif button in ['/', '*', '-', '+']:
                bg_color, fg_color = "#f39c12", "white"
            else:
                bg_color, fg_color = "#34495e", "white"

            tk.Button(root, text=button, width=5, height=2, font=("Arial", 14),
                      bg=bg_color, fg=fg_color, relief="flat",
                      command=action).grid(row=row_val, column=col_val, sticky="nsew", padx=2, pady=2)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

        # Configure grid weights
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)
        for i in range(1, 5):
            root.grid_rowconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == 'C':
            self.equation = ""
            self.display_var.set("")
        elif char == '=':
            try:
                # Using eval for simplicity in this basic example
                result = str(eval(self.equation))
                self.display_var.set(result)
                self.equation = result
            except ZeroDivisionError:
                messagebox.showerror("Error", "Cannot divide by zero")
                self.equation = ""
                self.display_var.set("")
            except Exception:
                messagebox.showerror("Error", "Invalid input")
                self.equation = ""
                self.display_var.set("")
        else:
            self.equation += str(char)
            self.display_var.set(self.equation)

if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
