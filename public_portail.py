import streamlit as st
from supabase import create_client, Client
import datetime

# ---------------------------------------------------------
# Connexion Supabase
# ---------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Portail d'inscription", page_icon="🐶", layout="centered")
st.title("Portail d'inscription du Club Canin")

# ---------------------------------------------------------
# Charger les cours pour afficher la catégorie
# ---------------------------------------------------------
cours = (
    supabase.table("cours")
    .select("id, categorie")
    .execute()
    .data
)

map_cours = {c["id"]: c["categorie"] for c in cours}

# ---------------------------------------------------------
# Choix du type d'utilisateur
# ---------------------------------------------------------
choix = st.radio(
    "Vous êtes :",
    ["Membre du club", "Personne extérieure"]
)

# ---------------------------------------------------------
# FLUX MEMBRE (corrigé : inscription directe dans cours_seances_inscriptions)
# ---------------------------------------------------------
if choix == "Membre du club":

    st.header("Inscription membre")
    email = st.text_input("Votre email (celui enregistré au club)")

    if email:
        membre = (
            supabase.table("membres")
            .select("*")
            .eq("email", email)
            .execute()
            .data
        )

        if not membre:
            st.error("Email inconnu. Vous devez être membre du club.")
            st.stop()

        membre = membre[0]
        membre_id = membre["id"]

        st.success(f"Bienvenue {membre['prenom']} {membre['nom']} !")

        est_benevole = membre.get("benevole", False)

        chiens = (
            supabase.table("chiens")
            .select("*")
            .eq("id_membre", membre_id)
            .execute()
            .data
        )

        if est_benevole:
            st.info("Vous êtes bénévole : l'inscription ne nécessite pas de chien.")
            chien_id = None

        else:
            if not chiens:
                st.error("Aucun chien enregistré pour ce membre.")
                st.stop()

            chien_labels = {f"{c['nom']} ({c['race']})": c["id"] for c in chiens}
            chien_nom = st.selectbox("Votre chien :", list(chien_labels.keys()))
            chien_id = chien_labels[chien_nom]

        # Charger uniquement les séances FUTURES
        aujourdhui = datetime.date.today().isoformat()

        seances = (
            supabase.table("cours_seances")
            .select("*")
            .gte("date_seance", aujourdhui)
            .order("date_seance")
            .execute()
            .data
        )

        if not seances:
            st.error("Aucune séance disponible.")
            st.stop()

        seance_labels = {
            s.get("nom_seance", f"{s['date_seance']}"): s["id"]
            for s in seances
        }

        seance_nom = st.selectbox("Séance :", list(seance_labels.keys()))
        seance_id = seance_labels[seance_nom]

        if st.button("S'inscrire à la séance"):

            # ⭐ INSCRIPTION DIRECTE DANS cours_seances_inscriptions (plus de préinscription pour les membres)
            supabase.table("cours_seances_inscriptions").insert({
                "seance_id": seance_id,
                "membre_id": membre_id,
                "chien_id": chien_id,
                "type_inscription": "membre",
                "present": False,
                "actif": True
            }).execute()

            st.success("Votre inscription a été enregistrée !")


# ---------------------------------------------------------
# FLUX EXTÉRIEUR (inchangé pour l’instant)
# ---------------------------------------------------------
if choix == "Personne extérieure":

    st.header("Préinscription extérieur")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email_ext = st.text_input("Email")
    telephone = st.text_input("Téléphone")

    chien_nom = st.text_input("Nom du chien")
    chien_race = st.text_input("Race du chien")

    aujourdhui = datetime.date.today().isoformat()

    seances = (
        supabase.table("cours_seances")
            .select("*")
            .gte("date_seance", aujourdhui)
            .order("date_seance")
            .execute()
            .data
    )

    if seances:
        seance_labels = {
            s.get("nom_seance", f"{s['date_seance']}"): s["id"]
            for s in seances
        }

        seance_nom = st.selectbox("Séance :", list(seance_labels.keys()))
        seance_id = seance_labels[seance_nom]

    if st.button("Envoyer la préinscription"):

        seance = next(s for s in seances if s["id"] == seance_id)

        data = {
            "nom": nom,
            "prenom": prenom,
            "email": email_ext,
            "telephone": telephone,

            "chien_nom": chien_nom,
            "chien_race": chien_race,
            "chien_naissance": None,

            "seance_id": seance_id,
            "cours_id": seance.get("cours_id"),
            "cours_nom": map_cours.get(seance.get("cours_id")),
            "date_seance": seance["date_seance"],
            "heure_debut": seance.get("heure_debut"),

            "traitee": False,
            "acceptee": False,
            "type": "exterieur"
        }

        supabase.table("preinscriptions").insert(data).execute()
        st.success("Votre préinscription a été enregistrée !")

     
