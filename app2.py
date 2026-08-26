import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client

st.write("PAGE ACTIVE : app2.py")

# --- Connexion Supabase ---
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

    # ⭐ Empêcher un membre d'utiliser le flux extérieur
    if email:
        membre_existe = (
            supabase.table("membres")
            .select("id")
            .eq("email", email)
            .execute()
            .data
        )
        if membre_existe:
            st.error("Vous êtes membre du club. Veuillez utiliser le formulaire membre.")
            st.stop()

    st.header("Votre chien")

    chien_nom = st.text_input("Nom du chien")
    chien_race = st.text_input("Race du chien")

    # ---------------------------------------------------------
    # CHOIX DU COURS
    # ---------------------------------------------------------

    st.header("Cours souhaité")

    cours_data = supabase.table("cours").select("id, nom").order("id").execute()
    cours_list = cours_data.data

    cours_options = [(c["nom"], c["id"]) for c in cours_list]
    cours_noms = [c[0] for c in cours_options]

    cours_choisi_nom = st.selectbox("Choisir un cours", cours_noms)
    cours_choisi_id = next(c[1] for c in cours_options if c[0] == cours_choisi_nom)

    # ---------------------------------------------------------
    # CHOIX DE LA SÉANCE
    # ---------------------------------------------------------

    st.header("Séance souhaitée")

    debut = date.today()
    fin = date.today() + timedelta(days=14)

    seances_data = (
        supabase
        .table("cours_seances")
        .select("id, cours_id, date_seance, heure_debut")
        .eq("cours_id", cours_choisi_id)
        .order("date_seance")
        .execute()
    )

    seances_raw = seances_data.data

    seances_list = []
    for s in seances_raw:
        raw = s["date_seance"]
        try:
            d = datetime.fromisoformat(raw.replace("Z", "")).date() if "T" in raw else date.fromisoformat(raw)
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
        if not nom or not prenom or not email or not telephone or not chien_nom or not chien_race:
            st.error("Veuillez remplir tous les champs obligatoires.")
            st.stop()

        if seance_choisie_id is None:
            st.error("Aucune séance disponible. Réessayez plus tard.")
            st.stop()

        # ⭐ Blocage anti-doublon extérieur
        existe_ext = (
            supabase.table("preinscriptions")
            .select("id")
            .eq("email", email)
            .eq("seance_id", seance_choisie_id)
            .execute()
            .data
        )

        if existe_ext:
            st.error("Vous avez déjà envoyé une préinscription pour cette séance.")
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
