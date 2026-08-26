import streamlit as st
from supabase import create_client, Client
import datetime

# ---------------------------------------------------------
# Connexion Supabase
# ---------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Portail d'inscription du Club Canin", page_icon="🐶", layout="centered")
st.title("Portail d'inscription du Club Canin")

# ---------------------------------------------------------
# Choix du type d'utilisateur
# ---------------------------------------------------------
choix = st.radio(
    "Vous êtes :",
    ["Membre du club", "Personne extérieure"]
)

# ---------------------------------------------------------
# FLUX MEMBRE (sans heure)
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

        # Charger les séances futures (sans heure)
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

        # PAS d'heure pour les membres
        seance_labels = {
            f"{s['date_seance']}": s["id"]
            for s in seances
        }

        seance_nom = st.selectbox("Séance :", list(seance_labels.keys()))
        seance_id = seance_labels[seance_nom]

        if st.button("S'inscrire à la séance"):

            # Vérifier doublon
            existe = (
                supabase.table("cours_seances_inscriptions")
                .select("id")
                .eq("seance_id", seance_id)
                .eq("chien_id", chien_id)
                .execute()
                .data
            )

            if existe:
                st.error("Ce chien est déjà inscrit à cette séance.")
                st.stop()

            # Inscription membre
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
# FLUX EXTÉRIEUR (avec heure)
# ---------------------------------------------------------
if choix == "Personne extérieure":

    st.header("Préinscription extérieur")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email_ext = st.text_input("Email")
    telephone = st.text_input("Téléphone")

    # Empêcher un membre d'utiliser le flux extérieur
    if email_ext:
        membre_existe = (
            supabase.table("membres")
            .select("id")
            .eq("email", email_ext)
            .execute()
            .data
        )
        if membre_existe:
            st.error("Vous êtes membre du club. Veuillez utiliser le formulaire membre.")
            st.stop()

    chien_nom = st.text_input("Nom du chien")
    chien_race = st.text_input("Race du chien")

    # Charger les séances futures (avec heure)
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

    # Ici on lit heure_debut (si elle existe)
    seance_labels = {
        f"{s['date_seance']} - {s.get('heure_debut', 'Non spécifiée')}": s["id"]
        for s in seances
    }

    seance_nom = st.selectbox("Séance :", list(seance_labels.keys()))
    seance_id = seance_labels[seance_nom]

    # Extraire date + heure
    date_seance_str, heure_debut_str = seance_nom.split(" - ")
    date_seance_value = datetime.date.fromisoformat(date_seance_str)

    if st.button("Envoyer la préinscription"):

        if not nom or not prenom or not email_ext or not telephone or not chien_nom or not chien_race:
            st.error("Veuillez remplir tous les champs obligatoires.")
            st.stop()

        # Vérifier doublon extérieur
        existe_ext = (
            supabase.table("preinscriptions")
            .select("id")
            .eq("email", email_ext)
            .eq("seance_id", seance_id)
            .execute()
            .data
        )

        if existe_ext:
            st.error("Vous avez déjà envoyé une préinscription pour cette séance.")
            st.stop()

        # Insertion conforme à ta table Supabase
        supabase.table("preinscriptions").insert({
            "nom": nom,
            "prenom": prenom,
            "email": email_ext,
            "telephone": telephone,

            "chien_nom": chien_nom,
            "chien_race": chien_race,
            "chien_naissance": None,

            "cours_id": None,
            "cours_nom": None,

            "seance_id": seance_id,
            "date_seance": date_seance_value.isoformat(),
            "heure_debut": heure_debut_str,

            "date_preinscription": datetime.date.today().isoformat(),

            "statut": "En attente",
            "traitee": False,
            "acceptee": False,
            "type": "exterieur",

            "chien_id": None,
            "membre_id": None
        }).execute()

        st.success("Préinscription envoyée, merci !")
