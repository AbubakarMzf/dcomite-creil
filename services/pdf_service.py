"""
Service de generation de PDF
Genere automatiquement des rapports PDF lors des enregistrements
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import PDF_OUTPUT_DIR, POSTES_DEPENSES, CURRENCY_SYMBOL, ADMIN_IDS


class PdfService:
    """Service pour la generation de PDF"""

    @staticmethod
    def _formater_montant(montant):
        """Formate un montant avec separateurs et devise"""
        return f"{montant:,.2f} {CURRENCY_SYMBOL}".replace(',', ' ')

    @staticmethod
    def _formater_date(date_str):
        """Convertit YYYY-MM-DD en DD/MM/YYYY"""
        if not date_str:
            return ''
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            return date_str

    @staticmethod
    def _date_pour_fichier(date_str):
        """Convertit YYYY-MM-DD en DD-MM-YYYY pour nom de fichier"""
        if not date_str:
            return 'sans-date'
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except ValueError:
            return date_str.replace('/', '-')

    @staticmethod
    def _chemin_unique(chemin):
        """Retourne un chemin unique en ajoutant un suffixe si le fichier existe"""
        if not os.path.exists(chemin):
            return chemin

        base, ext = os.path.splitext(chemin)
        compteur = 2
        while os.path.exists(f"{base}_{compteur}{ext}"):
            compteur += 1
        return f"{base}_{compteur}{ext}"

    @staticmethod
    def _get_styles():
        """Retourne les styles pour le PDF"""
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name='TitrePrincipal',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            name='SousTitre',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            name='Info',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=2,
            spaceAfter=2
        ))

        styles.add(ParagraphStyle(
            name='PiedPage',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        ))

        return styles

    @staticmethod
    def generer_pdf_depense(depense):
        """
        Genere un PDF pour une depense (deces)

        Args:
            depense: Instance de Depense

        Returns:
            Chemin du fichier PDF genere
        """
        # Creer le dossier
        dossier = os.path.join(PDF_OUTPUT_DIR, 'depenses')
        os.makedirs(dossier, exist_ok=True)

        # Nom du fichier
        date_fichier = PdfService._date_pour_fichier(depense.date_deces)
        nom_fichier = f"depense_{date_fichier}.pdf"
        chemin = PdfService._chemin_unique(os.path.join(dossier, nom_fichier))

        # Recuperer les infos
        adherent = depense.get_adherent()
        nom_defunt = depense.get_nom_defunt()

        # Creer le document
        doc = SimpleDocTemplate(
            chemin,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        styles = PdfService._get_styles()
        elements = []

        # Titre
        elements.append(Paragraph("Rapport de depense - Deces", styles['TitrePrincipal']))
        elements.append(Paragraph(
            f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
            styles['PiedPage']
        ))
        elements.append(Spacer(1, 0.5 * cm))

        # Section 1 : Informations sur le deces
        elements.append(Paragraph("Informations sur le deces", styles['SousTitre']))

        infos_deces = [
            ["Defunt", nom_defunt],
        ]

        if adherent:
            nom_adherent = adherent.get_nom_complet()
            if depense.defunt_est_adherent:
                infos_deces.append(["Adherent (decede)", nom_adherent])
            else:
                infos_deces.append(["Adherent lie", nom_adherent])

        if not depense.defunt_est_adherent and depense.defunt_relation:
            infos_deces.append(["Relation", depense.defunt_relation])

        infos_deces.append(["Date du deces", PdfService._formater_date(depense.date_deces)])

        if depense.pays_destination:
            infos_deces.append(["Pays de destination", depense.pays_destination])

        table_infos = Table(infos_deces, colWidths=[5 * cm, 10 * cm])
        table_infos.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(table_infos)
        elements.append(Spacer(1, 0.5 * cm))

        # Section 2 : Detail des frais
        elements.append(Paragraph("Detail des frais", styles['SousTitre']))

        # Entete du tableau
        donnees_frais = [["Poste", "Montant"]]

        for key, label in POSTES_DEPENSES.items():
            montant = getattr(depense, key, 0) or 0
            donnees_frais.append([label, PdfService._formater_montant(montant)])

        # Ligne total
        donnees_frais.append(["TOTAL", PdfService._formater_montant(depense.montant)])

        table_frais = Table(donnees_frais, colWidths=[8 * cm, 7 * cm])
        table_frais.setStyle(TableStyle([
            # Entete
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            # Corps
            ('FONTNAME', (0, 1), (0, -2), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            # Lignes alternees
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F2F3F4'))
              for i in range(2, len(donnees_frais) - 1, 2)],
            # Ligne total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            # Bordures
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ]))
        elements.append(table_frais)

        # Notes
        if depense.notes:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(Paragraph("Notes", styles['SousTitre']))
            elements.append(Paragraph(depense.notes, styles['Info']))

        # Generer le PDF
        doc.build(elements)

        return chemin

    @staticmethod
    def generer_pdf_paiement(contribution):
        """
        Genere un PDF pour un paiement (contribution)

        Args:
            contribution: Instance de Contribution

        Returns:
            Chemin du fichier PDF genere
        """
        # Recuperer l'adherent
        adherent = contribution.get_adherent()

        # Creer le sous-dossier par adherent
        nom_dossier = f"{adherent.id}_{adherent.nom}_{adherent.prenom}"
        dossier = os.path.join(PDF_OUTPUT_DIR, 'paiements', nom_dossier)
        os.makedirs(dossier, exist_ok=True)

        # Nom du fichier avec la date du jour
        date_jour = datetime.now().strftime('%d-%m-%Y')
        nom_fichier = f"paiement_{date_jour}.pdf"
        chemin = PdfService._chemin_unique(os.path.join(dossier, nom_fichier))

        # Creer le document
        doc = SimpleDocTemplate(
            chemin,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        styles = PdfService._get_styles()
        elements = []

        # Titre
        elements.append(Paragraph("Recu de paiement", styles['TitrePrincipal']))
        elements.append(Paragraph(
            f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
            styles['PiedPage']
        ))
        elements.append(Spacer(1, 0.5 * cm))

        # Section : Informations adherent
        elements.append(Paragraph("Informations adherent", styles['SousTitre']))

        infos_adherent = [
            ["Adherent", adherent.get_nom_complet()],
            ["ID", str(adherent.id)],
        ]

        if adherent.telephone:
            infos_adherent.append(["Telephone", adherent.telephone])

        table_adherent = Table(infos_adherent, colWidths=[5 * cm, 10 * cm])
        table_adherent.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(table_adherent)
        elements.append(Spacer(1, 0.5 * cm))

        # Section : Details du paiement
        elements.append(Paragraph("Details du paiement", styles['SousTitre']))

        # Nom de l'admin
        admin_nom = ADMIN_IDS.get(contribution.admin_id, f"Admin {contribution.admin_id}")

        infos_paiement = [
            ["Montant", PdfService._formater_montant(contribution.montant)],
            ["Date du paiement", PdfService._formater_date(contribution.date_paiement)],
            ["Mode de paiement", contribution.mode_paiement or '-'],
            ["Enregistre par", admin_nom],
        ]

        if contribution.reference_paiement:
            infos_paiement.insert(3, ["Reference", contribution.reference_paiement])

        table_paiement = Table(infos_paiement, colWidths=[5 * cm, 10 * cm])
        table_paiement.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            # Mettre le montant en gras
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
        ]))
        elements.append(table_paiement)

        # Notes
        if contribution.notes:
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(Paragraph("Notes", styles['SousTitre']))
            elements.append(Paragraph(contribution.notes, styles['Info']))

        # Generer le PDF
        doc.build(elements)

        return chemin
