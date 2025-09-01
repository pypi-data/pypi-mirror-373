#!/usr/bin/env python

from travo.script import main
from methnum import course


def methnum():
    usage = f"""Aide pour l'utilisation de la commande {course.script}
    
    Télécharger ou mettre à jour un TP ou un projet (ici pour la semaine 1):
    
        {course.script} fetch Seance1
    
    Lancer le notebook Jupyter (inutile sur le service JupyterHub):
    
        {course.script} jupyter lab
    
    Soumettre son TP ou projet (ici pour la séance 1 et un étudiant du groupe MP1):
    
        {course.script} submit Seance MP1
    
    Télécharger le résultat de la correction automatique (ici pour la séance 1)
    
        {course.script} fetch_feedback Semaine1
    
    Plus d'aide:
    
        {course.script} --help
    """
    if course.student_groups is not None:
        usage += f"\nGroupes: {', '.join(course.student_groups)}\n"

    main(course, usage)

