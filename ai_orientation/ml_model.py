import re
from collections import Counter

# Base volontairement simple et explicable : mots-clés + conseils d'orientation.
# Elle reste adaptée à un projet Django de cours, sans prétendre remplacer un diagnostic médical.
SPECIALTIES_DATA = {
    'Cardiologie': {
        'icon': '❤️',
        'keywords': 'douleur poitrine thorax oppression palpitations essoufflement souffle coeur cardiaque tachycardie hypertension tension malaise infarctus',
        'description': 'Pour les douleurs thoraciques, palpitations, essoufflement ou problèmes de tension.',
        'advice': 'Consultez rapidement si la douleur thoracique est forte, persistante ou associée à un malaise.'
    },
    'Dermatologie': {
        'icon': '🩹',
        'keywords': 'peau boutons rougeurs demangeaisons eczema acne eruption cutanee taches urticaire psoriasis allergie brulure grain beauté ongle cheveux',
        'description': 'Pour les problèmes de peau, allergies cutanées, acné, eczéma, cheveux ou ongles.',
        'advice': 'Évitez l’automédication si les lésions s’étendent ou s’infectent.'
    },
    'Pédiatrie': {
        'icon': '👶',
        'keywords': 'enfant bebe nourrisson fievre vaccination croissance otite angine toux pediatre developpement diarrhee vomissement pleurs',
        'description': 'Pour les nourrissons, enfants, fièvre, vaccination, croissance et suivi pédiatrique.',
        'advice': 'Chez un nourrisson, une fièvre élevée ou persistante doit être prise au sérieux.'
    },
    'Gynécologie': {
        'icon': '🌸',
        'keywords': 'grossesse regles menstruation uterus ovaires femme contraception fertilite douleur pelvienne pertes cycle retard grossesse sein gynecologique',
        'description': 'Pour le suivi féminin, contraception, grossesse, règles, douleurs pelviennes ou fertilité.',
        'advice': 'En cas de douleur pelvienne intense ou saignement inhabituel, consultez rapidement.'
    },
    'Neurologie': {
        'icon': '🧠',
        'keywords': 'maux tete migraine vertiges convulsions paralysie tremblement epilepsie cerveau neurologique fourmillement memoire perte connaissance',
        'description': 'Pour migraines, vertiges, troubles neurologiques, convulsions, tremblements ou pertes de connaissance.',
        'advice': 'Une faiblesse brutale d’un côté du corps ou une confusion soudaine nécessite une urgence.'
    },
    'Ophtalmologie': {
        'icon': '👁️',
        'keywords': 'yeux oeil vue vision trouble lunettes conjonctivite cataracte glaucome douleur oculaire rougeur flou larme',
        'description': 'Pour les troubles de vision, douleurs oculaires, rougeurs, lunettes ou suivi des yeux.',
        'advice': 'Une baisse brutale de vision doit être évaluée rapidement.'
    },
    'ORL': {
        'icon': '👂',
        'keywords': 'oreille nez gorge angine sinusite rhume audition tonsillite otite laryngite pharyngite rhinite acouphene nez bouche',
        'description': 'Pour les problèmes d’oreille, nez, gorge, sinusite, angine, otite ou audition.',
        'advice': 'Consultez si la fièvre, la douleur ou la gêne respiratoire persiste.'
    },
    'Dentisterie': {
        'icon': '🦷',
        'keywords': 'dent douleur dentaire carie gencive machoire extraction dentiste prothese dents abcès saignement bouche',
        'description': 'Pour douleurs dentaires, caries, gencives, mâchoire, abcès ou soins bucco-dentaires.',
        'advice': 'Un abcès dentaire ou gonflement du visage nécessite une prise en charge rapide.'
    },
    'Médecine générale': {
        'icon': '🩺',
        'keywords': 'fatigue fievre grippe rhume ordonnance generaliste consultation generale bilan sante douleur toux courbature suivi controle',
        'description': 'Pour un premier avis médical, bilan général, symptômes courants ou orientation vers un spécialiste.',
        'advice': 'Le généraliste est souvent le meilleur premier contact si les symptômes sont diffus.'
    },
    'Radiologie': {
        'icon': '🩻',
        'keywords': 'radio scanner irm imagerie radiographie echographie examen radiologique diagnostic image medicale fracture',
        'description': 'Pour les examens d’imagerie médicale : radio, scanner, IRM, échographie.',
        'advice': 'La radiologie intervient généralement sur demande d’un médecin.'
    },
    'Orthopédie': {
        'icon': '🦴',
        'keywords': 'os articulation fracture entorse genou epaule dos hanche ligament muscle traumatisme chute orthopedie douleur articulaire',
        'description': 'Pour douleurs articulaires, fractures, entorses, genou, dos, épaule ou traumatisme.',
        'advice': 'Après une chute avec impossibilité de bouger ou déformation, il faut consulter rapidement.'
    },
    'Pneumologie': {
        'icon': '🫁',
        'keywords': 'respiration asthme toux chronique bronchite poumon pneumonie souffle essoufflement sifflement allergie respiratoire',
        'description': 'Pour asthme, toux chronique, bronchite, essoufflement ou maladies respiratoires.',
        'advice': 'Une difficulté respiratoire importante est un signe d’urgence.'
    },
    'Gastro-entérologie': {
        'icon': '🧬',
        'keywords': 'ventre estomac digestion diarrhee constipation vomissement nausee reflux gastrite colon douleur abdominale foie intestin',
        'description': 'Pour douleurs abdominales, reflux, troubles digestifs, diarrhée, constipation ou vomissements.',
        'advice': 'Consultez vite en cas de douleur abdominale intense, sang dans les selles ou déshydratation.'
    },
    'Psychiatrie': {
        'icon': '💬',
        'keywords': 'anxiete stress depression sommeil insomnie panique tristesse peur trouble humeur psychiatre psychologie mental',
        'description': 'Pour anxiété, stress important, troubles du sommeil, humeur ou suivi psychique.',
        'advice': 'En cas d’idées suicidaires ou de danger immédiat, contactez les urgences.'
    },
    'Endocrinologie': {
        'icon': '⚖️',
        'keywords': 'diabete thyroide hormone poids glycémie soif fatigue endocrine goitre insuline metabolisme',
        'description': 'Pour diabète, thyroïde, hormones, troubles du poids ou métabolisme.',
        'advice': 'Une glycémie très élevée avec malaise doit être prise en charge rapidement.'
    },
}

EMERGENCY_KEYWORDS = {
    'urgence', 'infarctus', 'malaise', 'perte', 'connaissance', 'respirer', 'respiration',
    'paralysie', 'saignement', 'suicide', 'brutale', 'intense', 'grave', 'evanouissement'
}

ACCENTS = str.maketrans('àâäéèêëîïôöùûüç', 'aaaeeeeiioouuuc')


def _tokens(text):
    text = (text or '').lower().translate(ACCENTS)
    return re.findall(r"[a-zA-Z]{2,}", text)


def _urgency_level(tokens):
    token_set = set(tokens)
    hits = sorted(token_set & EMERGENCY_KEYWORDS)
    if len(hits) >= 2:
        return 'Élevée', hits
    if len(hits) == 1:
        return 'À surveiller', hits
    return 'Standard', []


def get_specialty_recommendations(symptom_text, duration='', intensity='', age_group='', top_n=4):
    query_tokens = _tokens(' '.join([symptom_text or '', duration or '', intensity or '', age_group or '']))
    if not query_tokens:
        return {
            'recommendations': [],
            'urgency': 'Standard',
            'urgent_keywords': [],
            'tokens': [],
            'summary': ''
        }

    query = Counter(query_tokens)
    results = []

    for specialty, data in SPECIALTIES_DATA.items():
        key_tokens = set(_tokens(data['keywords']))
        matched_words = sorted([word for word in query if word in key_tokens])
        matched_count = sum(query[word] for word in matched_words)
        if matched_count:
            coverage = matched_count / max(1, len(query_tokens))
            bonus = 8 if intensity in ['moyenne', 'forte'] else 0
            score = min(96, round(28 + coverage * 120 + matched_count * 7 + bonus))
            results.append({
                'specialty': specialty,
                'icon': data['icon'],
                'score': score,
                'matched_words': matched_words[:8],
                'description': data['description'],
                'advice': data['advice'],
            })

    if not results:
        # Fallback pédagogique : si rien n'est détecté, on propose le généraliste.
        data = SPECIALTIES_DATA['Médecine générale']
        results.append({
            'specialty': 'Médecine générale',
            'icon': data['icon'],
            'score': 45,
            'matched_words': [],
            'description': data['description'],
            'advice': 'Décrivez plus précisément vos symptômes ou commencez par un généraliste.',
        })

    results.sort(key=lambda item: item['score'], reverse=True)
    urgency, urgent_hits = _urgency_level(query_tokens)

    return {
        'recommendations': results[:top_n],
        'urgency': urgency,
        'urgent_keywords': urgent_hits,
        'tokens': query_tokens,
        'summary': f"{len(results[:top_n])} spécialité(s) proposée(s) selon les symptômes indiqués."
    }
