from enum import Enum
import customtkinter
import threading
import autoload as Autoload
import server

class Layout(Enum):
    GRID = 1
    PLACE = 2

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.font = customtkinter.CTkFont(size=14)

        self.title('TypeBubbleX AI')
        self.geometry("400x125")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        self.show_form()

        self.load_finished = True

    def show_form(self):
        self.model_entry = customtkinter.CTkEntry(self, placeholder_text="Model", font=self.font)
        self.model_entry.grid(row=0, column=0, padx=(20,70), pady=(20, 10), sticky='ew')

        self.filedialog_button = customtkinter.CTkButton(self, text="...", font=self.font, width=40, command=self.select_file)
        self.filedialog_button.grid(row=0, column=0, padx=20, pady=(20, 10), sticky='e')

        self.confirm_button = customtkinter.CTkButton(self, text="Confirm", font=self.font, command=self.confirm)
        self.confirm_button.grid(row=1, column=0, padx=20, pady=(0, 10), sticky='ew')

    def select_file(self):
        filetypes = (
            ('Model pytorch', '*.pt'),
            ('All files', '*.*')
        )

        filename = customtkinter.filedialog.askopenfilename(
            title='Open a file',
            filetypes=filetypes)

        self.model_entry.delete(0, 'end')
        self.model_entry.insert(0, filename)

    def confirm(self):
        try:
            self.hide([self.model_entry, self.filedialog_button, self.confirm_button], Layout.GRID)
            self.load()

            self.server = server.Server(self.model_entry.get())

            t = threading.Thread(target=self.server.run, daemon=True)
            t.start()
        except Exception as error:
            print(error)

    def hide(self, widgets : list, layout : Layout):
        for widget in widgets:
            if layout == Layout.GRID:
                widget.grid_remove()
            elif layout == Layout.PLACE:
                widget.place_forget()

    def load(self):
        Autoload.load_finished = False
        self.progressbar = customtkinter.CTkProgressBar(self, orientation="horizontal")

        self.progressbar.configure(mode="indeterminate")
        self.progressbar.start()
        self.progressbar.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        self.loading()

    def loading(self):
        if Autoload.load_finished:
            self.hide([self.progressbar], Layout.PLACE)
            self.progressbar.stop()
            self.show_message()
            return
        self.after(100, self.loading)

    def show_message(self):
        label = customtkinter.CTkLabel(self, text="Server open, you can upload the chapter\non TypeBubbleX and don't close this app, only close it\nwhen you close the TypeBubbleX application", fg_color="transparent", font=self.font)
        label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

app = App()
app.mainloop()
