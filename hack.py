import pymem
import time
import colorama

# init
pm = pymem.Pymem("ac_client.exe")

PROCESS_NAME = "ac_client.exe"    # nom du processus du jeu
PLAYER_PTR_OFFSET = 0x17E0A8      # offset statique depuis la base du module
AMMO_OFFSET = 0x140               # offset des balles dans la structure du joueur        # valeur qu'on veut imposer
REFRESH_DELAY = 0.05              # pause entre deux écritures (en secondes)

# Don't forget to change the values
def shield_hack(num):
    # variables
    shield_address = 0x00861938

    # reading memory
    shield = pm.read_int(shield_address)
    print("Current shield :",shield)

    pm.write_int(shield_address, num)

def bullet_hack(PROCESS_NAME, PLAYER_PTR_OFFSET, AMMO_OFFSET, AMMO_VALUE, REFRESH_DELAY):
    # 1) On s'attache au processus du jeu.
    #    Si le jeu n'est pas lancé, pymem lève une exception.
    try:
        pm = pymem.Pymem(PROCESS_NAME)
    except pymem.exception.ProcessNotFound:
        print(f"[!] {PROCESS_NAME} introuvable. Lance d'abord le jeu.")
        return

    # 2) On récupère l'adresse de base du module ac_client.exe.
    #    C'est l'équivalent du "ac_client.exe" affiché par Cheat Engine.
    module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)
    base_address = module.lpBaseOfDll
    print(f"[+] Base de {PROCESS_NAME} : {hex(base_address)}")

    print("[+] Munitions verrouillées. Ctrl+C pour arrêter.")

    try:
        while True:
            try:
                # 3) On lit le pointeur statique : il contient l'adresse
                #    de la structure du joueur local (32 bits => read_int).
                player_base = pm.read_int(base_address + PLAYER_PTR_OFFSET)

                # Si le pointeur vaut 0, aucune partie n'est en cours
                # (menu principal, chargement de map...) : on attend.
                if player_base == 0:
                    time.sleep(0.5)
                    continue

                # 4) Adresse finale = base du joueur + offset des balles.
                ammo_address = player_base + AMMO_OFFSET

                # 5) On écrit la nouvelle valeur. Comme le jeu décrémente
                #    les balles à chaque tir, on la réécrit en boucle.
                pm.write_int(ammo_address, AMMO_VALUE)

            except pymem.exception.MemoryReadError:
                # Le pointeur peut être temporairement invalide (changement
                # de map, respawn...). On ignore et on réessaie.
                pass
            except pymem.exception.MemoryWriteError:
                pass

            time.sleep(REFRESH_DELAY)

    except KeyboardInterrupt:
        print("\n[+] Arrêt du script.")
    
def health_hack(num):
    """ 
    Increase the health points
    """
    # variables
    health_address = 0x0070D4A4

    # reading memory
    health = pm.read_int(health_address)
    print("Current health :",health)

    pm.write_int(health_address, num)


while True:
    param = input("What do you want to hack ? (bullet:1 ; health:2 ; shield:3) : ")
    if param == "1":
        AMMO_VALUE = int(input("How many bullet do you want ?"))
        bullet_hack(PROCESS_NAME, PLAYER_PTR_OFFSET, AMMO_OFFSET, AMMO_VALUE, REFRESH_DELAY)
    elif param == "2":
        num = int(input("How many health points do you want ?"))
        health_hack(num)
    elif param == "3":
        num = int(input("How many health points do you want ?"))
        shield_hack(num)
    else:
        print("Error please retry")