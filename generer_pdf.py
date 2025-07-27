import locale
from contextlib import contextmanager
from fpdf import FPDF

# Constants
LOCALE_SETTINGS = 'fr_FR.UTF-8'

# Colors
BLUE_COLOR = (43, 113, 184)
LIGHT_BLUE_COLOR = (0, 191, 220)
YELLOW_COLOR = (252, 181, 32)
GRAY_BACKGROUND = (240, 240, 240)

class PDFDocument(FPDF):
    """Classe pour la génération de documents PDF personnalisés."""

    def footer(self):
        """Ajoute un pied de page personnalisé avec des lignes colorées et numérotation."""
        self.set_y(-15)
        self._draw_footer_lines()
        self._add_page_number()

    def _draw_footer_lines(self):
        """Dessine les lignes colorées dans le pied de page."""
        pos_y = 280
        line_segments = [
            (0, 120, BLUE_COLOR),
            (120, 180, LIGHT_BLUE_COLOR),
            (180, 210, YELLOW_COLOR)
        ]
        self.set_line_width(1)
        for start, end, color in line_segments:
            self.set_draw_color(*color)
            self.line(x1=start, y1=pos_y, x2=end, y2=pos_y)

    def _add_page_number(self):
        """Ajoute la numérotation des pages au pied de page."""
        self.set_font('helvetica', 'I', 11)
        self.cell(0, 10, f"Page {self.page_no()} sur {{nb}}", align="C")

class DispatchDocument:
    def __init__(self, form_data):
        self.form_data = form_data

    @contextmanager
    def _pdf_context(self):
        """Gestionnaire de contexte pour les ressources PDF."""
        pdf = None
        try:
            pdf = self._create_pdf_document()
            yield pdf
        finally:
            if pdf:
                del pdf

    def _create_pdf_document(self):
        pdf = PDFDocument(orientation='P', format='A4', unit='mm')
        pdf.add_page()
        pdf.set_font("helvetica", style="B", size=16)
        pdf.cell(40, 10, f"Classement : {self.form_data['rank']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Projet : {self.form_data['project']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Numéro d'affaire : {self.form_data['number']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Date : {self.form_data['date']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"ID : {self.form_data['id']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Titre : {self.form_data['title']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Expéditeur :  : {self.form_data['sender']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Destinataire : {self.form_data['receiver']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Entreprise : {self.form_data['company']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Nombre de fichiers : {self.form_data['files_quantity']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Message : {self.form_data['message']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Statut : {self.form_data['status']}")
        pdf.ln(10)
        pdf.cell(40, 10, f"Transmission : {self.form_data['transmission_modes']}")
        return pdf

    def generate_pdf(self):
        with self._pdf_context() as pdf:
            pdf.output('test.pdf')

if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, LOCALE_SETTINGS)
    document = DispatchDocument()
    document.generate_pdf()