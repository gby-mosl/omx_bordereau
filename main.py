from dataclasses import dataclass
import ttkbootstrap as ttk
from contacts import ContactsApp
import openpyxl
import re


@dataclass
class InformationExcelCells:
    INFO_WORKSHEET: str = 'Page de garde'
    PROJECT: str = 'B3'
    SENDING_INFO: str = 'C8'
    DATE: str = 'C5'
    ID: str = 'C7'
    SENDER: str = 'C6'
    MESSAGE: str = 'C11'
    FILES_QUANTITY: str = 'C9'


@dataclass
class filesExcelCells:
    FILES_WORKSHEET: str = 'Fichiers'


class ExcelDocument:
    XLSX_EXTENSION = '.xlsx'
    STATUS = {
        "BPE": "Bon pour exécution",
        "BPO": "Bon pour observation",
        "APPRO": "Pour approbation",
        "INF": "Pour information",
        "V1": "Dossier V1",
        "V2": "Dossier V2",
        "CAE": "Conforme à exécution"
    }
    PROJECT_PATTERN = r"^(?P<rank>[^-]+)-(?P<project>.+)-(?P<number>[^-]+)$"
    SENDING_INFO_PATTERN = r"@(?P<receiver>.+?)\s+\((?P<company>.+?)\)\s+#(?P<title>.+)"


class dispatchApp:
    def __init__(self, root):
        self.root = root
        self.create_menu()
        self.root.title("Création bordereau d'envoi")
        self.root.geometry("700x950")
        self.root.resizable(False, False)
        self.info_excel_cells = InformationExcelCells()
        self.files_excel_cells = filesExcelCells()
        self.setup_ui()

    def create_menu(self):
        menubar = ttk.Menu(self.root)
        # Menu "Fichier"
        file_menu = ttk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Gestion du carnet d'adresse", command=self.open_contacts_app)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)

        self.root.config(menu=menubar)

    def open_contacts_app(self):
        # Ouvre une nouvelle fenêtre pour les contacts
        contact_window = ttk.Toplevel(self.root)
        ContactsApp(contact_window)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("yeti")

        # Frame principale - réduire le padding général
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Sélection du fichier
        file_section = ttk.LabelFrame(main_frame, text="Séléction du fichier", padding="10")  # Réduit de 20 à 10
        file_section.pack(fill="x", padx=5, pady=(0, 10))  # Réduit padx de 10 à 5 et pady de 20 à 10

        self.search_var = ttk.StringVar()
        self.search_entry = ttk.Entry(
            file_section,
            textvariable=self.search_var,
            width=65
        )
        self.search_entry.pack(side="left", padx=(0, 10))

        self.browse_button = ttk.Button(
            file_section,
            text="...",
            command=self.browse_file,
            width=15
        )
        self.browse_button.pack(side="left")

        # Section formulaire
        form_section = ttk.LabelFrame(main_frame, text="Informations du document", padding="10")  # Réduit de 20 à 10
        form_section.pack(fill="both", expand=True, padx=10)  # Réduit padx de 10 à 5

        # Extraction des informations du projet
        # match = re.match(ExcelDocument.PROJECT_PATTERN, InformationExcelCells.PROJECT)
        # result = match.groupdict()
        # if match:
        #     rank = result['rank']
        #     project = result['project']
        #     number = result['number']

        # Variables pour les champs du formulaire
        self.form_vars = {
            'rank': ttk.StringVar(),
            'project': ttk.StringVar(),
            'number': ttk.StringVar(),
            'date': ttk.StringVar(),
            'id': ttk.StringVar(),
            'title': ttk.StringVar(),
            'sender': ttk.StringVar(),
            'receiver': ttk.StringVar(),
            'company': ttk.StringVar(),
            'message': ttk.StringVar(),
            'files_quantity': ttk.StringVar(),
            'status': ttk.StringVar(),
            'response_delay': ttk.StringVar()
        }

        # Grille pour le formulaire
        form_grid = ttk.Frame(form_section)
        form_grid.grid(row=0, column=0, sticky="nsew")

        # Configuration des poids des colonnes pour permettre l'expansion
        form_section.grid_columnconfigure(0, weight=1)
        form_grid.grid_columnconfigure(1, weight=1)

        # Création des champs du formulaire
        labels = {
            'rank': 'Classement :',
            'project': 'Projet :',
            'number': 'N° d\'Affaire :',
            'date': 'Date :',
            'id': 'N° de bordereau :',
            'title': 'Titre du bordereau :',
            'sender': 'Expéditeur :',
            'receiver': 'Destinataire :',
            'company': 'Entreprise :',
            'files_quantity': 'Nombre de fichiers :',
            'message': 'Message :',
        }

        # Création des champs - réduire l'espacement entre les champs
        for row, (key, label) in enumerate(labels.items()):
            form_grid.grid_rowconfigure(row, weight=1)
            ttk.Label(form_grid, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=5)
            if key == 'message':
                entry = ttk.Text(form_grid, height=3, width=80)
                entry.grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
                self.message_widget = entry
            else:
                entry = ttk.Entry(form_grid, textvariable=self.form_vars.get(key), width=80)
                entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        # Section statut
        status_section = ttk.LabelFrame(main_frame, text="Type de diffusion", padding="10")
        status_section.pack(fill="x", padx=5, pady=10)

        status_container = ttk.Frame(status_section)
        status_container.pack(fill="x", expand=True)

        # Définir combien de boutons par ligne
        buttons_per_row = 3

        # Création des boutons radio
        for i, (status_key, status_text) in enumerate(ExcelDocument.STATUS.items()):
            row = i // buttons_per_row
            col = i % buttons_per_row
            ttk.Radiobutton(
                status_container,
                text=status_text,
                value=status_key,
                variable=self.form_vars['status'],
                style='TRadiobutton'
            ).grid(row=row, column=col, padx=5, pady=5, sticky="w")

            # Configure le poids des colonnes pour une distribution uniforme
            status_container.grid_columnconfigure(col, weight=1)

        # Conteneur délai
        delay_container = ttk.Frame(status_section)
        delay_container.pack(fill="x", expand=True, pady=(10, 0))

        # Ajout du label et du champ de saisie pour le délai
        self.delay_label = ttk.Label(
            delay_container,
            text="Délai de réponse (jours) :",
            foreground="gray"
        )
        self.delay_label.pack(side="left", padx=(0, 10))

        self.delay_entry = ttk.Entry(
            delay_container,
            textvariable=self.form_vars['response_delay'],
            width=10,
            state="disabled"
        )
        self.delay_entry.pack(side="left")

        # Fonction pour gérer l'état du champ délai
        def on_status_change(*args):
            selected_status = self.form_vars['status'].get()
            if selected_status in ["BPO", "APPRO"]:
                self.delay_entry.configure(state="normal")
                self.delay_label.configure(foreground="black")
                if not self.form_vars['response_delay'].get():
                    self.form_vars['response_delay'].set("15")
                # Mettre le focus sur le champ après un court délai pour assurer que l'interface est mise à jour
                self.root.after(100, lambda: self.delay_entry.focus_set())

            else:
                self.delay_entry.configure(state="disabled")
                self.delay_label.configure(foreground="gray")
                self.form_vars['response_delay'].set("")  # Efface le contenu quand désactivé

        # Surveillance des changements de statut
        self.form_vars['status'].trace_add('write', on_status_change)

        # Section mode de transmission - réduire le padding et l'espacement
        means_section = ttk.LabelFrame(main_frame, text="Modes de transmission", padding="10")
        means_section.pack(fill="x", padx=5, pady=10)

        means_container = ttk.Frame(means_section)
        means_container.pack(fill="x", expand=True)

        # Ajout des variables pour les checkbox
        self.form_vars.update({
            'mail': ttk.BooleanVar(),
            'transfer': ttk.BooleanVar(),
            'courier': ttk.BooleanVar()
        })

        # Checkbox
        ttk.Checkbutton(
            means_container,
            text="Mail",
            variable=self.form_vars['mail']
        ).pack(side="left", padx=10)

        ttk.Checkbutton(
            means_container,
            text="Transfer Vinci",
            variable=self.form_vars['transfer']
        ).pack(side="left", padx=10)

        ttk.Checkbutton(
            means_container,
            text="Courier",
            variable=self.form_vars['courier']
        ).pack(side="left", padx=10)

        # Conteneur pour le bouton Générer PDF
        button_container = ttk.Frame(main_frame)
        button_container.pack(side="bottom", fill="x", padx=5, pady=10)

        # Bouton Générer PDF
        generate_button = ttk.Button(
            button_container,
            text="Générer le PDF",
            command=self.generate_pdf,
            style="primary",
            width=20
        )
        generate_button.pack(side="right")

    def browse_file(self):
        pass

    def generate_pdf(self):
        pass


if __name__ == "__main__":
    app = ttk.Window()
    dispatchApp(app)
    app.mainloop()