# ---------------------------------------------------------
# FLUX EXTÉRIEUR
# ---------------------------------------------------------
if choix == "Personne extérieure":

    st.header("Préinscription extérieur")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    email_ext = st.text_input("Email")
    telephone = st.text_input("Téléphone")

    chien_nom = st.text_input("Nom du chien")
    chien_race = st.text_input("Race du chien")
    # 🔥 Date de naissance retirée
    chien_naissance = None

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

    if seances:
        seance_labels = {
            f"{s['date_seance']} - {s.get('heure_debut','')} - {map_cours.get(s.get('cours_id'),'')}": s["id"]
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
            "chien_naissance": None,  # 🔥 retiré

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
        st.success("Votre préinscription a été envoyée !")
