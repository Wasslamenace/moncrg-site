#!/usr/bin/env python3
"""Genere guide-decouverte.pdf (le lead magnet servi par guide.html).

Pourquoi ce script existe : le PDF a ete produit une fois a la main le 07/08/2026,
sans source. Quand l'offre fondateur a 79 EUR a ete abandonnee le 17/08 et la date
d'ouverture fixee au 30 novembre 2026, index.html a ete corrige mais le PDF est
reste en production avec l'ancienne offre — invisible a tout grep sur le HTML.
Le contenu vit desormais ici, en clair, et se regenere par :

    python3 outils/build-guide-decouverte.py

Toute modification de prix, de date ou d'offre doit passer par ce fichier.

Deux sorties :
    python3 outils/build-guide-decouverte.py             -> guide-decouverte.pdf
    python3 outils/build-guide-decouverte.py --diffusion -> guide-decouverte-diffusion.pdf

La variante --diffusion omet l'encadre commercial final (< Aller plus loin >) :
c'est la version remise aux services publics (ISTF/UDAF) pour qu'ils puissent la
diffuser aux familles sans paraitre recommander un produit payant. Tout le reste
est identique.
"""

import sys

DIFFUSION = "--diffusion" in sys.argv

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                Paragraph, Spacer, ListFlowable, ListItem)

SORTIE = "guide-decouverte-diffusion.pdf" if DIFFUSION else "guide-decouverte.pdf"
TITRE = "Le compte de gestion 2024\u00a0: ce qui a chang\u00e9, ce qu'on attend de vous"

MARINE = colors.HexColor("#1d3a5f")
DOUX = colors.HexColor("#5d6b7d")

def style(nom, **kw):
    base = dict(fontName="Helvetica", fontSize=9.5, leading=13.5,
                textColor=colors.HexColor("#1b2430"), spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(nom, **base)

S = {
    "h1": style("h1", fontName="Helvetica-Bold", fontSize=17, leading=21,
                textColor=MARINE, spaceAfter=4),
    "sous": style("sous", fontSize=10, leading=14, textColor=DOUX, spaceAfter=10),
    "avert": style("avert", fontSize=8, leading=11, textColor=DOUX, spaceAfter=14),
    "h2": style("h2", fontName="Helvetica-Bold", fontSize=12, leading=15,
                textColor=MARINE, spaceBefore=10, spaceAfter=5),
    "p": style("p", alignment=TA_JUSTIFY),
    "puce": style("puce", alignment=TA_JUSTIFY, spaceAfter=4),
    "encadre": style("encadre", fontSize=9, leading=12.5, alignment=TA_JUSTIFY,
                     borderColor=colors.HexColor("#dfe3ea"), borderWidth=0.7,
                     borderPadding=8, backColor=colors.HexColor("#f6f7f9"),
                     spaceBefore=8, spaceAfter=8),
    "legal": style("legal", fontSize=7.5, leading=10, textColor=DOUX, spaceBefore=10),
}

def liste(items, st="puce"):
    return ListFlowable([ListItem(Paragraph(t, S[st]), leftIndent=14) for t in items],
                        bulletType="bullet", start="\u2022", bulletFontSize=8,
                        bulletOffsetY=-1, leftIndent=14, bulletColor=MARINE, spaceAfter=6)

def habillage(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(DOUX)
    canvas.drawString(18 * mm, A4[1] - 12 * mm,
                      "MonCRG.fr - %s - offert par moncrg.fr" % TITRE)
    canvas.setStrokeColor(colors.HexColor("#dfe3ea"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, "Page %d" % doc.page)
    canvas.restoreState()

def contenu():
    f = []
    P = lambda t, st="p": f.append(Paragraph(t, S[st]))

    P("Le compte de gestion depuis la r&eacute;forme de 2024&nbsp;:<br/>"
      "ce qui a chang&eacute;, ce qu'on attend de vous", "h1")
    P("Guide d&eacute;couverte pour tuteurs et curateurs familiaux - offert par MonCRG.fr", "sous")
    P("Ce guide est une information g&eacute;n&eacute;rale. Il ne remplace ni les services publics "
      "gratuits d'information et de soutien aux tuteurs familiaux (ISTF, port&eacute;s par les UDAF), "
      "ni un professionnel du droit pour votre situation.", "avert")

    P("1. Ce qui a chang&eacute; en 2024", "h2")
    P("Chaque ann&eacute;e, en tant que tuteur ou curateur, vous rendez compte de votre gestion. "
      "Deux textes de 2024 ont chang&eacute; la donne&nbsp;: le <b>d&eacute;cret n&deg; 2024-659 du "
      "2 juillet 2024</b> et l'<b>arr&ecirc;t&eacute; du 4 juillet 2024</b> (JORF du 12 juillet 2024).")
    P("<b>Premier changement - qui contr&ocirc;le.</b> Ce n'est plus le greffe du tribunal qui "
      "v&eacute;rifie vos comptes. Selon votre situation, c'est un &laquo;&nbsp;contr&ocirc;leur "
      "interne&nbsp;&raquo; (subrog&eacute; tuteur, co-tuteur, conseil de famille) ou un "
      "<b>professionnel qualifi&eacute;</b> d&eacute;sign&eacute; par le juge (notaire, commissaire "
      "de justice, commissaire aux comptes, mandataire judiciaire...). Ce v&eacute;rificateur a de "
      "vrais moyens&nbsp;: il peut exiger toute pi&egrave;ce utile et interroger directement les "
      "banques - le secret bancaire ne lui est pas opposable (articles 510 et 513-1 du code civil).")
    P("<b>Second changement - le format.</b> Le compte de gestion n'est plus un tableau libre&nbsp;: "
      "c'est un <b>mod&egrave;le officiel</b>, avec des rubriques pr&eacute;cises, dans un ordre "
      "pr&eacute;cis. Un document qui ne suit pas ce mod&egrave;le part avec un handicap - et un "
      "document qui le suit, pi&egrave;ces &agrave; l'appui, est exactement ce que les textes "
      "demandent au v&eacute;rificateur d'examiner.")
    P("La bonne nouvelle&nbsp;: un mod&egrave;le impos&eacute;, c'est aussi un mode d'emploi. Si vous "
      "savez ce que chaque rubrique attend, vous savez exactement quoi pr&eacute;parer.")

    P("2. Le mod&egrave;le officiel en un coup d'oeil", "h2")
    P("Le mod&egrave;le annex&eacute; &agrave; l'arr&ecirc;t&eacute; du 4 juillet 2024 "
      "(L&eacute;gifrance, r&eacute;f. JORFTEXT000049893287) s'organise en trois blocs&nbsp;:")
    f.append(liste([
        "<b>Trois parties d'identification</b>&nbsp;: la personne prot&eacute;g&eacute;e (I), la "
        "mesure de protection et vos coordonn&eacute;es (II), les actes de gestion de "
        "l'ann&eacute;e - ventes, achats, placements (III).",
        "<b>Cinq tableaux chiffr&eacute;s</b>&nbsp;: A. les ressources de l'ann&eacute;e - "
        "B. les d&eacute;penses - C. la balance - D. tous les comptes bancaires, livrets et "
        "contrats - E. les dettes en cours.",
        "<b>Les observations et la signature</b>, qui certifie la sinc&eacute;rit&eacute; du compte.",
    ]))
    P("Chaque rubrique a ses attentes pr&eacute;cises, ses pi&egrave;ces justificatives - et ses "
      "pi&egrave;ges. Les remplir &laquo;&nbsp;de m&eacute;moire&nbsp;&raquo; est la premi&egrave;re "
      "cause d'&eacute;carts inexpliqu&eacute;s&nbsp;; la bonne m&eacute;thode part toujours des "
      "relev&eacute;s bancaires.")

    P("3. Les trois erreurs qui co&ucirc;tent le plus cher", "h2")
    f.append(liste([
        "<b>Le compte oubli&eacute;.</b> Ne d&eacute;clarer au tableau D que le compte courant "
        "&laquo;&nbsp;qui vit&nbsp;&raquo;, en omettant un vieux livret. Le v&eacute;rificateur peut "
        "interroger les banques directement&nbsp;: un compte pr&eacute;sent chez la banque mais "
        "absent de votre tableau transforme un oubli en question d&eacute;sagr&eacute;able.",
        "<b>La grosse d&eacute;pense sans justificatif.</b> La liste minist&eacute;rielle des "
        "pi&egrave;ces demande un justificatif pour toute d&eacute;pense sup&eacute;rieure &agrave; "
        "500&nbsp;&euro;. &Agrave; l'inverse, inutile de garder les tickets des courses courantes - "
        "la circulaire du 24 septembre 2024 le dit express&eacute;ment.",
        "<b>L'&eacute;cart inexpliqu&eacute;.</b> Un total de ressources ou de d&eacute;penses qui ne "
        "colle pas aux relev&eacute;s bancaires attire l'attention bien plus que les montants "
        "eux-m&ecirc;mes. Une ligne inhabituelle mais expliqu&eacute;e en deux phrases factuelles ne "
        "pose, elle, aucun probl&egrave;me.",
    ]))

    P("4. Votre calendrier", "h2")
    f.append(liste([
        "Vous transmettez le compte et les pi&egrave;ces au v&eacute;rificateur <b>au plus tard le "
        "30 juin de l'ann&eacute;e suivante</b>. Exemple&nbsp;: le compte de l'ann&eacute;e 2026 se "
        "transmet avant le 30 juin 2027 - <b>et il se pr&eacute;pare maintenant, au fil des mois</b>.",
        "Si votre mission prend fin en cours d'ann&eacute;e, le compte se transmet <b>dans les trois "
        "mois</b> suivant la fin de la mission.",
        "<b>V&eacute;rifiez votre jugement</b>&nbsp;: le juge peut fixer des dates "
        "diff&eacute;rentes. La date qui vous engage est celle de votre jugement s'il en fixe "
        "une&nbsp;; &agrave; d&eacute;faut, le 30 juin.",
    ]))
    P("Un conseil qui change tout&nbsp;: ouvrez d&egrave;s janvier une pochette (papier ou "
      "num&eacute;rique) o&ugrave; chaque facture de plus de 500&nbsp;&euro;, chaque ordonnance du "
      "juge, chaque attestation arrive au fil de l'eau. Le d&eacute;p&ocirc;t de juin devient un "
      "assemblage de pi&egrave;ces d&eacute;j&agrave; class&eacute;es.")

    P("5. L'aide gratuite existe - utilisez-la", "h2")
    P("Vous n'&ecirc;tes pas seul, et il n'y a aucune raison de payer pour ce qui est gratuit.")
    f.append(liste([
        "<b>L'ISTF</b> (Information et Soutien aux Tuteurs Familiaux), le plus souvent port&eacute; "
        "par l'UDAF de votre d&eacute;partement. Ces dispositifs existent dans la quasi-totalit&eacute; "
        "des d&eacute;partements et sont financ&eacute;s sur fonds publics&nbsp;: ils informent, "
        "orientent et accompagnent gratuitement les tuteurs familiaux, y compris sur le compte de "
        "gestion. C'est le premier r&eacute;flexe &agrave; avoir. Cherchez &laquo;&nbsp;ISTF&nbsp;&raquo; "
        "+ votre d&eacute;partement, ou appelez l'UDAF la plus proche.",
        "<b>Le greffe du tribunal</b> qui suit la mesure&nbsp;: copie du jugement, dates, "
        "transmission.",
        "<b>Un professionnel du droit</b> pour toute question propre &agrave; votre dossier.",
    ]))
    P("MonCRG ne remplace aucun de ces interlocuteurs et ne cherche pas &agrave; le faire. Notre "
      "travail commence apr&egrave;s&nbsp;: une fois le compte rempli, le relire ligne &agrave; ligne "
      "avant le d&eacute;p&ocirc;t.")

    if DIFFUSION:
        P("MonCRG.fr - Wassim Tallal, entrepreneur individuel, SIREN 795 055 482 - "
          "contact@moncrg.fr. Information g&eacute;n&eacute;rale, jamais de conseil juridique "
          "individualis&eacute; (loi n&deg; 71-1130 du 31 d&eacute;cembre 1971). Document "
          "librement diffusable.", "legal")
        return f

    P("Aller plus loin", "h2")
    P("Votre compte de l'ann&eacute;e 2026 se pr&eacute;pare <b>maintenant</b> - et se d&eacute;pose "
      "au plus tard le 30 juin 2027. <b>Le Pack Contr&ocirc;le 2026</b> reprend le mod&egrave;le "
      "officiel <b>ligne par ligne</b>&nbsp;: pour chaque rubrique - ce qu'on vous demande, o&ugrave; "
      "trouver l'information, l'erreur fr&eacute;quente et le geste qui vous met en ordre - plus la "
      "<b>checklist officielle des pi&egrave;ces justificatives</b> (1 page, imprimable), le "
      "<b>mod&egrave;le de courrier &agrave; votre banque</b> pour obtenir les relev&eacute;s annuels "
      "de tous les comptes (article 510), et les rappels d'&eacute;ch&eacute;ances par email. Il est "
      "livr&eacute; imm&eacute;diatement avec la pr&eacute;commande de votre v&eacute;rification "
      "(89&nbsp;&euro;, remboursable 30 jours). L'outil ouvre le <b>30 novembre 2026</b>&nbsp;: la "
      "saisie de votre exercice y est gratuite et sans limite, et la v&eacute;rification se relance "
      "autant de fois qu'il le faut jusqu'au d&eacute;p&ocirc;t. <b>moncrg.fr</b>", "encadre")

    P("MonCRG.fr - Wassim Tallal, entrepreneur individuel, SIREN 795 055 482 - contact@moncrg.fr. "
      "Information g&eacute;n&eacute;rale, jamais de conseil juridique individualis&eacute; "
      "(loi n&deg; 71-1130 du 31 d&eacute;cembre 1971).", "legal")
    return f

doc = BaseDocTemplate(SORTIE, pagesize=A4,
                      leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=20 * mm, bottomMargin=18 * mm,
                      title=TITRE, author="Wassim Tallal - MonCRG.fr",
                      subject="Compte de gestion des tutelles et curatelles familiales")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="corps")
doc.addPageTemplates([PageTemplate(id="std", frames=[frame], onPage=habillage)])
doc.build(contenu())
print("ecrit:", SORTIE)
