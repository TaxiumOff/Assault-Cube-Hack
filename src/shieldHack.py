"""
AssaultCube - Bouclier (armure) infini (mode solo, à but d'apprentissage)
Interface colorée grâce à colorama.

Prérequis :
    pip install pymem colorama

Utilisation :
    1. Lance AssaultCube et démarre une partie solo
    2. Lance ce script (idéalement dans un terminal administrateur)
    3. Ctrl+C pour arrêter

Principe :
    C'est le MÊME pointeur statique que pour les balles : il mène à la
    structure du joueur local. Seul l'offset final change.

        ac_client.exe + 0x17E0A8  -->  [adresse de la structure du joueur]
                                              + 0xF0   -->  [bouclier]
                                              + 0x140  -->  [balles]
"""

import sys
import time

import pymem
import pymem.exception
import pymem.process
from colorama import Fore, Style, init

# autoreset=True : les couleurs sont remises à zéro après chaque print()
init(autoreset=True)

# ----------------------------------------------------------------------------
# Constantes issues du Pointer Scan de Cheat Engine (shield2.PTR)
# ----------------------------------------------------------------------------
PROCESS_NAME = "ac_client.exe"
PLAYER_PTR_OFFSET = 0x17E0A8   # pointeur statique vers la structure du joueur
SHIELD_OFFSET = 0xF0           # offset du bouclier dans cette structure
SHIELD_VALUE = 100             # valeur imposée (100 = bouclier plein)
REFRESH_DELAY = 0.05

# ----------------------------------------------------------------------------
# Raccourcis de style
# ----------------------------------------------------------------------------
B = Style.BRIGHT
RED, GREEN, YELLOW = Fore.RED, Fore.GREEN, Fore.YELLOW
CYAN, MAGENTA, WHITE = Fore.CYAN, Fore.MAGENTA, Fore.WHITE
GREY = Style.DIM + Fore.WHITE
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def banner():
    """Affiche le logo ASCII avec un petit dégradé de couleurs."""
    lines = [
        r"    ___                   ____  __     ______      __         ",
        r"   /   |  _____________ _/ / /_/ /_   / ____/_  __/ /_  ___   ",
        r"  / /| | / ___/ ___/ __ `/ / __/ __/  / /   / / / / __ \/ _ \  ",
        r" / ___ |(__  |__  ) /_/ / / /_/ /_   / /___/ /_/ / /_/ /  __/  ",
        r"/_/  |_/____/____/\__,_/_/\__/\__/   \____/\__,_/_.___/\___/   ",
    ]
    colors = [CYAN, CYAN, MAGENTA, MAGENTA, MAGENTA]
    print()
    for color, line in zip(colors, lines):
        print(B + color + line)
    print(GREY + "  " + "─" * 62)
    print(B + CYAN + "  BOUCLIER INFINI " + GREY + "│ mode solo · apprentissage")
    print(GREY + "  " + "─" * 62 + "\n")


def log(kind, message):
    """Affiche un message préfixé par une pastille colorée."""
    tags = {
        "ok": (GREEN, "[ OK ]"),
        "info": (CYAN, "[INFO]"),
        "warn": (YELLOW, "[WARN]"),
        "err": (RED, "[ERR ]"),
    }
    color, tag = tags[kind]
    print(f" {B}{color}{tag}{Style.RESET_ALL} {WHITE}{message}")


def status_line(frame, state, player_base, shield, writes):
    """
    Ligne de statut qui s'actualise sur place (\\r).
    \\033[K efface la fin de la ligne pour éviter les résidus.
    """
    spin = SPINNER[frame % len(SPINNER)]

    if state == "active":
        badge = B + GREEN + "● ACTIF     "
    else:
        badge = B + YELLOW + "● EN ATTENTE"

    base_txt = f"{player_base:#010x}" if player_base else "----------"
    shield_txt = f"{shield:>4}" if shield is not None else "  --"

    line = (
        f"\r {B}{MAGENTA}{spin}{Style.RESET_ALL} {badge}{Style.RESET_ALL} "
        f"{GREY}│ {WHITE}Joueur {CYAN}{base_txt} "
        f"{GREY}│ {WHITE}Bouclier {B}{GREEN}{shield_txt} "
        f"{GREY}│ {WHITE}Écritures {YELLOW}{writes}\033[K"
    )
    sys.stdout.write(line)
    sys.stdout.flush()


def main():
    banner()

    # 1) Attache au processus du jeu
    log("info", f"Recherche du processus {B}{PROCESS_NAME}{Style.RESET_ALL}...")
    try:
        pm = pymem.Pymem(PROCESS_NAME)
    except pymem.exception.ProcessNotFound:
        log("err", "Jeu introuvable. Lance AssaultCube puis relance ce script.")
        return
    except Exception as exc:  # ex. droits insuffisants
        log("err", f"Impossible de s'attacher au processus : {exc}")
        log("warn", "Essaie de lancer le terminal en administrateur.")
        return
    log("ok", f"Attaché au processus (PID {B}{pm.process_id}{Style.RESET_ALL})")

    # 2) Base du module ac_client.exe (le "ac_client.exe" de Cheat Engine)
    module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)
    if module is None:
        log("err", f"Module {PROCESS_NAME} introuvable.")
        return
    base_address = module.lpBaseOfDll
    log("ok", f"Base du module : {B}{CYAN}{hex(base_address)}")
    log("info", f"Pointeur joueur : {CYAN}+{PLAYER_PTR_OFFSET:#x}{WHITE}"
                f"  Offset bouclier : {CYAN}+{SHIELD_OFFSET:#x}")
    log("info", f"Valeur imposée : {B}{GREEN}{SHIELD_VALUE}")
    print(GREY + "\n  Ctrl+C pour arrêter\n")

    writes = 0
    frame = 0

    try:
        while True:
            try:
                # 3) Lecture du pointeur statique -> base de la structure joueur
                player_base = pm.read_int(base_address + PLAYER_PTR_OFFSET)

                if player_base == 0:
                    # Pas de partie en cours (menu, chargement de map...)
                    status_line(frame, "wait", 0, None, writes)
                else:
                    # 4) Adresse finale = base joueur + offset bouclier
                    shield_address = player_base + SHIELD_OFFSET

                    # 5) On écrit la valeur (le jeu la baisse quand on est touché)
                    pm.write_int(shield_address, SHIELD_VALUE)
                    writes += 1

                    # Relecture pour afficher la vraie valeur en mémoire
                    shield = pm.read_int(shield_address)
                    status_line(frame, "active", player_base, shield, writes)

            except (pymem.exception.MemoryReadError,
                    pymem.exception.MemoryWriteError):
                # Pointeur temporairement invalide (respawn, changement de map)
                status_line(frame, "wait", 0, None, writes)

            frame += 1
            time.sleep(REFRESH_DELAY)

    except KeyboardInterrupt:
        print(f"\n\n {B}{YELLOW}[STOP]{Style.RESET_ALL} {WHITE}Arrêt demandé. "
              f"{YELLOW}{writes}{WHITE} écritures effectuées. À bientôt !\n")


if __name__ == "__main__":
    main()