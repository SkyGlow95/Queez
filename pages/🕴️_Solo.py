import streamlit as st

def mettre_a_jour_classement(score, temps_total):
    # Votre logique pour mettre à jour le classement dans Firestore
    # Exemple :
    user_id = "identifiant_utilisateur"  # Identifiant unique de l'utilisateur
    user_doc = db.collection("rank").document(user_id).get()
    if user_doc.exists:
        db.collection("rank").document(user_id).update({"score": firestore.Increment(score)})
    else:
        db.collection("rank").document(user_id).set({"score": score})

def recuperer_questions(type_question):
    questions = []
    for doc in db.collection("quizzes").where("type", "==", type_question).stream():
        question_data = doc.to_dict()
        bonne_propositions = question_data['propositions'][0]  # Supposer que la première réponse est la bonne
        random.shuffle(question_data['propositions'])  # Mélanger les réponses

        # Identifier l'index de la bonne réponse après mélange
        question_data['bonne_propositions_index'] = question_data['propositions'].index(bonne_propositions)
        questions.append(question_data)
    return questions


MODES_DE_JEU = ["cyber", "litterature", "science", "geographie", "Extrème"]

def mode_solo():
    st.header("Mode Solo")
    display_rankings()
    display_chat()

    if 'en_jeu' not in st.session_state or not st.session_state['en_jeu']:
        mode_choisi = st.selectbox("Choisir un type de quiz", MODES_DE_JEU)
        if st.button("Commencer le quiz"):
            demarrer_quiz(mode_choisi)

    if st.session_state.get('en_jeu', False):
        afficher_question_et_propositions()

def demarrer_quiz(mode_choisi):
    st.session_state['questions'] = recuperer_questions(mode_choisi)
    random.shuffle(st.session_state['questions'])
    st.session_state['current_question_index'] = 0
    st.session_state['score'] = 0
    st.session_state['en_jeu'] = True
    st.session_state['propositions_validee'] = False
    st.session_state['start_time'] = time.time()  # Enregistrer le début du quiz
    st.rerun()

def afficher_question_et_propositions():
    current_index = st.session_state['current_question_index']
    question = st.session_state['questions'][current_index]
    st.subheader(f"Question {current_index + 1}: {question['question']}")

    if 'time_left' not in st.session_state or st.session_state['time_left'] <= 0:
        st.session_state['time_left'] = 30  # Réinitialiser le temps pour la question

    time_container = st.empty()
    time_container.write(f"Temps restant: {st.session_state['time_left']} secondes")
    st.success(f"Score actuel : {st.session_state['score']}")

    if not st.session_state.get('propositions_validee', False):
        if question['points'] == 5:
            choix = st.text_input("Votre réponse :", key=f"propositions_{current_index}")
        else:
            choix = st.radio("Choisissez votre réponse :", question['propositions'], key=f"propositions_{current_index}")

        if st.button("Valider la réponse", key=f"valider_{current_index}"):
            st.session_state['propositions_validee'] = True
            verifier_et_afficher_propositions(question, choix)
    else:
        afficher_bonne_propositions_et_bouton_suivant(question)

    if st.session_state['time_left'] > 1:
        time.sleep(1)
        st.session_state['time_left'] -= 1
        st.rerun()
    if st.session_state['time_left'] == 1:
        st.session_state['propositions_validee'] = True
        passer_a_la_question_suivante()
        st.rerun()
    else:
        st.session_state['propositions_validee'] = True
        passer_a_la_question_suivante()

def verifier_et_afficher_propositions(question, choix):
    bonne_propositions = question['propositions'][question['bonne_propositions_index']]
    if choix.strip().lower() == bonne_propositions.lower():
        st.session_state['score'] += question['points']
        st.success(f"Réponse correcte! {bonne_propositions}")
    else:
        st.error(f"Mauvaise réponse, la bonne réponse était : {bonne_propositions}")

def afficher_bonne_propositions_et_bouton_suivant(question):
    bonne_propositions = question['propositions'][question['bonne_propositions_index']]
    st.write(f"La bonne réponse était : {bonne_propositions}")
    if st.button("Question suivante", key=f"suivante_{st.session_state['current_question_index']}"):
        passer_a_la_question_suivante()

def passer_a_la_question_suivante():
    if st.session_state['current_question_index'] < len(st.session_state['questions']) - 1:
        st.session_state['current_question_index'] += 1
        st.session_state['propositions_validee'] = False
        st.session_state['time_left'] = 30
    else:
        terminer_quiz()

def terminer_quiz():
    temps_total = time.time() - st.session_state['start_time']
    mettre_a_jour_classement(st.session_state['score'], temps_total)
    st.success(f"Quiz terminé. Merci d'avoir participé ! Vous avez pris {temps_total:.2f} secondes.")
    st.button("Retour au choix du mode de jeu", on_click=reset_quiz_state)
    time.sleep(10)
    st.session_state['en_jeu'] = False

def reset_quiz_state():
    for key in ['questions', 'current_question_index', 'score', 'en_jeu', 'propositions_validee', 'start_time', 'time_left']:
        if key in st.session_state:
            del st.session_state[key]
