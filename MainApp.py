import tkinter as tk
from text_processor import TextProcessor
from newAlgorithmProcessor import NewAlgorithmProcessor
from userInterface import UIComponent  
class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text Summarization Application")
        self.root.geometry("1440x570")  # Adjust size 

        # Initialize your text processor and new algorithm processor
        text_processor = TextProcessor()
        new_algorithm_processor = NewAlgorithmProcessor()

        # Create the UIComponent with the necessary processors
        self.ui = UIComponent(self.root, text_processor, new_algorithm_processor)
        

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
