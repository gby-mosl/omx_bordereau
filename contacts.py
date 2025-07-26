import json
import os
import ttkbootstrap as ttk
import re
from tkinter import messagebox

FICHIER_JSON = "contacts.json"


def load_data():
    try:
        if os.path.exists(FICHIER_JSON):
            with open(FICHIER_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
    except FileNotFoundError:
        return {"entreprises": []}


def save_data(data):
    with open(FICHIER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class ContactsApp:
    def __init__(self, root):
        self.root = root
        self.data = load_data()
        self.selection_index = None
        self.setup_ui()
        self.refresh_list()
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("yeti")
        style.configure("Treeview", font=("Segoe UI", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.configure("Custom.Treeview", rowheight=28)

        # Fenêtre gauche : "Treeview" des entreprises et contacts
        self.left_frame = ttk.Frame(self.root, padding=10)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.left_frame, columns="info", show="tree")
        self.tree.configure(style="Custom.Treeview")
        self.tree.tag_configure("entreprise", font=("Segoe UI", 11, "bold"), foreground="#158cba")
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Fenêtre droite : Formulaires
        self.right_frame = ttk.Frame(self.root, padding=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Formulaire "Entreprise"
        self.company_form_frame = ttk.LabelFrame(self.right_frame, text="Entreprise", padding=10)
        self.company_form_frame.pack(fill="x", padx=10, pady=(0, 10))

        company_labels = ["Nom", "Rue", "CP", "Ville", "Pays"]
        self.company_entries = []

        self.company_form_frame.columnconfigure(1, weight=1)

        for i, label in enumerate(company_labels):
            ttk.Label(self.company_form_frame, text=label).grid(row=i, column=0, sticky="e", padx=(5, 10), pady=5)
            entry = ttk.Entry(self.company_form_frame, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.company_entries.append(entry)

        self.c_name_entry, self.c_street_entry, self.c_zip_entry, self.c_city_entry, self.c_country_entry = self.company_entries

        self.company_action_button = ttk.Button(
            self.company_form_frame,
            text="Ajouter",
            command=self.add_update_company
        )
        self.company_action_button.grid(row=len(company_labels), column=1, sticky="e", pady=10)

        # Formulaire "Contact"
        self.employee_form_frame = ttk.LabelFrame(self.right_frame, text="Contact", padding=10)
        self.employee_form_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.employee_entries = []  # Liste pour stocker les champs de saisie des employés

        # Création des champs pour les employés
        employee_labels = ["Nom", "Prénom", "Email"]
        for i, label in enumerate(employee_labels):
            ttk.Label(self.employee_form_frame, text=label).grid(row=i, column=0, sticky="e", padx=(5, 10), pady=5)
            entry = ttk.Entry(self.employee_form_frame, width=40, state="disabled")  # Désactivé par défaut
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            self.employee_entries.append(entry)

        # Ajouter la validation de l'email sur le champ email
        self.employee_entries[2].bind('<KeyRelease>', self.validate_email)  # Index 2 est le champ email

        # Ajouter un label pour afficher le message d'erreur
        self.email_error_label = ttk.Label(
            self.employee_form_frame,
            text="",
            foreground="red",
            font=("Segoe UI", 9)
        )
        self.email_error_label.grid(row=3, column=1, sticky="w", padx=5)

        # Création du bouton Ajouter pour les employés
        self.employee_action_button = ttk.Button(
            self.employee_form_frame,
            text="Ajouter",
            command=self.add_employee,
            state="disabled"  # Désactivé par défaut
        )
        self.employee_action_button.grid(row=len(employee_labels), column=1, sticky="e", pady=10)

        # Ajouter une validation sur les champs entreprise
        for entry in self.company_entries:
            entry.bind('<KeyRelease>', self.validate_company_form)

    def validate_company_form(self, event=None):
        """Vérifie si tous les champs entreprise sont remplis"""
        # Vérifie si une entreprise est sélectionnée
        has_selection = self.selection_index is not None

        # Vérifie si tous les champs sont remplis
        fields_filled = all(entry.get().strip() for entry in self.company_entries)

        # Active/désactive les champs employés et le bouton
        state = "normal" if has_selection and fields_filled else "disabled"

        # Met à jour l'état des champs employés
        for entry in self.employee_entries:
            entry.configure(state=state)

        # Met à jour l'état du bouton
        self.employee_action_button.configure(state=state)

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())

        sorted_companies = sorted(self.data["entreprises"], key=lambda c: c["nom"].upper())

        for company in sorted_companies:
            item = self.tree.insert("", "end", text=company["nom"], tags=("entreprise",))
            sorted_employees = sorted(company["personnel"], key=lambda e: e["nom"].upper())
            for employee in sorted_employees:
                self.tree.insert(item, "end", text=(f'👤 {employee["nom"].upper()} {employee["prenom"]}'))

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            self.clear_company_form()
            self.validate_company_form()  # Désactive les champs employés
            return

        item = selection[0]
        parent_item = self.tree.parent(item)

        if not parent_item:  # C'est une entreprise
            # Recherche l'entreprise sélectionnée dans les données
            company_name = self.tree.item(item)['text']
            selected_company = next(
                (company for company in self.data["entreprises"]
                 if company["nom"] == company_name),
                None
            )

            if selected_company:
                self.fill_company_form(selected_company)
                # Vider les champs employé
                for entry in self.employee_entries:
                    entry.delete(0, 'end')
                self.employee_action_button.configure(text="Ajouter")

        else:  # C'est un employé
            # Récupérer le nom de l'entreprise parente
            company_name = self.tree.item(parent_item)['text']
            selected_company = next(
                (company for company in self.data["entreprises"]
                 if company["nom"] == company_name),
                None
            )

            if selected_company:
                # Remplir le formulaire entreprise avec les infos de l'entreprise parente
                self.fill_company_form(selected_company)

                # Récupérer les informations de l'employé
                employee_text = self.tree.item(item)['text']
                # Enlever l'emoji et les espaces au début
                employee_text = employee_text.replace('👤 ', '')
                # Séparer le nom et le prénom
                last_name, first_name = employee_text.split(' ', 1)
                last_name = last_name.strip()

                # Rechercher l'employé dans la liste du personnel
                selected_employee = next(
                    (employee for employee in selected_company["personnel"]
                     if employee["nom"].upper() == last_name and employee["prenom"] == first_name),
                    None
                )

                if selected_employee:
                    # Remplir les champs employé
                    self.employee_entries[0].delete(0, 'end')  # Prénom
                    self.employee_entries[0].insert(0, selected_employee["nom"])

                    self.employee_entries[1].delete(0, 'end')  # Nom
                    self.employee_entries[1].insert(0, selected_employee["prenom"])

                    self.employee_entries[2].delete(0, 'end')  # Email
                    self.employee_entries[2].insert(0, selected_employee["email"])

                    # Changer le texte du bouton employé
                    self.employee_action_button.configure(text="Modifier")

        # Valider le formulaire pour activer/désactiver les champs employé
        self.validate_company_form()

    def fill_company_form(self, company):
        """Remplit le formulaire entreprise avec les données fournies"""
        self.c_name_entry.delete(0, 'end')
        self.c_name_entry.insert(0, company.get("nom", ""))

        adresse = company.get("adresse", {})

        self.c_street_entry.delete(0, 'end')
        self.c_street_entry.insert(0, adresse.get("rue", ""))

        self.c_zip_entry.delete(0, 'end')
        self.c_zip_entry.insert(0, adresse.get("code_postal", ""))

        self.c_city_entry.delete(0, 'end')
        self.c_city_entry.insert(0, adresse.get("ville", ""))

        self.c_country_entry.delete(0, 'end')
        self.c_country_entry.insert(0, adresse.get("pays", ""))

        # Changer le texte du bouton pour indiquer une modification
        self.company_action_button.configure(text="Modifier")

        # Stocker l'index de l'entreprise sélectionnée
        self.selection_index = next(
            (index for index, c in enumerate(self.data["entreprises"])
             if c["nom"] == company["nom"]),
            None
        )

    def add_update_company(self):
        # Récupérer les valeurs des champs
        new_company = {
            "nom": self.c_name_entry.get(),
            "adresse": {
                "rue": self.c_street_entry.get(),
                "ville": self.c_city_entry.get(),
                "code_postal": self.c_zip_entry.get(),
                "pays": self.c_country_entry.get()
            },
            "personnel": []
        }

        if self.selection_index is not None:
            # Mode modification
            # Préserver la liste du personnel existant
            new_company["personnel"] = self.data["entreprises"][self.selection_index]["personnel"]
            self.data["entreprises"][self.selection_index] = new_company
        else:
            # Mode ajout
            new_company["personnel"] = []  # Initialiser une liste vide pour le personnel
            self.data["entreprises"].append(new_company)

        # Sauvegarder les données
        save_data(self.data)

        # Rafraîchir l'affichage
        self.refresh_list()

        # Réinitialiser le formulaire
        self.clear_company_form()

    def clear_company_form(self):
        """Réinitialise le formulaire entreprise"""
        for entry in self.company_entries:
            entry.delete(0, 'end')
        self.company_action_button.configure(text="Ajouter")
        self.selection_index = None

        # Désactive les champs employés
        self.validate_company_form()

    def validate_email(self, event=None):
        """Valide le format de l'email"""
        email = self.employee_entries[2].get().strip()

        if not email:  # Si le champ est vide
            self.email_error_label.configure(text="")
            self.employee_action_button.configure(state="normal")
            return

        if self.email_pattern.match(email):
            self.email_error_label.configure(text="✓ Format d'email valide", foreground="green")
            self.employee_action_button.configure(state="normal")
        else:
            self.email_error_label.configure(text="⚠ Format d'email invalide", foreground="red")
            self.employee_action_button.configure(state="disabled")

    def add_employee(self):
        """Ajoute ou met à jour un employé"""
        if self.selection_index is None:
            return

        # Valider l'email avant d'ajouter/modifier
        email = self.employee_entries[2].get().strip()
        if not self.email_pattern.match(email):
            return  # Ne pas procéder si l'email est invalide

        # Récupérer les valeurs des champs
        new_employee = {
            "nom": self.employee_entries[0].get().strip(),
            "prenom": self.employee_entries[1].get().strip(),
            "email": self.employee_entries[2].get().strip()
        }

        # Vérifier si c'est une modification (si le bouton affiche "Modifier")
        if self.employee_action_button.cget("text") == "Modifier":
            # Rechercher l'employé existant
            personnel = self.data["entreprises"][self.selection_index]["personnel"]
            employee_index = next(
                (index for index, employee in enumerate(personnel)
                 if employee["nom"] == new_employee["nom"] and
                 employee["prenom"] == new_employee["prenom"]),
                None
            )
            if employee_index is not None:
                # Mettre à jour l'employé existant
                self.data["entreprises"][self.selection_index]["personnel"][employee_index] = new_employee
        else:
            # Ajouter le nouvel employé
            self.data["entreprises"][self.selection_index]["personnel"].append(new_employee)

        # Sauvegarder les données
        save_data(self.data)

        # Rafraîchir l'affichage
        self.refresh_list()

        # Vider les champs employé et réinitialiser le bouton
        for entry in self.employee_entries:
            entry.delete(0, 'end')
        self.employee_action_button.configure(text="Ajouter")


if __name__ == "__main__":
    app = ttk.Window(title="Gestion des contacts", size=(1000, 550), resizable=(False, False))
    app.iconbitmap("omexom.ico")
    ContactsApp(app)
    app.mainloop()