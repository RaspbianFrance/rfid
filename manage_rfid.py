#!/usr/bin/env python3.5
#-- coding: utf-8 --

import RPi.GPIO as GPIO #Importe la bibliothèque pour contrôler les GPIOs
from pirc522 import RFID
import time
import sys
import json

def read_uid () :
    print('En attente d\'un badge (pour quitter, Ctrl + c): ') #On affiche un message demandant à l'utilisateur de passer son badge

    #On va faire une boucle infinie pour lire en boucle
    while True :
        rc522.wait_for_tag() #On attnd qu'une puce RFID passe à portée
        (error, tag_type) = rc522.request() #Quand une puce a été lue, on récupère ses infos

        if not error : #Si on a pas d'erreur
            (error, uid) = rc522.anticoll() #On nettoie les possibles collisions, ça arrive si plusieurs cartes passent en même temps

            if not error : #Si on a réussi à nettoyer
                return uid


def read_badges_list (list_path = './list_badges.json') :
    try :
        file = open(list_path, 'r')
        file_content = file.read()
        return json.loads(file_content)

    except OSError as error :
        print('Impossible to read file {}'.format(list_path))
        sys.exit()

    except json.JSONDecodeError as error :
        print('Le fichier {} n\'est pas une chaine json valide.'.format(list_path))
        sys.exit()


def write_badges_list (badges_list, list_path = './list_badges.json') :
    try :
        file = open(list_path, 'w')
        json_string = json.dumps(badges_list)
        file.write(json_string)
        return True

    except OSError as error :
        print('Impossible to write file {}'.format(list_path))
        sys.exit()


def add_badge (name, uid) :
    badges_list = read_badges_list()
    badges_list.append({
        'name': name,
        'uid': uid,
    })
    write_badges_list(badges_list = badges_list)


def delete_badge (name = False, uid = False) :
    if name == False and uid == False :
        return False

    badges_list = read_badges_list()
    for key, badge in enumerate(badges_list) :
        if name :
            if badge['name'] == name :
                del badges_list[key]
                write_badges_list(badges_list = badges_list)
                return True
        else :
            if badge['uid'] == uid :
                del badges_list[key]
                write_badges_list(badges_list = badges_list)
                return True

    return False


def search_badge (name = False, uid = False) :
    if name == False and uid == False :
        return False

    badges_list = read_badges_list()

    for key, badge in enumerate(badges_list) :
        if name :
            if badge['name'] == name :
                return True
        else :
            if badge['uid'] == uid :
                return True

    return False



GPIO.setmode(GPIO.BOARD) #Définit le mode de numérotation (Board)
GPIO.setwarnings(False) #On désactive les messages d'alerte

rc522 = RFID() #On instancie la lib

while True :
    print("\n")
    print('Voulez-vous :')
    print('1 - Supprimer un tag')
    print('2 - Ajouter un tag')
    print('3 - Lister les badges')
    print('4 - Quitter')
    action = input("Tapez le chiffre : ")
    print("\n")

    #On va supprimer un badge
    if action == "1" :
        print('Voulez-vous le supprimer par :')
        print('1 - Son nom')
        print('2 - Son uid')
        method = input("Tapez le chiffre : ")
        print("\n")

        if method == "1" :
            name = input("Tapez le nom du badge à supprimer : ")

            has_delete = delete_badge(name = name)
            if has_delete :
                print('Le badge a bien été supprimé')
            else :
                print('Le badge {} n\'existe pas'.format(name))
        else :
            uid = read_uid()

            has_delete = delete_badge(uid = uid)
            if has_delete :
                print('Le badge a bien été supprimé')
            else :
                print('Le badge passé n\'existe pas encore')

    #On va ajouter un badge
    elif action == "2" :
        valid_name = False
        while not valid_name :
            name = input('Tapez le nom du badge à ajouter : ')

            if search_badge(name = name) :
                print('Un badge avec ce nom existe déjà.')
                continue
            
            valid_name = True
        
        uid = read_uid()
        add_badge(name, uid)
        print('Le badge a bien été ajouté')
       
    #On va lister les badge
    elif action == "3" :
        print("Liste des badges :")
        badges_list = read_badges_list()
        for badge in badges_list :
            print('Nom : {}'.format(badge['name']))
            print('Uid : {}'.format(badge['uid']))
            print("\n")

    #On va quitter le programme
    else :
        print('Goodbye.')
        sys.exit()



