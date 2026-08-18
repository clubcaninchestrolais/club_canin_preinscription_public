import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Préinscription extérieure")

with st.form("preinscription_form"):
    st.header("Vos informations")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email = st.text_input("E-mail")
    telephone = st.text_input("Téléphone")

    st.header("Votre chien")

    chien_nom = st.text_input("Nom du chien")
    chien_race = st.text_input("Race du chien")

    st.header("Cours souhaité")

    cours_data = supabase.table("cours").select("id, nom").execute()
    cours_list = cours_data.data

    cours_nom_par_id = {c["nom"]: c["id"] for c in cours_list}
    cours_nom = list(cours_nom_par_id.keys())

    cours_choisi_nom = st.selectbox("Choisir un cours", cours_nom)
    cours_choisi_id = cours_nom_par_id[cours_choisi_nom]

    # 🔥 DEBUG : afficher l’ID du cours sélectionné
    st.write("DEBUG - cours_choisi_nom :", cours_choisi_nom)
    st.write("DEBUG - cours_choisi_id :", cours_choisi_id)

    st.header("Séance souhaitée")

    debut = date.today()
    fin = date.today() + timedelta(days=14)

    seances_data = (
        supabase
        .table("cours_seances")
        .select("id, cours_id, date_seance, heure_debut, actif")
        .eq("cours_id", cours_choisi_id)
        .order("date_seance", desc=False)
        .execute()
    )

    seances_raw = seances_data.data

    # 🔥 DEBUG : afficher les séances renvoyées
    st.write("DEBUG - séances brutes :", seances_raw)

    seances_list = []
    for s in seances_raw:
        raw = s["date_seance"]
        try:
            if "T" in raw:
                d = datetime.fromisoformat(raw.replace("Z", "")).date()
            else:
                d = date.fromisoformat(raw)
        except:
            continue

        if debut <= d <= fin:
            seances_list.append(s)

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

    submitted = st.form_submit_button("Envoyer la préinscription")

    if submitted:
        st.success("Préinscription envoyée, merci !")
