import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from file_loader import FileLoader
from text_processor import TextProcessor
import time
import threading
from PIL import Image, ImageTk
from PIL import Image, ImageTk, ImageDraw


class UIComponent:
    def __init__(self, parent, text_processor, new_algorithm_processor):
        self.parent = parent
        self.text_processor = text_processor
        self.new_algorithm_processor = new_algorithm_processor
        self.create_widgets()

    def create_widgets(self):
        self.create_header()
        self.create_columns()
        # Configure main window grid
        self.parent.grid_rowconfigure(0, weight=0)  # Header row
        self.parent.grid_rowconfigure(1, weight=1)  # Columns row
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)


    def create_header(self):
        header_frame = tk.Frame(self.parent, background='#121212')
        header_frame.grid(row=0, column=0, columnspan=3, sticky='ew')

        screen_width = self.parent.winfo_screenwidth()

        tk.Label(header_frame, text="Adaptive Dynamic Approach Applied in Text Summarization",
                 font=('Slussen Mono', 15), fg="white", bg="#121212", wraplength=screen_width * 0.45).pack(pady=15)

        self.summarizer = tk.Button(header_frame, text='Summarize', borderwidth=1, state='disabled', 
                                     width=12, height=2, activebackground='#FF5555', 
                                     activeforeground="gray", disabledforeground='#555555', font=('Lato Bold', 9), 
                                     cursor='X_cursor', command=self.on_summarize_click, bg='#232323', fg='white')
        self.summarizer.pack(side=tk.RIGHT, padx=5)

        tk.Button(header_frame, text='Presentation of Data', borderwidth=1, 
                width=16, height=2, activebackground='#ABDBE6', activeforeground="white",
                disabledforeground='#555555', font=('Lato Bold', 9), cursor='X_cursor',
                bg='#232323', fg='white', command=self.open_presentation_modal).pack(side=tk.RIGHT, padx=5)

        tk.Button(header_frame, text='About', borderwidth=1, state='normal', 
                  width=12, height=2, activebackground='#ABDBE6', activeforeground="white",
                  font=('Lato Bold', 9), cursor='hand2', bg='#232323', fg='white', command=self.open_about_modal).pack(side=tk.RIGHT, padx=5)


        self.clear_button = tk.Button(header_frame, text='Clear All', borderwidth=1, state='normal', 
                                      width=12, height=2, activebackground='#ABDBE6', 
                                      activeforeground="white", font=('Lato Bold', 9), cursor='hand2', bg='#232323', fg='white', 
                                      command=self.clear_all_data)
        self.clear_button.pack(side=tk.RIGHT, padx=5)

    def create_columns(self):
        self.create_column1()
        self.create_column2()
        self.create_column3()

    def create_column1(self):
        self.column1 = tk.Frame(self.parent, width=300, height=500, padx=15, pady=2, borderwidth=1, relief='groove', background='#232323')
        self.column1.grid(row=1, column=0)
        self.column1.grid_propagate(False)  # Prevents resizing

        tk.Label(self.column1, text='File Content Preview', pady=6, font=('Lato Bold', 15), background='#232323', fg='#E0E0E0').pack(side='top')

        # Create a Scrollbar and associate it with the Text widget
        text_scrollbar = tk.Scrollbar(self.column1)
        text_scrollbar.pack(side='right', fill=tk.Y)

        self.file_content_text = tk.Text(self.column1, wrap='word', background='#121212', fg='#E0E0E0', insertbackground='white', yscrollcommand=text_scrollbar.set)
        self.file_content_text.pack(expand=True, fill=tk.BOTH)

        # Configure the scrollbar to scroll the Text widget
        text_scrollbar.config(command=self.file_content_text.yview)

        # Insert File button and File Destination label placed below the file content text
        button_frame = tk.Frame(self.column1, background='#232323')
        button_frame.pack(side='bottom', fill=tk.X, pady=5)

        self.insert_file_button = tk.Button(button_frame, text="Insert File", width=15, height=2, borderwidth=1, relief='ridge', cursor='hand2', bg='#C6DEF1', fg='white', command=self.on_open_file_click)
        self.insert_file_button.pack(side='left', padx=5)

        self.file_label = tk.Label(button_frame, text="File Destination", padx=5, background='#232323', fg='#E0E0E0')
        self.file_label.pack(side='right', padx=5)

    def create_column2(self):
        self.column2 = tk.Frame(self.parent, width=300, height=400, padx=15, pady=26, borderwidth=1, relief='groove', background='#232323')
        self.column2.grid(row=1, column=1)
        self.column2.grid_propagate(False)  # Prevents resizing

        tk.Label(self.column2, text='Existing Algorithm', pady=6, font=('Lato Bold', 15), background='#232323', fg='#E0E0E0').pack(side='top')

        # Create a Scrollbar and associate it with the Text widget
        text_scrollbar = tk.Scrollbar(self.column2)
        text_scrollbar.pack(side='right', fill=tk.Y)

        self.resultsText = tk.Text(self.column2, wrap='word', state='disabled', background='#121212', fg='#E0E0E0', insertbackground='white', yscrollcommand=text_scrollbar.set)
        self.resultsText.pack(expand=True, fill=tk.BOTH)

        # Configure the scrollbar to scroll the Text widget
        text_scrollbar.config(command=self.resultsText.yview)

    def create_column3(self):
        self.column3 = tk.Frame(self.parent, width=300, height=400, padx=15, pady=26, borderwidth=1, relief='groove', background='#232323')
        self.column3.grid(row=1, column=2)
        self.column3.grid_propagate(False)  # Prevents resizing

        tk.Label(self.column3, text='New Algorithm', pady=6, font=('Lato Bold', 15), background='#232323', fg='#E0E0E0').pack(side='top')

        # Create a Scrollbar
        text_scrollbar = tk.Scrollbar(self.column3)
        text_scrollbar.pack(side='right', fill=tk.Y)

        self.newAlgoResultsText = tk.Text(self.column3, wrap='word', state='disabled', background='#121212', fg='#E0E0E0', insertbackground='white', yscrollcommand=text_scrollbar.set)
        self.newAlgoResultsText.pack(expand=True, fill=tk.BOTH)

        # Configure the scrollbar to scroll the Text widget
        text_scrollbar.config(command=self.newAlgoResultsText.yview)

    def on_open_file_click(self):
        file_loader = FileLoader()
        filename, file_content = file_loader.open_file()

        if not filename or not file_content:
            messagebox.showerror("Error", "No file selected or file content is empty.")
            return

        self.file_label.config(text=filename)
        self.file_content_text.delete(1.0, tk.END)
        self.file_content_text.insert(tk.END, file_content)

        self.text_processor.set_content(file_content)
        self.summarizer.config(state='normal')


    def on_summarize_click(self):
        # Check if there is content in text_processor
        if not self.text_processor.get_content():
            messagebox.showerror("Error", "No content found in text_processor.")
            return

        # Generate summary using the Top-Down approach
        summary = self.text_processor.generate_summary_top_down()  # Updated method name

        # Configure the title tag for existing algorithm
        self.resultsText.tag_config("title", foreground="green", font=("Helvetica", 12, "bold"))
        self.resultsText.config(state='normal')
        self.resultsText.delete(1.0, tk.END)
        self.resultsText.insert(tk.END, f"{self.text_processor.title}\n\n", "title")  # Insert title with tag
        self.resultsText.insert(tk.END, summary)  # Insert summary without tag
        self.resultsText.config(state='disabled')

        # Prepare for new algorithm summarization
        self.new_algorithm_processor.set_content(self.text_processor.get_content())

        # Generate new algorithm summary
        new_algo_summary = self.new_algorithm_processor.generate_summary()

        # Check if new_algo_summary has a valid value
        if new_algo_summary is None or new_algo_summary == "":
            messagebox.showerror("Error", "Failed to generate summary using the new algorithm.")
            return

        # Get the title from the NewAlgorithmProcessor
        new_algo_title = self.new_algorithm_processor.get_title()

        # Display the new algorithm summary with the title
        self.newAlgoResultsText.tag_config("title", foreground="green", font=("Helvetica", 12, "bold"))
        self.newAlgoResultsText.config(state='normal')
        self.newAlgoResultsText.delete(1.0, tk.END)
        self.newAlgoResultsText.insert(tk.END, f"{new_algo_title}\n\n", "title")  # Insert file title with tag
        self.newAlgoResultsText.insert(tk.END, new_algo_summary)  # Insert new algorithm summary without tag
        self.newAlgoResultsText.config(state='disabled')





    def clear_all_data(self):
        self.file_label.config(text="File Destination")
        self.file_content_text.delete(1.0, tk.END)
        self.resultsText.config(state='normal')
        self.resultsText.delete(1.0, tk.END)
        self.resultsText.config(state='disabled')
        self.newAlgoResultsText.config(state='normal')
        self.newAlgoResultsText.delete(1.0, tk.END)
        self.newAlgoResultsText.config(state='disabled')
        self.summarizer.config(state='disabled')

        
    def make_circle(self, img):
        # Create a mask for circular cropping
        width, height = img.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=255)

        # Apply mask to the image
        img.putalpha(mask)
        return img


    def open_about_modal(self):
        about_modal = tk.Toplevel(self.parent)
        about_modal.title("About")
        about_modal.geometry("350x600")
        about_modal.configure(bg="#181818")  # Dark background color

        # Information label
        tk.Label(about_modal, text="Dynamic Approach Applied in Text Summarization", padx=10, pady=5,
                font=("Arial", 12), bg="#181818", fg="#FFFFFF").pack()

        tk.Label(about_modal, text="Contributors:", font=("Lato", 12, "bold"), padx=10, pady=10,
                bg="#181818", fg="#FFFFFF").pack()

        # Frame for holding contributor information
        contributor_frame = tk.Frame(about_modal, bg="#181818")
        contributor_frame.pack(pady=10)

        # Load images and contributor details
        contributors = [
            {"name": "Tenio, Jonald R.", "course": "Computer Science Student", "role": "Leader", "image_path": r"C:\Users\Ronan\Desktop\ts-backup-master\prof.image\tenioo.jpg"},
            {"name": "Caladiao, Jerome Z.", "course": "Computer Science Student", "role": "Documentation Paper", "image_path": r"C:\Users\Ronan\Desktop\ts-backup-master\prof.image\Caladiaoo.jpg"},
            {"name": "Baje, Ronan C.", "course": "Computer Science Student", "role": "Developer", "image_path": r"C:\Users\Ronan\Desktop\ts-backup-master\prof.image\Ronan.jpg"}
        ]

        for contributor in contributors:
            # Load and prepare the image
            img = Image.open(contributor["image_path"])
            img = img.resize((100, 100), Image.LANCZOS)  # Resize image
            img = self.make_circle(img)  # Call make_circle method
            img_tk = ImageTk.PhotoImage(img)

            # Create a frame for each contributor with a border and rounded corners
            contributor_frame_individual = tk.Frame(contributor_frame, bg="#2a2a2a", bd=2, relief="raised")
            contributor_frame_individual.pack(anchor='w', pady=7, padx=10)

            # Create a label for the image with some padding
            img_label = tk.Label(contributor_frame_individual, image=img_tk, bg="#2a2a2a", bd=0)
            img_label.image = img_tk  
            img_label.pack(side="left", padx=5, pady=5) 

            # Create a frame for the name, course, and role labels
            text_frame = tk.Frame(contributor_frame_individual, bg="#2a2a2a")
            text_frame.pack(side="left", padx=(10, 0))

            # Create and pack the name label
            name_label = tk.Label(text_frame, text=contributor['name'],
                                font=("Lato", 10), anchor="w", justify="left", bg="#2a2a2a", fg="#FFFFFF")
            name_label.pack()

            # Colorize the course title
            title_color = "#ffa38a"  
            
            # Create and pack the course label
            course_label = tk.Label(text_frame, text=contributor['course'],
                                    font=("Lato", 10), anchor="w", justify="left", bg="#2a2a2a", fg=title_color)
            course_label.pack()

            # Create and pack the role label
            role_label = tk.Label(text_frame, text=contributor['role'],
                                font=("Lato", 10, "italic"), anchor="w", justify="left", bg="#2a2a2a", fg="#FFFFFF")
            role_label.pack()

        # Thesis Advisor
        tk.Label(about_modal, text="Thesis Advisor:\nFrancis L. Atienza", font=("Lato", 10, "italic"),
                padx=10, pady=10, bg="#181818", fg="#8ad6ff").pack()





    def open_presentation_modal(self):
        # Ensure summaries are generated before presenting data
        if not self.text_processor.generated_summary or not self.new_algorithm_processor.generated_summary:
            tk.messagebox.showerror("Error", "Please generate summaries before viewing evaluation scores.")
            return

        # Set original text for evaluation
        original_text = self.text_processor.get_reference_summary()
        self.new_algorithm_processor.set_original_text(original_text)

        # Calculate word count for the original text
        original_word_count = len(original_text.split())

        loading_modal = tk.Toplevel(self.parent)
        loading_modal.title("Just a sec...")
        loading_modal.config(bg='#232323')

        loading_modal.geometry("400x150")

        screen_width = loading_modal.winfo_screenwidth()
        screen_height = loading_modal.winfo_screenheight()
        x = (screen_width // 2) - (400 // 2) 
        y = (screen_height // 2) - (150 // 2) 
        loading_modal.geometry(f"400x150+{x}+{y}")

        loading_label = tk.Label(loading_modal, text=" ", bg='#232323', fg='white')
        loading_label.pack(pady=10)

        # Progress bar
        progress_bar = ttk.Progressbar(loading_modal, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()  # Start the progress bar animation

        # Progress text label for displaying different stages of processing
        progress_text_label = tk.Label(loading_modal, text="", bg='#232323', fg='white')
        progress_text_label.pack(pady=10)

        # Start the loading animation and data calculation in a separate thread
        threading.Thread(target=self.show_presentation_data, 
                        args=(loading_modal, original_text, original_word_count, progress_bar, progress_text_label), 
                        daemon=True).start()

    def show_presentation_data(self, loading_modal, original_text, original_word_count, progress_bar, progress_text_label):
        # Update the label text with different stages of loading
        progress_text_label.config(text="Calculating scores...")
        time.sleep(1)  # Simulate processing time

        progress_text_label.config(text="Computing BERT embedding...")
        time.sleep(2)  # Simulate BERT embedding computation

        # Perform calculations for ROUGE and BERT scores
        existing_rouge = self.text_processor.get_rouge_scores()
        new_algorithm_rouge = self.new_algorithm_processor.get_rouge_scores()

        existing_summary = self.text_processor.generated_summary
        new_summary = self.new_algorithm_processor.generated_summary

        # Simulate the next step in the process
        progress_text_label.config(text="Computing greedy matching...")
        time.sleep(1)

        existing_bertscore = self.text_processor.calculate_bertscore(existing_summary, original_text)
        new_bertscore = self.new_algorithm_processor.calculate_bertscore(new_summary, original_text)

        existing_word_count = len(existing_summary.split())
        new_word_count = len(new_summary.split())

        # Simulate the final stage of computation
        progress_text_label.config(text="Finalizing...")
        time.sleep(1)

        # Close the loading modal after calculations
        loading_modal.after(100, loading_modal.destroy)

        # Stop the progress bar
        progress_bar.stop()  # Stop the progress bar animation

        # Create and show the presentation modal after loading
        self.show_presentation_modal(existing_rouge, new_algorithm_rouge, existing_bertscore, new_bertscore,
                                    original_word_count, existing_word_count, new_word_count)


    def show_presentation_modal(self, existing_rouge, new_algorithm_rouge, existing_bertscore, new_bertscore,
                                original_word_count, existing_word_count, new_word_count):
        # New window for presentation
        presentation_modal = tk.Toplevel(self.parent)
        presentation_modal.title("Presentation of Data")
        presentation_modal.geometry("600x400")
        presentation_modal.config(bg='#232323')

        # Treeview for displaying evaluation scores
        columns = ("Metric", "Existing Algorithm", "New Algorithm")
        metrics_tree = ttk.Treeview(presentation_modal, columns=columns, show='headings')

        # Center the headings
        metrics_tree.heading("Metric", text="Metric", anchor='center')
        metrics_tree.heading("Existing Algorithm", text="Existing Algorithm", anchor='center')
        metrics_tree.heading("New Algorithm", text="New Algorithm", anchor='center')

        # Center the columns' data
        metrics_tree.column("Metric", anchor='center', width=200)  # Adjust width as needed
        metrics_tree.column("Existing Algorithm", anchor='center', width=150)
        metrics_tree.column("New Algorithm", anchor='center', width=150)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(presentation_modal, orient=tk.VERTICAL, command=metrics_tree.yview)
        metrics_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insert metrics into the Treeview
        self.insert_metrics(metrics_tree, existing_rouge, new_algorithm_rouge, existing_bertscore, new_bertscore,
                            original_word_count, existing_word_count, new_word_count)

        # Configure the Treeview
        metrics_tree.pack(expand=True, fill=tk.BOTH)


    def insert_metrics(self, metrics_tree, existing_rouge, new_algorithm_rouge, existing_bertscore, new_bertscore, original_word_count, existing_word_count, new_word_count):
        # Insert ROUGE scores
        existing_rouge_l = existing_rouge[0]['rouge-l']
        new_rouge_l = new_algorithm_rouge[0]['rouge-l']

        # Existing and new summaries
        existing_summary = self.text_processor.generated_summary
        new_summary = self.new_algorithm_processor.generated_summary

        # Insert ROUGE metrics
        metrics_tree.insert("", "end", values=("Rouge L", "", ""), tags=('colored_row',))
        metrics_tree.insert("", "end", values=("ROUGE-L Precision", existing_rouge_l['p'], new_rouge_l['p']))
        metrics_tree.insert("", "end", values=("ROUGE-L Recall", existing_rouge_l['r'], new_rouge_l['r']))
        metrics_tree.insert("", "end", values=("ROUGE-L F1-Score", existing_rouge_l['f'], new_rouge_l['f']))

        # Insert BERTScore metrics with limited decimals
        metrics_tree.insert("", "end", values=("BERTScore", "", ""), tags=('colored_row',))
        metrics_tree.insert("", "end", values=("BERT Precision", f"{existing_bertscore['precision']:.2f}", f"{new_bertscore['precision']:.2f}"))
        metrics_tree.insert("", "end", values=("BERT Recall", f"{existing_bertscore['recall']:.2f}", f"{new_bertscore['recall']:.2f}"))
        metrics_tree.insert("", "end", values=("BERT F1-Score", f"{existing_bertscore['f1']:.2f}", f"{new_bertscore['f1']:.2f}"))

        # Reference-Free Score
        existing_reference_free_score = self.text_processor.calculate_reference_free_score(existing_summary)
        reference_free_score = self.new_algorithm_processor.calculate_reference_free_score(new_summary)

        # Insert Reference-Free Score
        metrics_tree.insert("", "end", values=("Reference-Free Score", f"{existing_reference_free_score:.2f}", f"{reference_free_score:.2f}"))

        # Insert Word Count for original and summarized content
        metrics_tree.insert("", "end", values=(" ", "", ""))
        metrics_tree.insert("", "end", values=("Original Content Word Count", original_word_count, original_word_count))
        metrics_tree.insert("", "end", values=("Summarized Content Word Count", existing_word_count, new_word_count))

        # Configure the tag for the colored row
        metrics_tree.tag_configure('colored_row', background='#C9E4DE')  # Change to your desired color