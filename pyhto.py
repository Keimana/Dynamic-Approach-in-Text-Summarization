import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from docx import Document
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import FreqDist
from collections import defaultdict
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.show = True
        self.result = True
        self.chosenFile = 'No chosen file'
        self.filename = ''
        self.fileContent = ''
        self.xstAlgoContent = 'Placeholder for existing algorithm results.'
        self.newAlgoContent = 'Placeholder for new algorithm results.'
        self.create_widgets()

    def create_widgets(self):
        self.setup_window()
        self.create_header()
        self.create_columns()
        self.create_results_window()

    def setup_window(self):
        self.screenWidth = self.winfo_screenwidth()
        self.screenHeight = self.winfo_screenheight()
        self.geometry('%dx%d' % (self.screenWidth * 0.95, self.screenHeight * 0.9))
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        tk.Frame(self, background='antiquewhite').grid(row=0, column=0, columnspan=3, sticky='nsew')

    def create_header(self):
        try:
            self.tenioPic = tk.PhotoImage(file='./player-spaceship.png').subsample(15, 14)
            self.bajePic = tk.PhotoImage(file='./player-spaceship.png').subsample(15, 14)
            self.caladiaoPic = tk.PhotoImage(file='./player-spaceship.png').subsample(15, 14)
        except tk.TclError as e:
            print("Error loading image:", e)
            self.tenioPic = self.bajePic = self.caladiaoPic = None

        header_frame = tk.Frame(self, background='antiquewhite')
        header_frame.grid(row=0, column=0, columnspan=3, sticky='ew')

        tk.Label(header_frame, text="Designing An Adaptive Dynamic Approach Applied in Text Summarization",
                 font=('Slussen Mono Black', 15), background='antiquewhite', wraplength=self.screenWidth * 0.45).pack(pady=10)

        self.summarizer = tk.Button(header_frame, text='Summarize', borderwidth=2, state='disabled', background='antiquewhite',
                                    width=12, height=2, activebackground='antiquewhite4', activeforeground="white",
                                    disabledforeground='bisque2', font=('Calibri Bold', 9), cursor='X_cursor', command=self.summarize_text)
        self.summarizer.pack(side=tk.RIGHT, padx=5)

        tk.Button(header_frame, text='Results', borderwidth=2, state='disabled', background='antiquewhite',
                  width=12, height=2, activebackground='antiquewhite4', activeforeground="white",
                  disabledforeground='bisque2', font=('Calibri Bold', 9), cursor='X_cursor').pack(side=tk.RIGHT, padx=5)

        tk.Button(header_frame, text='About', borderwidth=2, state='normal', background='antiquewhite',
                  width=12, height=2, activebackground='antiquewhite4', activeforeground="white",
                  font=('Calibri Bold', 9), cursor='hand2', command=self.open_about_modal).pack(side=tk.RIGHT, padx=5)

    def open_about_modal(self):
        # Create a new Toplevel window
        modal = tk.Toplevel(self)
        modal.title("About")
        modal.geometry("400x300")
        modal.transient(self)  # Make the window transient to the main window
        modal.grab_set()  # Block interaction with the main window

        # Add content to the modal window
        tk.Label(modal, text="Designing An Adaptive Dynamic Approach Applied in Text Summarization",
                 font=('Times New Roman Bold', 13), wraplength=350).pack(pady=10)

        tk.Label(modal, text="This is the abstract of the study...", font=('Times New Roman Normal', 11),
                 wraplength=350, justify='left').pack(pady=30)

        self.setup_researchers(modal)

        # Add a close button
        tk.Button(modal, text="Close", command=modal.destroy).pack(pady=10)

    def setup_researchers(self, parent):
        group_Members = tk.Frame(parent, background='whitesmoke', height=125, width=350)
        tk.Label(group_Members, text="Tenio", background='whitesmoke', font=('Times New Roman Bold', 8)).place(relx=0.95, anchor=tk.NE)
        tk.Label(group_Members, image=self.tenioPic).place(relx=1.05, rely=0.99, anchor=tk.SE)

        tk.Label(group_Members, text="Baje", background='whitesmoke', font=('Times New Roman Bold', 8)).place(relx=0.7, anchor=tk.N)
        tk.Label(group_Members, image=self.bajePic).place(relx=0.7, rely=0.99, anchor=tk.S)

        tk.Label(group_Members, text="Caladiao", background='whitesmoke', font=('Times New Roman Bold', 8)).place(relx=0.43, anchor=tk.NW)
        tk.Label(group_Members, image=self.caladiaoPic).place(relx=0.35, rely=0.99, anchor=tk.SW)

        group_Members.pack(pady=10)

    def create_columns(self):
        self.create_column1()
        self.create_column2()
        self.create_column3()

    def create_column1(self):
        column1 = tk.Frame(self, padx=15, pady=2, borderwidth=2, relief='groove', background='whitesmoke')
        column1.grid(row=1, column=0, sticky='nsew')

        runningFile = tk.Canvas(column1, borderwidth=2, relief='sunken')
        runningFileFrame = tk.Frame(runningFile)
        self.runningFileLabel = tk.Label(runningFileFrame, text=self.fileContent, wraplength=self.screenWidth * 0.2, justify='left')
        self.runningFileLabel.pack()
        runningFileFrame.place(anchor=tk.NW, relx=0.05, rely=0.025)
        runningFile.pack(side='bottom', fill=tk.BOTH, expand=True)

        insertFile = tk.Button(column1, text="Insert File", width=15, height=2, borderwidth=2, relief='ridge', cursor='hand2', command=self.open_file_dialog)
        insertFile.pack(side='left', padx=5, pady=5)
        self.fileLabel = tk.Label(column1, text=self.filename, padx=5, background='whitesmoke')
        self.fileLabel.pack(side='right', padx=5, pady=5)

    def create_column2(self):
        column2 = tk.Frame(self, padx=15, pady=2, borderwidth=2, relief='groove', background='whitesmoke')
        column2.grid(row=1, column=1, sticky='nsew')

        xstAlgoCanvas = tk.Canvas(column2, borderwidth=2, relief='sunken')
        xstAlgoFrame = tk.Frame(xstAlgoCanvas)
        tk.Label(xstAlgoFrame, text=self.xstAlgoContent, wraplength=self.screenWidth * 0.25, justify='left').pack()
        xstAlgoFrame.place(anchor=tk.NW, relx=0.05, rely=0.025)
        xstAlgoCanvas.pack(side='bottom', fill=tk.BOTH, expand=True)
        tk.Label(column2, text='Existing Algorithm', pady=6, font=('Calibri Bold', 15), background='whitesmoke').pack(side='top')

    def create_column3(self):
        column3 = tk.Frame(self, padx=15, pady=2, borderwidth=2, relief='groove', background='whitesmoke')
        column3.grid(row=1, column=2, sticky='nsew')

        newAlgoCanvas = tk.Canvas(column3, borderwidth=2, relief='sunken')
        newAlgoFrame = tk.Frame(newAlgoCanvas)
        tk.Label(newAlgoFrame, text=self.newAlgoContent, wraplength=self.screenWidth * 0.25, justify='left').pack()
        newAlgoFrame.place(anchor=tk.NW, relx=0.05, rely=0.025)
        newAlgoCanvas.pack(side='bottom', fill=tk.BOTH, expand=True)
        tk.Label(column3, text='New Algorithm', pady=6, font=('Calibri Bold', 15), background='whitesmoke').pack(side='top')

    def create_results_window(self):
        # Create results window frame
        self.resultsWindow = tk.Frame(self, padx=15, pady=2, borderwidth=2, relief='groove', background='whitesmoke')
        self.resultsWindow.grid(row=1, column=2, sticky='nsew')

        # Add title to results window
        title_label = tk.Label(self.resultsWindow, text="Summary Results", font=('Calibri Bold', 15), background='whitesmoke')
        title_label.pack(pady=5)

        # Add text widget for results
        self.resultsText = tk.Text(self.resultsWindow, wrap='word')
        self.resultsText.pack(expand=True, fill=tk.BOTH)

    def summarize_text(self):
        if self.fileContent:
            # Apply the existing algorithm with memoization
            self.xstAlgoContent = self.generate_summary(self.fileContent)
            self.resultsText.delete(1.0, tk.END)
            self.resultsText.insert(tk.END, self.xstAlgoContent)

    def generate_summary(self, text, num_sentences=3):
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.probability import FreqDist
        import re

        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        freq_dist = FreqDist(word.lower() for word in words if word.isalpha())

        # Memoization approach
        sentence_scores = {}

        def get_sentence_score(sentence):
            if sentence in sentence_scores:
                return sentence_scores[sentence]

            score = 0
            for word in word_tokenize(sentence):
                if word.lower() in freq_dist:
                    score += freq_dist[word.lower()]

            sentence_scores[sentence] = score
            return score

        # Calculate sentence scores
        sentence_scores = {sentence: get_sentence_score(sentence) for sentence in sentences}

        # Filter sentences to exclude those with any letters
        filtered_sentences = self.filter_sentences_without_letters(sentences)

        # Sort filtered sentences and get the top ones
        summarized_sentences = sorted(filtered_sentences, key=lambda s: sentence_scores.get(s, 0), reverse=True)[:num_sentences]
        return ' '.join(summarized_sentences)

    def filter_sentences_without_letters(self, sentences):
        import re
        # Regex to check if a sentence contains any letters
        pattern = re.compile(r'[a-zA-Z]')
        return [sentence for sentence in sentences if not pattern.search(sentence)]

    def open_file_dialog(self):
        from tkinter import filedialog
        from docx import Document

        # Open file dialog to choose a file
        self.filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Word Documents", "*.docx")])
        if self.filename:
            self.fileLabel.config(text=self.filename)
            self.read_file_content()

    def read_file_content(self):
        if self.filename.endswith('.txt'):
            with open(self.filename, 'r') as file:
                self.fileContent = file.read()
        elif self.filename.endswith('.docx'):
            doc = Document(self.filename)
            self.fileContent = ' '.join([para.text for para in doc.paragraphs])
        self.runningFileLabel.config(text=self.fileContent[:1000] + ('...' if len(self.fileContent) > 1000 else ''))
        self.summarizer.config(state='normal')

    def toggle_about(self):
        # Show or hide the about window
        if self.show:
            self.aboutWindow.grid(row=1, column=0, columnspan=3, sticky='nsew')
            self.show = False
        else:
            self.aboutWindow.grid_forget()
            self.show = True

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
