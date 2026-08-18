import streamlit as st
from datetime import date, timedelta
from supabase import create_client, Client

# --- Connexion Supabase ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Préinscription extérieure")

# ---------------------------------------------------------
# FORMULAIRE PUBLIC
# ---------------------------------------------------------

with st.form("preinscription_form"):
    st.header("Vos informations")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("E-mail")
    telephone = st.text_input("Téléphone")

    st.header("Votre chien")

    chien_nom = st.text_input("Nom du chien")
    chien_race = st.text_input("Race du chien")

    # ---------------------------------------------------------
    # CHOIX DU COURS
    # ---------------------------------------------------------

    st.header("Cours souhaité")

    cours_data = supabase.table("cours").select("id, nom").execute()
    cours_list = cours_data.data

    if not cours_list:
        st.error("Aucun cours disponible.")
        st.stop()

    cours_nom_par_id = {c["nom"]: c["id"] for c in cours_list}
    cours_nom = list(cours_nom_par_id.keys())

    cours_choisi_nom = st.selectbox("Choisir un cours", cours_nom)
    cours_choisi_id = cours_nom_par_id[cours_choisi_nom]

    # ---------------------------------------------------------
    # CHOIX DE LA SÉANCE (14 JOURS À VENIR)
    # ---------------------------------------------------------

    st.header("Séance souhaitée")

    debut = date.today()
    fin = date.today() + timedelta(days=14)

    seances_data = (
        supabase
        .table("cours_seances")
        .select("id, date_seance, heure_debut")
        .eq("cours_id", cours_choisi_id)
        .gte("date_seance", debut.isoformat())
        .lte("date_seance", fin.isoformat())
        .execute()
    )

    seances_list = seances_data.data

    if not seances_list:
        st.warning("Aucune séance disponible pour les 14 jours à venir.")
        seance_choisie_id = None
    else:
        seance_label_par_id = {
            f"{s['date_seance']} - {s['heure_debut']}": s["id"]
            for s in seances_list
        }
        seance_labels = list(seance_label_par_id.keys())

        seance_choisie_label = st.selectbox("Choisir une séance", seance_labels)
        seance_choisie_id = seance_label_par_id[seance_choisie_label]

    # ---------------------------------------------------------
    # VALIDATION DU FORMULAIRE
    # ---------------------------------------------------------

    submitted = st.form_submit_button("Envoyer la préinscription")

    if submitted:
        if not nom or not prenom or not email or not telephone or not chien_nom or not chien_race:
            st.error("Veuillez remplir tous les champs obligatoires.")
            st.stop()

        if seance_choisie_id is None:
            st.error("Aucune séance disponible. Réessayez plus tard.")
            st.stop()

        supabase.table("preinscriptions").insert({
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "telephone": telephone,
            "chien_nom": chien_nom,
            "chien_race": chien_race,
            "cours_id": cours_choisi_id,
            "seance_id": seance_choisie_id,
            "date_preinscrip": date.today().isoformat(),
            "statut": "en_attente",
            "traitee": False,
        }).execute()

        st.success("Préinscription envoyée, merci !")
