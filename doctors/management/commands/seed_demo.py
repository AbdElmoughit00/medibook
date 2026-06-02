from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import CustomUser
from doctors.models import Doctor, Specialty
from schedules.models import Availability

SPECIALTIES = [
    ('Cardiologie', 'Maladies du cœur et de la circulation.', 'coeur, poitrine, palpitations, hypertension, essoufflement'),
    ('Dermatologie', 'Pathologies de la peau, cheveux et ongles.', 'peau, boutons, rougeurs, démangeaisons, acné, allergie'),
    ('Pédiatrie', 'Suivi médical des enfants et nourrissons.', 'enfant, bébé, fièvre, vaccination, croissance'),
    ('Gynécologie', 'Suivi féminin, grossesse, contraception et douleurs pelviennes.', 'grossesse, règles, contraception, fertilité, douleur pelvienne'),
    ('Neurologie', 'Troubles du système nerveux, migraines et vertiges.', 'migraine, vertiges, convulsions, tremblement, mémoire'),
    ('Ophtalmologie', 'Santé des yeux et troubles de la vision.', 'yeux, vision, vue, lunettes, douleur oculaire'),
    ('ORL', 'Oreille, nez, gorge, audition et sinus.', 'oreille, nez, gorge, sinusite, otite, angine'),
    ('Dentisterie', 'Soins dentaires et douleurs bucco-dentaires.', 'dent, carie, gencive, douleur dentaire, abcès'),
    ('Médecine générale', 'Premier avis, bilan de santé et symptômes courants.', 'fatigue, fièvre, grippe, bilan, douleur, toux'),
    ('Radiologie', 'Examens d’imagerie médicale.', 'radio, scanner, irm, échographie, radiographie'),
    ('Orthopédie', 'Os, articulations, fractures, entorses et traumatismes.', 'os, articulation, fracture, entorse, genou, dos'),
    ('Pneumologie', 'Poumons, asthme, toux chronique et respiration.', 'asthme, respiration, toux, poumon, bronchite'),
    ('Gastro-entérologie', 'Appareil digestif, estomac, foie et intestins.', 'ventre, estomac, digestion, diarrhée, reflux, constipation'),
    ('Psychiatrie', 'Santé mentale, anxiété, stress, sommeil et humeur.', 'anxiété, stress, dépression, sommeil, panique'),
    ('Endocrinologie', 'Diabète, thyroïde, hormones et métabolisme.', 'diabète, thyroïde, hormone, poids, glycémie'),
]

DOCTORS = [
    ('amina.bennani', 'Amina', 'Bennani', 'Cardiologie', 'Cabinet Médical Maarif, Casablanca', 12, 'Cardiologue spécialisée dans le suivi de l’hypertension, des palpitations et des douleurs thoraciques.'),
    ('youssef.elidrissi', 'Youssef', 'El Idrissi', 'Dermatologie', 'Centre Santé Agdal, Rabat', 8, 'Dermatologue pour acné, allergies cutanées, eczéma et suivi de la peau.'),
    ('salma.alaoui', 'Salma', 'Alaoui', 'Pédiatrie', 'Clinique Ibn Sina, Tanger', 10, 'Pédiatre pour le suivi des enfants, fièvre, vaccination et croissance.'),
    ('hajar.mansouri', 'Hajar', 'Mansouri', 'Gynécologie', 'Centre Médical Gauthier, Casablanca', 11, 'Gynécologue pour suivi féminin, contraception, grossesse et douleurs pelviennes.'),
    ('omar.berrada', 'Omar', 'Berrada', 'Neurologie', 'Clinique Al Amal, Rabat', 14, 'Neurologue pour migraines, vertiges, tremblements et troubles neurologiques.'),
    ('mehdi.tazi', 'Mehdi', 'Tazi', 'Ophtalmologie', 'Centre Vision, Casablanca', 7, 'Ophtalmologue pour troubles de la vue, douleurs oculaires et contrôle de vision.'),
    ('karim.elalami', 'Karim', 'El Alami', 'ORL', 'Cabinet ORL Médina, Fès', 9, 'Spécialiste ORL pour otites, sinusites, angines, audition et nez-gorge.'),
    ('nora.fassi', 'Nora', 'Fassi', 'Dentisterie', 'Cabinet Dentaire Anfa, Casablanca', 9, 'Dentiste pour douleurs dentaires, caries, gencives et soins préventifs.'),
    ('imad.rachidi', 'Imad', 'Rachidi', 'Médecine générale', 'Centre Santé Atlas, Marrakech', 6, 'Médecin généraliste pour bilan, fièvre, grippe, fatigue et orientation initiale.'),
    ('sara.elkhatib', 'Sara', 'El Khatib', 'Radiologie', 'Centre Imagerie Médicale, Rabat', 13, 'Radiologue pour radiographie, scanner, IRM et échographie.'),
    ('anas.lahlou', 'Anas', 'Lahlou', 'Orthopédie', 'Clinique Orthopédique, Casablanca', 10, 'Orthopédiste pour fractures, entorses, douleurs articulaires, genou et dos.'),
    ('meryem.ouazzani', 'Meryem', 'Ouazzani', 'Pneumologie', 'Centre Respiratoire, Tanger', 8, 'Pneumologue pour asthme, toux chronique, bronchite et essoufflement.'),
    ('adnane.sabri', 'Adnane', 'Sabri', 'Gastro-entérologie', 'Clinique Digestive, Rabat', 12, 'Gastro-entérologue pour douleurs abdominales, reflux, diarrhée et constipation.'),
    ('lina.haddad', 'Lina', 'Haddad', 'Psychiatrie', 'Cabinet Santé Mentale, Casablanca', 7, 'Psychiatre pour anxiété, stress, troubles du sommeil et suivi de l’humeur.'),
    ('samir.boukhari', 'Samir', 'Boukhari', 'Endocrinologie', 'Centre Diabète & Hormones, Rabat', 15, 'Endocrinologue pour diabète, thyroïde, hormones et troubles métaboliques.'),
]


class Command(BaseCommand):
    help = 'Crée des spécialités, médecins et disponibilités de démonstration.'

    @transaction.atomic
    def handle(self, *args, **options):
        specialty_map = {}
        for name, description, keywords in SPECIALTIES:
            sp, _ = Specialty.objects.update_or_create(
                name=name,
                defaults={'description': description, 'keywords': keywords}
            )
            specialty_map[name] = sp

        for username, first_name, last_name, specialty_name, address, years, description in DOCTORS:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@medibook.demo',
                    'role': 'doctor',
                    'phone': '0600000000',
                }
            )
            changed = False
            if not user.first_name:
                user.first_name = first_name
                changed = True
            if not user.last_name:
                user.last_name = last_name
                changed = True
            if user.role != 'doctor':
                user.role = 'doctor'
                changed = True
            if created:
                user.set_password('demo12345')
                changed = True
            if changed:
                user.save()

            doctor, _ = Doctor.objects.update_or_create(
                user=user,
                defaults={
                    'cabinet_address': address,
                    'description': description,
                    'years_experience': years,
                    'is_active': True
                }
            )
            doctor.specialties.add(specialty_map[specialty_name])

            for day in range(0, 5):
                Availability.objects.get_or_create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time='09:00',
                    end_time='12:00',
                    defaults={'slot_duration': 30, 'is_active': True}
                )
                Availability.objects.get_or_create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time='14:00',
                    end_time='17:00',
                    defaults={'slot_duration': 30, 'is_active': True}
                )

        admin, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'MediBook',
                'email': 'admin@medibook.demo',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin12345')
            admin.save()

        patient, created = CustomUser.objects.get_or_create(
            username='patient.demo',
            defaults={
                'first_name': 'Patient',
                'last_name': 'Demo',
                'email': 'patient@medibook.demo',
                'role': 'patient',
                'phone': '0611111111',
            }
        )
        if created:
            patient.set_password('patient12345')
            patient.save()

        self.stdout.write(self.style.SUCCESS(
            f'Données de démonstration créées : {len(SPECIALTIES)} spécialités, {len(DOCTORS)} médecins, 1 patient et 1 admin.'
        ))
