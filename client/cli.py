
import os, sys, json
from .api import call

def prompt(msg):
    return input(msg).strip()

def menu():
    print("\n=== Annuaire (Client) ===")
    print("1) Lister par catégorie")
    print("2) Lister profs par domaine")
    print("3) Rechercher")
    print("---- Admin ----")
    print("4) Ajouter un membre")
    print("5) Supprimer un membre")
    print("6) Modifier un membre")
    print("7) Mettre sur liste rouge")
    print("8) Enlever de la liste rouge")
    print("0) Quitter")

def get_admin_token():
    return prompt("Mot de passe admin: ")

def main():
    while True:
        menu()
        choice = prompt("Choix: ")
        if choice == "0":
            break
        try:
            if choice == "1":
                cat = prompt("Categorie (professeur|auxiliaire|etudiant): ")
                resp = call("list_by_category", {"category": cat})
            elif choice == "2":
                dom = prompt("Domaine (ex: reseaux): ")
                resp = call("list_profs_by_domain", {"domain": dom})
            elif choice == "3":
                term = prompt("Terme (nom/matricule/courriel): ")
                resp = call("search", {"term": term})
            elif choice == "4":
                admin = get_admin_token()
                member = {}
                member["prenom"] = prompt("Prénom: ")
                member["nom"] = prompt("Nom: ")
                member["categorie"] = prompt("Categorie (professeur|auxiliaire|etudiant): ")
                member["matricule"] = prompt("Matricule (si étudiant, sinon vide): ")
                member["courriel"] = prompt("Courriel: ")
                member["telephone_bureau"] = prompt("Téléphone bureau (si prof/aux): ")
                member["domaine"] = prompt("Domaine (si prof, sinon vide): ")
                resp = call("add", {"member": member}, admin)
            elif choice == "5":
                admin = get_admin_token()
                member_id = prompt("ID à supprimer: ")
                resp = call("delete", {"id": member_id}, admin)
            elif choice == "6":
                admin = get_admin_token()
                member_id = prompt("ID à modifier: ")
                print("Entrer patch JSON (ex: {\"telephone_bureau\":\"+1-819-...\"}):")
                try:
                    patch = json.loads(prompt("> "))
                except Exception:
                    print("Patch JSON invalide")
                    continue
                resp = call("update", {"id": member_id, "patch": patch}, admin)
            elif choice == "7":
                admin = get_admin_token()
                member_id = prompt("ID: ")
                resp = call("redlist", {"id": member_id}, admin)
            elif choice == "8":
                admin = get_admin_token()
                member_id = prompt("ID: ")
                resp = call("unredlist", {"id": member_id}, admin)
            else:
                print("Choix invalide")
                continue
        except KeyboardInterrupt:
            print("\nInterruption utilisateur.")
            break

        if resp.get("ok"):
            print(json.dumps(resp["data"], ensure_ascii=False, indent=2))
        else:
            err = resp.get("error") or {}
            print(f"Erreur [{err.get('code')}]: {err.get('message')}")

if __name__ == "__main__":
    main()
