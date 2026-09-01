#!/usr/bin/env python3
"""Genere guide-decouverte.pdf (le lead magnet servi par guide.html).

Pourquoi ce script existe : le PDF a ete produit une fois a la main le 07/08/2026,
sans source. Quand l'offre fondateur a 79 EUR a ete abandonnee le 17/08 et la date
d'ouverture fixee au 30 novembre 2026, index.html a ete corrige mais le PDF est
reste en production avec l'ancienne offre — invisible a tout grep sur le HTML.
Le contenu vit desormais ici, en clair, et se regenere par :

    python3 outils/build-guide-decouverte.py             -> guide-decouverte.pdf
    python3 outils/build-guide-decouverte.py --diffusion -> guide-decouverte-diffusion.pdf

La variante --diffusion omet l'encadre commercial final (« Aller plus loin ») :
c'est la version remise aux services publics (ISTF/UDAF) pour qu'ils puissent la
diffuser aux familles sans paraitre recommander un produit payant. Tout le reste
est identique.

Identite visuelle : BRAND.md (« notaire moderne ») et les infographies deja
publiees — bandeau marine, wordmark Mon/CRG or/.fr, cartes bordées, accents or.
Serif : Liberation Serif si presente (esprit Georgia), sinon Times. Le lectorat a
50-75 ans : gros corps, fort contraste, reperes visuels simples, jamais d'emoji.

Toute modification de prix, de date ou d'offre doit passer par ce fichier.
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame,
                                KeepTogether, NextPageTemplate, PageTemplate,
                                Paragraph, Spacer)

DIFFUSION = "--diffusion" in sys.argv
SORTIE = "guide-decouverte-diffusion.pdf" if DIFFUSION else "guide-decouverte.pdf"
TITRE = "Le compte de gestion 2024 : ce qui a changé, ce qu’on attend de vous"

# --- Charte (BRAND.md) -------------------------------------------------------
MARINE = colors.HexColor("#1d3a5f")
MARINE_F = colors.HexColor("#142c4a")
BLEU_CLair = colors.HexColor("#f0f5fb")
OR = colors.HexColor("#b8860b")
OR_CLAIR = colors.HexColor("#e8c469")
VERT = colors.HexColor("#2a6b2e")
TEXTE = colors.HexColor("#26303b")
GRIS = colors.HexColor("#5b6a7a")
BORD = colors.HexColor("#dfe8f2")
BLANC = colors.white

# --- Polices : Liberation Serif si disponible, sinon Times -------------------
_LIB = "/usr/share/fonts/truetype/liberation"
try:
    pdfmetrics.registerFont(TTFont("Serif", os.path.join(_LIB, "LiberationSerif-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Serif-Bold", os.path.join(_LIB, "LiberationSerif-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Serif-Italic", os.path.join(_LIB, "LiberationSerif-Italic.ttf")))
    pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold", italic="Serif-Italic")
    SERIF, SERIF_B, SERIF_I = "Serif", "Serif-Bold", "Serif-Italic"
except Exception:
    SERIF, SERIF_B, SERIF_I = "Times-Roman", "Times-Bold", "Times-Italic"
SANS, SANS_B = "Helvetica", "Helvetica-Bold"

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo", "moncrg-monogramme.png")

MARGE = 17 * mm
LARGEUR = A4[0] - 2 * MARGE


def style(nom, **kw):
    base = dict(fontName=SERIF, fontSize=10.5, leading=15,
                textColor=TEXTE, spaceAfter=7)
    base.update(kw)
    return ParagraphStyle(nom, **base)


S = {
    "titre1": style("titre1", fontName=SERIF_B, fontSize=20, leading=25,
                    textColor=MARINE, spaceBefore=2, spaceAfter=0),
    "titre2": style("titre2", fontName=SERIF_B, fontSize=20, leading=25,
                    textColor=OR, spaceAfter=8),
    "avert": style("avert", fontName=SERIF_I, fontSize=9, leading=12.5,
                   textColor=GRIS, spaceAfter=12),
    "h2": style("h2", fontName=SERIF_B, fontSize=14, leading=18,
                textColor=MARINE, spaceBefore=13, spaceAfter=6),
    "p": style("p", alignment=TA_JUSTIFY),
    "note": style("note", fontName=SERIF_I, fontSize=9.5, leading=13, textColor=GRIS,
                  spaceBefore=2, spaceAfter=8),
    "legal": style("legal", fontName=SANS, fontSize=7.2, leading=9.8,
                   textColor=GRIS, spaceBefore=12),
}


def typo(t):
    """Finition typographique francaise, apres coup pour garder les sources lisibles."""
    t = t.replace(" - ", " — ")
    t = t.replace("'", "’")
    t = t.replace("oeil", "œil")
    t = t.replace(" :", " :")
    t = t.replace("  :", " :")
    return t


def decoupe(texte, police, corps, largeur):
    """Coupe un texte simple (sans balises) en lignes tenant dans `largeur`."""
    lignes, cour = [], ""
    for mot in texte.split():
        essai = (cour + " " + mot).strip()
        if stringWidth(essai, police, corps) <= largeur:
            cour = essai
        else:
            if cour:
                lignes.append(cour)
            cour = mot
    if cour:
        lignes.append(cour)
    return lignes


def petites_caps(canv, x, y, texte, corps=8.2, couleur=OR, interlettre=1.1):
    """Etiquette en capitales espacees, or — le code visuel des infographies."""
    canv.setFont(SANS_B, corps)
    canv.setFillColor(couleur)
    cx = x
    for ch in texte.upper():
        canv.drawString(cx, y, ch)
        cx += stringWidth(ch, SANS_B, corps) + interlettre
    return cx


def carte(canv, x, y, l, h, fond=BLANC, bord=MARINE, epaisseur=1.1, rayon=2.6 * mm):
    canv.setFillColor(fond)
    canv.setStrokeColor(bord)
    canv.setLineWidth(epaisseur)
    canv.roundRect(x, y, l, h, rayon, stroke=1, fill=1)


class SchemaQuiVerifie(Flowable):
    """Avant / Desormais / Sinon — la meme grammaire que l'infographie publiee."""

    H = 62 * mm

    def wrap(self, aw, ah):
        self.l = aw
        return aw, self.H

    def draw(self):
        c = self.canv
        l = self.l
        h_avant, h_cartes = 15 * mm, 30 * mm
        y_avant = self.H - h_avant
        # Carte AVANT, pleine largeur
        carte(c, 0, y_avant, l, h_avant)
        petites_caps(c, 5 * mm, y_avant + h_avant - 6 * mm, "Avant")
        c.setFont(SERIF, 11)
        c.setFillColor(GRIS)
        t = "Le greffe du tribunal vérifiait votre compte"
        c.drawString(5 * mm, y_avant + 3.2 * mm, t)
        lt = stringWidth(t, SERIF, 11)
        c.setStrokeColor(OR)
        c.setLineWidth(1.1)
        c.line(5 * mm, y_avant + 4.6 * mm, 5 * mm + lt, y_avant + 4.6 * mm)
        # Fleche
        xm = l / 2
        y1, y2 = y_avant - 1.5 * mm, y_avant - 8 * mm
        c.setStrokeColor(OR)
        c.setLineWidth(1.4)
        c.line(xm, y1, xm, y2)
        c.line(xm, y2, xm - 1.6 * mm, y2 + 2.4 * mm)
        c.line(xm, y2, xm + 1.6 * mm, y2 + 2.4 * mm)
        # Deux cartes
        ec = 6 * mm
        lc = (l - ec) / 2
        y_c = y_avant - 9.5 * mm - h_cartes
        for i, (etiquette, contenu) in enumerate([
            ("Désormais", "Le contrôleur interne, s’il en existe un : "
             "subrogé tuteur, co-tuteur ou conseil de famille."),
            ("Sinon", "Un professionnel qualifié, désigné par le juge : "
             "notaire, commissaire de justice, commissaire aux comptes, mandataire "
             "judiciaire à la protection des majeurs."),
        ]):
            x = i * (lc + ec)
            carte(c, x, y_c, lc, h_cartes)
            petites_caps(c, x + 5 * mm, y_c + h_cartes - 6 * mm, etiquette)
            c.setFont(SERIF, 10)
            c.setFillColor(TEXTE)
            yl = y_c + h_cartes - 11.5 * mm
            for ligne in decoupe(contenu, SERIF, 10, lc - 10 * mm)[:5]:
                c.drawString(x + 5 * mm, yl, ligne)
                yl -= 4.6 * mm
        # Legende
        c.setFont(SERIF_I, 9.5)
        c.setFillColor(GRIS)
        c.drawString(0, y_c - 5.5 * mm,
                     "Qui, dans votre cas ? C’est écrit dans votre jugement.")


class SchemaModele(Flowable):
    """Le modele officiel montre comme ce qu'il est : un document. Une miniature
    du formulaire (zones I-III, tableaux A-E, signature) annotee sur la droite —
    le lecteur voit l'objet qu'il devra produire, pas une liste decoree."""

    H = 66 * mm
    LF, HF = 40 * mm, 58 * mm      # la feuille miniature (ratio proche A4)

    def wrap(self, aw, ah):
        self.l = aw
        return aw, self.H

    def _grille(self, c, x, y, l, h, lignes, colonnes):
        c.setFillColor(BLEU_CLair)
        c.rect(x, y + h - h / lignes, l, h / lignes, stroke=0, fill=1)  # ligne d'en-tete
        c.setStrokeColor(BORD)
        c.setLineWidth(0.5)
        c.rect(x, y, l, h, stroke=1, fill=0)
        for i in range(1, lignes):
            c.line(x, y + h * i / lignes, x + l, y + h * i / lignes)
        for j in range(1, colonnes):
            c.line(x + l * j / colonnes, y, x + l * j / colonnes, y + h)

    def _lettre(self, c, x, y, t, cote=3.4 * mm):
        c.setFillColor(MARINE)
        c.roundRect(x, y, cote, cote, 0.8 * mm, stroke=0, fill=1)
        c.setFont(SERIF_B, 6.5)
        c.setFillColor(BLANC)
        c.drawCentredString(x + cote / 2, y + cote / 2 - 0.8 * mm, t)

    def _annotation(self, c, y_zone, titre, detail):
        x_texte = self.LF + 13 * mm
        c.setStrokeColor(OR)
        c.setLineWidth(0.9)
        c.line(self.LF + 2 * mm, y_zone, x_texte - 3 * mm, y_zone)
        c.setFillColor(OR)
        c.circle(self.LF + 2 * mm, y_zone, 1 * mm, stroke=0, fill=1)
        c.setFont(SERIF_B, 10.5)
        c.setFillColor(MARINE)
        c.drawString(x_texte, y_zone + 1.2 * mm, titre)
        c.setFont(SERIF, 9)
        c.setFillColor(GRIS)
        yl = y_zone - 3.4 * mm
        for ligne in decoupe(detail, SERIF, 9, self.l - x_texte)[:3]:
            c.drawString(x_texte, yl, ligne)
            yl -= 3.8 * mm

    def draw(self):
        c = self.canv
        y0 = self.H - self.HF - 2 * mm
        # Ombre puis feuille
        c.setFillColor(colors.HexColor("#d8dee8"))
        c.roundRect(1 * mm, y0 - 1 * mm, self.LF, self.HF, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(BLANC)
        c.setStrokeColor(GRIS)
        c.setLineWidth(0.8)
        c.roundRect(0, y0, self.LF, self.HF, 1.2 * mm, stroke=1, fill=1)
        # En-tete du formulaire
        c.setFont(SANS_B, 4.2)
        c.setFillColor(GRIS)
        c.drawCentredString(self.LF / 2, y0 + self.HF - 4 * mm, "COMPTE DE GESTION — MODÈLE OFFICIEL")
        c.setStrokeColor(BORD)
        c.setLineWidth(0.5)
        c.line(3 * mm, y0 + self.HF - 5.5 * mm, self.LF - 3 * mm, y0 + self.HF - 5.5 * mm)

        # Zone 1 : identification (trois bandes de champs I, II, III)
        y = y0 + self.HF - 10.5 * mm
        for chiffre in ("I", "II", "III"):
            self._lettre(c, 3 * mm, y, chiffre)
            c.setStrokeColor(BORD)
            c.setLineWidth(0.6)
            for k in range(2):
                c.line(8.5 * mm, y + 0.7 * mm + k * 1.7 * mm,
                       self.LF - 3.5 * mm, y + 0.7 * mm + k * 1.7 * mm)
            y -= 5.2 * mm
        y_zone1 = y0 + self.HF - 12.5 * mm

        # Zone 2 : les cinq tableaux (A B / C D / E) — E s'arrete au-dessus
        # de la zone de signature, rien ne se chevauche
        yt = y - 3 * mm
        lt = (self.LF - 8.5 * mm) / 2
        ht, pas = 7 * mm, 8.6 * mm
        positions = [("A", 3 * mm, yt, lt, 3, 3), ("B", 5.5 * mm + lt, yt, lt, 3, 3),
                     ("C", 3 * mm, yt - pas, lt, 2, 2), ("D", 5.5 * mm + lt, yt - pas, lt, 3, 4),
                     ("E", 3 * mm, yt - 2 * pas, lt, 2, 3)]
        for lettre, x, yy, l_, lg, coln in positions:
            self._grille(c, x, yy - ht, l_, ht, lg, coln)
            self._lettre(c, x + 0.6 * mm, yy - 3.8 * mm, lettre)
        y_zone2 = yt - pas - ht / 2

        # Zone 3 : observations + signature, sous le tableau E
        c.setStrokeColor(BORD)
        c.setLineWidth(0.6)
        c.line(3 * mm, y0 + 7 * mm, self.LF - 3.5 * mm, y0 + 7 * mm)
        c.line(3 * mm, y0 + 5.2 * mm, self.LF - 16 * mm, y0 + 5.2 * mm)
        c.setStrokeColor(OR)
        c.setLineWidth(1)
        c.line(self.LF - 16 * mm, y0 + 2.4 * mm, self.LF - 4 * mm, y0 + 2.4 * mm)
        c.setFont(SERIF_I, 6.5)
        c.setFillColor(OR)
        c.drawString(self.LF - 14.5 * mm, y0 + 3.2 * mm, "Wassim T.")
        y_zone3 = y0 + 4.6 * mm

        # Annotations
        self._annotation(c, y_zone1, "L’identification (parties I à III)",
                         "la personne protégée · la mesure et vos coordonnées "
                         "· les actes de gestion de l’année")
        self._annotation(c, y_zone2, "Les cinq tableaux chiffrés (A à E)",
                         "A ressources · B dépenses · C balance · D tous les "
                         "comptes, livrets et contrats · E dettes")
        self._annotation(c, y_zone3, "Les observations et la signature",
                         "votre signature certifie la sincérité du compte")


class Frise(Flowable):
    """Le calendrier : exercice civil, puis depot au 30 juin de l'annee suivante."""

    H = 34 * mm

    def wrap(self, aw, ah):
        self.l = aw
        return aw, self.H

    def draw(self):
        c = self.canv
        y = self.H - 19 * mm
        x0, x1 = 4 * mm, self.l - 4 * mm
        # segment exercice (plein) puis segment N+1 (pointille)
        xc = x0 + (x1 - x0) * 0.58
        c.setStrokeColor(MARINE)
        c.setLineWidth(1.6)
        c.line(x0, y, xc, y)
        c.setDash(2.2, 2.2)
        c.line(xc, y, x1, y)
        c.setDash()
        jalons = [
            (x0 + (x1 - x0) * 0.04, "1er janvier", "l’exercice s’ouvre — la pochette aussi"),
            (xc, "31 décembre", "l’exercice se clôt"),
            (x1 - (x1 - x0) * 0.02, "30 juin suivant", "dépôt au vérificateur, au plus tard"),
        ]
        ancrages = [
            lambda x, yy, t: c.drawString(x - 1 * mm, yy, t),
            lambda x, yy, t: c.drawCentredString(x, yy, t),
            lambda x, yy, t: c.drawRightString(x + 1 * mm, yy, t),
        ]
        for i, (x, haut, bas) in enumerate(jalons):
            ancre = ancrages[0 if i == 0 else (2 if i == len(jalons) - 1 else 1)]
            c.setFillColor(OR)
            c.circle(x, y, 1.9 * mm, stroke=0, fill=1)
            c.setFont(SERIF_B, 10)
            c.setFillColor(MARINE)
            ancre(x, y + 3.6 * mm, haut)
            c.setFont(SERIF, 8.8)
            c.setFillColor(GRIS)
            ancre(x, y - 6 * mm, bas)
        c.setFont(SERIF_I, 9.5)
        c.setFillColor(GRIS)
        c.drawString(0, self.H - 31 * mm,
                     "Votre jugement peut fixer d’autres dates : il prime toujours. "
                     "Fin de mission en cours d’année : trois mois pour transmettre.")


class CarteErreur(Flowable):
    """Une erreur qui coute cher : numero or, barre laterale, fond bleu clair."""

    def __init__(self, numero, titre, corps):
        super().__init__()
        self.numero, self.titre, self.corps = numero, titre, corps

    def wrap(self, aw, ah):
        self.l = aw
        self.retrait = 16 * mm
        self.lignes = decoupe(self.corps, SERIF, 9.8, aw - self.retrait - 5 * mm)
        self.h = max(17 * mm, 8.6 * mm + len(self.lignes) * 4.5 * mm)
        return aw, self.h + 3 * mm

    def draw(self):
        c = self.canv
        y0 = 3 * mm
        carte(c, 0, y0, self.l, self.h, fond=BLEU_CLair, bord=BORD, epaisseur=0.9)
        c.setFillColor(OR)
        c.rect(0, y0, 1.6 * mm, self.h, stroke=0, fill=1)
        c.setFont(SERIF_B, 21)
        c.setFillColor(OR)
        c.drawCentredString(8.2 * mm, y0 + self.h - 10.5 * mm, self.numero)
        c.setFont(SERIF_B, 10.8)
        c.setFillColor(MARINE)
        c.drawString(self.retrait, y0 + self.h - 6.8 * mm, self.titre)
        c.setFont(SERIF, 9.8)
        c.setFillColor(TEXTE)
        yl = y0 + self.h - 11.6 * mm
        for ligne in self.lignes:
            c.drawString(self.retrait, yl, ligne)
            yl -= 4.5 * mm


class Puce(Flowable):
    """Point d'aide : pastille bleu clair, titre marine, corps serif."""

    def __init__(self, titre, corps):
        super().__init__()
        self.titre, self.corps = titre, corps

    def wrap(self, aw, ah):
        self.l = aw
        self.retrait = 10 * mm
        texte = self.corps
        self.lignes = decoupe(texte, SERIF, 10, aw - self.retrait)
        self.h = 6 * mm + len(self.lignes) * 4.8 * mm
        return aw, self.h + 2.2 * mm

    def draw(self):
        c = self.canv
        haut = self.h + 1 * mm
        c.setFillColor(BLEU_CLair)
        c.circle(3.4 * mm, haut - 3.2 * mm, 3.2 * mm, stroke=0, fill=1)
        c.setFillColor(MARINE)
        c.circle(3.4 * mm, haut - 3.2 * mm, 1.1 * mm, stroke=0, fill=1)
        c.setFont(SERIF_B, 10.6)
        c.setFillColor(MARINE)
        c.drawString(self.retrait, haut - 4.4 * mm, self.titre)
        c.setFont(SERIF, 10)
        c.setFillColor(TEXTE)
        yl = haut - 9.6 * mm
        for ligne in self.lignes:
            c.drawString(self.retrait, yl, ligne)
            yl -= 4.8 * mm


class Encadre(Flowable):
    """Encadre plein : etiquette petites caps + texte serif, fond bleu clair."""

    def __init__(self, etiquette, corps, bord_c=MARINE):
        super().__init__()
        self.etiquette, self.corps, self.bord_c = etiquette, corps, bord_c

    def wrap(self, aw, ah):
        self.l = aw
        self.lignes = decoupe(self.corps, SERIF, 9.8, aw - 10 * mm)
        self.h = 12 * mm + len(self.lignes) * 4.5 * mm
        return aw, self.h + 3 * mm

    def draw(self):
        c = self.canv
        y0 = 2 * mm
        carte(c, 0, y0, self.l, self.h, fond=BLEU_CLair, bord=self.bord_c, epaisseur=1.2)
        petites_caps(c, 5 * mm, y0 + self.h - 6.4 * mm, self.etiquette)
        c.setFont(SERIF, 9.8)
        c.setFillColor(TEXTE)
        yl = y0 + self.h - 12 * mm
        for ligne in self.lignes:
            c.drawString(5 * mm, yl, ligne)
            yl -= 4.5 * mm


# --- Habillage des pages -----------------------------------------------------

def _wordmark(c, x, y, corps):
    c.setFont(SERIF_B, corps)
    c.setFillColor(BLANC)
    c.drawString(x, y, "Mon")
    x += stringWidth("Mon", SERIF_B, corps)
    c.setFillColor(OR_CLAIR)
    c.drawString(x, y, "CRG")
    x += stringWidth("CRG", SERIF_B, corps)
    c.setFillColor(BLANC)
    c.drawString(x, y, ".fr")


def bandeau_premiere(c, doc):
    c.saveState()
    H = 30 * mm
    c.setFillColor(MARINE)
    c.rect(0, A4[1] - H, A4[0], H, stroke=0, fill=1)
    c.setFillColor(OR)
    c.rect(0, A4[1] - H - 1.2 * mm, A4[0], 1.2 * mm, stroke=0, fill=1)
    x = MARGE
    if os.path.exists(LOGO):
        cote = 13 * mm
        c.drawImage(LOGO, x, A4[1] - H + (H - cote) / 2, cote, cote,
                    mask="auto", preserveAspectRatio=True)
        x += cote + 5 * mm
    _wordmark(c, x, A4[1] - H / 2 + 0.4 * mm, 19)
    c.setFont(SERIF_I, 10.5)
    c.setFillColor(OR_CLAIR)
    c.drawString(x, A4[1] - H / 2 - 5.6 * mm,
                 "Guide découverte pour tuteurs et curateurs familiaux")
    pied(c, doc)
    c.restoreState()


def bandeau_suite(c, doc):
    c.saveState()
    H = 11 * mm
    c.setFillColor(MARINE)
    c.rect(0, A4[1] - H, A4[0], H, stroke=0, fill=1)
    c.setFillColor(OR)
    c.rect(0, A4[1] - H - 0.9 * mm, A4[0], 0.9 * mm, stroke=0, fill=1)
    _wordmark(c, MARGE, A4[1] - H + 3.4 * mm, 11)
    c.setFont(SERIF_I, 8.5)
    c.setFillColor(BLANC)
    c.drawRightString(A4[0] - MARGE, A4[1] - H + 3.6 * mm,
                      "Le compte de gestion depuis la réforme de 2024")
    pied(c, doc)
    c.restoreState()


def pied(c, doc):
    c.setFont(SANS, 7.6)
    c.setFillColor(GRIS)
    c.drawString(MARGE, 10 * mm, "moncrg.fr — guide offert, sources officielles")
    c.drawRightString(A4[0] - MARGE, 10 * mm, "Page %d" % doc.page)


# --- Contenu -----------------------------------------------------------------

def contenu():
    f = []
    P = lambda t, st="p": f.append(Paragraph(typo(t), S[st]))
    f.append(NextPageTemplate("suite"))

    P("Le compte de gestion depuis la r&eacute;forme de 2024&nbsp;:", "titre1")
    P("ce qui a chang&eacute;, ce qu'on attend de vous", "titre2")
    P("Ce guide est une information g&eacute;n&eacute;rale. Il ne remplace ni les services publics "
      "gratuits d'information et de soutien aux tuteurs familiaux (ISTF, port&eacute;s par les UDAF), "
      "ni un professionnel du droit pour votre situation.", "avert")

    P("1. Ce qui a chang&eacute; en 2024", "h2")
    P("Chaque ann&eacute;e, en tant que tuteur ou curateur, vous rendez compte de votre gestion. "
      "La donne a chang&eacute; avec le <b>d&eacute;cret n&deg; 2024-659 du 2 juillet 2024</b>, "
      "compl&eacute;t&eacute; par <b>deux arr&ecirc;t&eacute;s du 4 juillet 2024</b> (JORF du "
      "12 juillet 2024)&nbsp;: l'un fixe les mod&egrave;les officiels, l'autre la "
      "r&eacute;mun&eacute;ration du professionnel charg&eacute; du contr&ocirc;le.")
    P("<b>Premier changement - qui contr&ocirc;le.</b> Ce n'est plus le greffe du tribunal "
      "qui v&eacute;rifie vos comptes - le circuit d&eacute;pend de votre situation&nbsp;:")
    f.append(SchemaQuiVerifie())
    f.append(Spacer(1, 3 * mm))
    P("Ce v&eacute;rificateur a de vrais moyens&nbsp;: il peut exiger toute pi&egrave;ce utile "
      "et interroger directement les banques - le secret bancaire ne lui est pas opposable "
      "(articles 510 et 513-1 du code civil).")
    P("<b>Second changement - le format.</b> Le compte de gestion n'est plus un tableau "
      "libre&nbsp;: c'est un <b>mod&egrave;le officiel</b>, avec des rubriques pr&eacute;cises, "
      "dans un ordre pr&eacute;cis. Un document qui ne suit pas ce mod&egrave;le part avec un "
      "handicap - et un document qui le suit, pi&egrave;ces &agrave; l'appui, est exactement ce "
      "que les textes demandent au v&eacute;rificateur d'examiner. La bonne nouvelle&nbsp;: un "
      "mod&egrave;le impos&eacute;, c'est aussi un mode d'emploi. Si vous savez ce que chaque "
      "rubrique attend, vous savez exactement quoi pr&eacute;parer.")

    f.append(KeepTogether([
        Paragraph(typo("2. Le mod&egrave;le officiel en un coup d'oeil"), S["h2"]),
        Paragraph(typo("Le mod&egrave;le annex&eacute; &agrave; l'arr&ecirc;t&eacute; "
                       "&laquo;&nbsp;mod&egrave;les&nbsp;&raquo; du 4 juillet 2024 "
                       "(L&eacute;gifrance, r&eacute;f. JORFTEXT000049893287) s'organise en "
                       "trois blocs&nbsp;:"), S["p"]),
        SchemaModele(),
    ]))
    f.append(Spacer(1, 2.5 * mm))
    P("Chaque rubrique a ses attentes pr&eacute;cises, ses pi&egrave;ces justificatives - et ses "
      "pi&egrave;ges. Remplis &laquo;&nbsp;de m&eacute;moire&nbsp;&raquo;, les tableaux produisent "
      "des &eacute;carts inexpliqu&eacute;s&nbsp;; la bonne m&eacute;thode part toujours des "
      "relev&eacute;s bancaires.")

    P("3. Les trois erreurs qui co&ucirc;tent le plus cher", "h2")
    f.append(CarteErreur("1", typo("Le compte oublié"), typo(
        "Ne déclarer au tableau D que le compte courant « qui vit », en omettant "
        "un vieux livret. Le vérificateur peut interroger les banques directement : un compte "
        "présent chez la banque mais absent de votre tableau transforme un oubli en question "
        "désagréable.")))
    f.append(CarteErreur("2", typo("La grosse dépense sans justificatif"), typo(
        "La liste ministérielle des pièces (annexe n° 2 de la circulaire du "
        "ministère de la Justice du 24 septembre 2024) demande un justificatif pour toute "
        "dépense supérieure à 500 €. À l'inverse, pour les dépenses "
        "de la vie courante sous ce seuil, aucun ticket de caisse n'est exigé.")))
    f.append(CarteErreur("3", typo("L'écart inexpliqué"), typo(
        "Un total de ressources ou de dépenses qui ne colle pas aux relevés bancaires "
        "attire l'attention bien plus que "
        "les montants eux-mêmes. Une ligne inhabituelle mais expliquée en deux phrases "
        "factuelles ne pose, elle, aucun problème.")))

    P("4. Votre calendrier", "h2")
    P("Vous transmettez le compte et les pi&egrave;ces au v&eacute;rificateur <b>au plus tard le "
      "30 juin de l'ann&eacute;e suivante</b>. Exemple&nbsp;: le compte de l'ann&eacute;e 2026 se "
      "transmet avant le 30 juin 2027 - et il se pr&eacute;pare maintenant, au fil des mois.")
    f.append(Frise())
    f.append(Spacer(1, 2 * mm))
    f.append(Encadre("Le conseil qui change tout", typo(
        "Ouvrez dès janvier une pochette (papier ou numérique) où chaque facture "
        "de plus de 500 €, chaque ordonnance du juge, chaque attestation arrive au fil de "
        "l'eau. Le dépôt de juin devient un assemblage de pièces déjà "
        "classées."), bord_c=BORD))

    P("5. L'aide gratuite existe - utilisez-la", "h2")
    P("Vous n'avez pas &agrave; faire cela sans aide - et aucune raison de payer pour ce qui est "
      "gratuit.")
    f.append(Puce(typo("L'ISTF (Information et Soutien aux Tuteurs Familiaux)"), typo(
        "Le plus souvent porté par l'UDAF de votre département. Ces dispositifs existent "
        "dans la quasi-totalité des départements et sont financés sur fonds "
        "publics : ils informent, orientent et accompagnent gratuitement les tuteurs familiaux, y "
        "compris sur le compte de gestion. C'est le premier réflexe à avoir. Cherchez "
        "« ISTF » + votre département, ou appelez l'UDAF la plus proche.")))
    f.append(Puce(typo("Le greffe du tribunal qui suit la mesure"), typo(
        "Copie du jugement, dates, transmission.")))
    f.append(Puce(typo("Un professionnel du droit"), typo(
        "Pour toute question propre à votre dossier.")))
    P("MonCRG ne remplace aucun de ces interlocuteurs et ne cherche pas &agrave; le faire. Notre "
      "travail commence apr&egrave;s&nbsp;: une fois le compte rempli, le relire ligne &agrave; "
      "ligne avant le d&eacute;p&ocirc;t.", "note")

    if not DIFFUSION:
        f.append(Spacer(1, 2 * mm))
        f.append(Encadre("Aller plus loin", typo(
            "Votre compte de l'année 2026 se prépare maintenant - et se dépose au "
            "plus tard le 30 juin 2027. Le Pack Contrôle 2026 reprend le modèle officiel "
            "ligne par ligne : pour chaque rubrique - ce qu'on vous demande, où trouver "
            "l'information, l'erreur fréquente et le geste qui vous met en ordre - plus la "
            "checklist officielle des pièces justificatives (1 page, imprimable), le "
            "modèle de courrier à votre banque pour obtenir les relevés annuels de "
            "tous les comptes (article 510), et les rappels d'échéances par email. Il "
            "est livré immédiatement avec la précommande de votre vérification "
            "(89 €, remboursable 30 jours). L'outil ouvre le 30 novembre 2026 : la saisie de "
            "votre exercice y est gratuite et sans limite, et la vérification se relance "
            "autant de fois qu'il le faut jusqu'au dépôt. moncrg.fr")))

    mention = ("MonCRG.fr - Wassim Tallal, entrepreneur individuel, SIREN 795 055 482 - "
               "contact@moncrg.fr. Information g&eacute;n&eacute;rale, jamais de conseil juridique "
               "individualis&eacute; (loi n&deg; 71-1130 du 31 d&eacute;cembre 1971).")
    if DIFFUSION:
        mention += " Document librement diffusable."
    P(mention, "legal")
    return f


doc = BaseDocTemplate(SORTIE, pagesize=A4,
                      leftMargin=MARGE, rightMargin=MARGE,
                      topMargin=36 * mm, bottomMargin=16 * mm,
                      title=TITRE, author="Wassim Tallal - MonCRG.fr",
                      subject="Compte de gestion des tutelles et curatelles familiales")
cadre_1 = Frame(MARGE, 16 * mm, LARGEUR, A4[1] - 36 * mm - 16 * mm, id="c1")
cadre_s = Frame(MARGE, 16 * mm, LARGEUR, A4[1] - 18 * mm - 16 * mm, id="cs")
doc.addPageTemplates([
    PageTemplate(id="premiere", frames=[cadre_1], onPage=bandeau_premiere),
    PageTemplate(id="suite", frames=[cadre_s], onPage=bandeau_suite),
])
doc.build(contenu())
print("ecrit:", SORTIE)
