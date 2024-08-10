from django.contrib.auth.decorators import login_required
import datetime
from hashlib import shake_128
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import numpy as np
import pandas as pd
from .models import Appointment, Doctor

slots = ['10am-12pm','12pm-2pm']


drs = ['Dr. Bhurat', 'Dr. Mahajan', 'Dr. Rathod', 'Dr. Deshmukh', 'Dr. Joshi',
       'Dr. Mohalkar', 'Dr. Lomte', 'Dr. Kale', 'Dr. Deodhar', 'Dr. Rathi']
doctors = {
    'Dr. Bhurat': ['Gastrologist', 'MBBS,MD', '11 years', 'gerd', 'chronic' 'cholestatis', 'gastroenteritis'],

    'Dr. Mahajan':  ['Urologist', 'MBBS, MS(Gen.Surgery), M.ch.Urology', '18 years', 'peptic ulcer disease', 'dimorphic hemmorhids(piles)', 'urinary tract infection'],

    'Dr. Rathod': ['Allergist', "Bachelor's Degree,PG diploma in dermatology ", '22 years', 'fungal infection', 'allergy', 'drug reaction'],

    'Dr. Deshmukh': ['Neurology', 'MD-Physician,MBBS', '18 years', 'paralysis ( brain hammorage)', 'varicos veins', 'spondylosis', 'migrane', 'cervical spondylisis', 'migrane'],

    'Dr. Joshi': ['General Physician', 'phD,MSc', '16 years', 'malaria', 'tuberculosis', 'common cold', 'pnemonia', 'jaundice', 'aids', 'bronchial asthama', 'typhoid'],

    'Dr. Mohalkar': ['Neurologist',
                     'MBBS ,MD,Doctorate of medicine in Rheumatology', '19 years', 'osteoarthritis', 'arthritis', 'paromysal positional vertigo'],

    'Dr. Lomte': ['Endocrinologist(Diabetic Specialist)', 'MBBS,MCI(Medical council of India)', '20 years', 'diabetes', 'hypoglycemia', 'hyperthyroidism',
                  'hypothyroidism', 'hypertension', 'Dengue', ],
    'Dr. Kale': ['Skin Specialist', 'Bachelor of science in Dermatology,PostGradute Diploma in Dermatology,master of science in Dertology', '13 years', 'chicken pox', 'acne', 'psoriasis', 'impetigo'],

    'Dr. Deodhar': ['Cardiologist', 'MBBS,MD,DM in cardiology', '22 years', ' heart attack'],

    'Dr. Rathi': ['Orthopaedic', 'MBBS,DNB(Diplomate of Nation Board),DM(Hepatology)', '17 years', 'hepatitis a', 'hepatitis b', 'hepatitis c', 'hepatitis d', 'hepatitis e', 'alcoholic hepatitis']
}
# for ML

l1 = ['itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering', 'chills', 'joint_pain',
      'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_ urination', 'fatigue',
      'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings', 'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat',
      'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration', 'indigestion',
      'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation',
      'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine', 'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload',
      'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation',
      'redness_of_eyes', 'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs', 'fast_heart_rate',
      'pain_during_bowel_movements', 'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps',
      'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails',
      'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech', 'knee_pain', 'hip_joint_pain',
      'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side',
      'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine', 'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
      'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation', 'dischromic _patches',
      'watering_from_eyes', 'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration', 'visual_disturbances',
      'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption',
      'fluid_overload', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
      'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze']

disease = ['Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
           'Peptic ulcer diseae', 'AIDS', 'Diabetes', 'Gastroenteritis', 'Bronchial Asthma', 'Hypertension',
           ' Migraine', 'Cervical spondylosis',
           'Paralysis (brain hemorrhage)', 'Jaundice', 'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
           'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Alcoholic hepatitis', 'Tuberculosis',
           'Common Cold', 'Pneumonia', 'Dimorphic hemmorhoids(piles)',
           'Heartattack', 'Varicoseveins', 'Hypothyroidism', 'Hyperthyroidism', 'Hypoglycemia', 'Osteoarthristis',
           'Arthritis', '(vertigo) Paroymsal  Positional Vertigo', 'Acne', 'Urinary tract infection', 'Psoriasis',
           'Impetigo']

l2 = []
for x in range(0, len(l1)):
    l2.append(0)

df = pd.read_csv('static/datasets/disease_symptoms.csv')
# print(df)


df.replace({'prognosis': {'Fungal infection': 0, 'Allergy': 1, 'GERD': 2, 'Chronic cholestasis': 3, 'Drug Reaction': 4,
                          'Peptic ulcer diseae': 5, 'AIDS': 6, 'Diabetes ': 7, 'Gastroenteritis': 8, 'Bronchial Asthma': 9, 'Hypertension ': 10,
                          'Migraine': 11, 'Cervical spondylosis': 12,
                          'Paralysis (brain hemorrhage)': 13, 'Jaundice': 14, 'Malaria': 15, 'Chicken pox': 16, 'Dengue': 17, 'Typhoid': 18, 'hepatitis A': 19,
                          'Hepatitis B': 20, 'Hepatitis C': 21, 'Hepatitis D': 22, 'Hepatitis E': 23, 'Alcoholic hepatitis': 24, 'Tuberculosis': 25,
                          'Common Cold': 26, 'Pneumonia': 27, 'Dimorphic hemmorhoids(piles)': 28, 'Heart attack': 29, 'Varicose veins': 30, 'Hypothyroidism': 31,
                          'Hyperthyroidism': 32, 'Hypoglycemia': 33, 'Osteoarthristis': 34, 'Arthritis': 35,
                          '(vertigo) Paroymsal  Positional Vertigo': 36, 'Acne': 37, 'Urinary tract infection': 38, 'Psoriasis': 39,
                          'Impetigo': 40}}, inplace=True)

X = df[l1]

y = df[["prognosis"]]
np.ravel(y)


def NaiveBayes(s1, s2, s3, s4, s5):
    from sklearn.naive_bayes import MultinomialNB
    gnb = MultinomialNB()
    gnb = gnb.fit(X, np.ravel(y))
    # s1 = 'itching'
    # s2 = 'shivering'
    # s3 = 'skin_rash'
    # s4 = 'nodal_skin_eruptions'
    # s5 = 'continuous_sneezing'

    psymptoms = [s1, s2, s3, s4, s5]

    for k in range(0, len(l1)):
        for z in psymptoms:
            if(z == l1[k]):
                l2[k] = 1

    inputtest = [l2]
    predict = gnb.predict(inputtest)
    predicted = predict[0]

    h = 'no'
    for a in range(0, len(disease)):
        if(predicted == a):
            h = 'yes'
            break

    if (h == 'yes'):
        # t3.delete("1.0", END)
        # t3.insert(END, disease[a])
        print('predicted : ', disease[a])
        return disease[a]
    else:
        # t3.delete("1.0", END)
        # t3.insert(END, "No Disease")
        print('no disease')
        return 'no disease'


def index(request):
    return render(request, 'index.html')


def contactus(request):
    return render(request, 'contact_us.html')


def submit(request):
    return render(request, 'index.html')


def signin(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request=request, user=user)
            return redirect('home')
        else:
            messages.success(
                request, 'There Was Error Logging In! Please Fill Correct Details')
            return redirect('signupsignin')
    else:
        pass


def signup(request: HttpRequest):
    if request.method == 'POST':

        usr = User.objects.create_user(
            request.POST['username'], request.POST['email'], request.POST['password'])
        messages.success(request, 'Account Created Successfully! Kindly Login')
    return redirect('signupsignin')


def signupsignin(request):
    return render(request, 'signupsignin.html')


@login_required
def schedule(request: HttpRequest):
    # print('done')
    context = {'drs': drs,'slots':slots}
    return render(request, 'schedule.html', context)


@login_required
def predictview(request: HttpRequest):

    context = {'symptoms': l1}
    context['disable'] = 'disabled'
    context['predicted_disease'] = ''
    context['hiddenstatus'] = 'hidden'
    if request.method == 'POST':
        # doctor = Doctor.objects.create(name='Dr. khan')
        # doctor.save()
        # print(doctor)
        s1 = request.POST.get('symptom1')
        s2 = request.POST.get('symptom2')
        s3 = request.POST.get('symptom3')
        s4 = request.POST.get('symptom4')
        s55 = request.POST.get('symptom5')

        # print(s1,s2,s3,s4,s5)
        context['predicted_disease'] = NaiveBayes(s1, s2, s3, s4, s55)
        # print(context['predicted_disease'].lower())
        for key in doctors.keys():
            if context['predicted_disease'].lower() in doctors[key]:
                context['doc_req'] = key
                context['disable'] = ''
                context['hiddenstatus'] = ''

                # print(key)
                break

    return render(request, 'predict.html', context)


def services(request):
    return render(request, 'services.html')


def fordoctorsnext(request: HttpRequest):
    if request.method == "POST":
        sdr = request.POST['suggesteddoctor']
        password = request.POST['password']
        if password == 'pass':

            # apts = Appointment.objects.filter(doctor = sdr)
            apts = Appointment.objects.all()
            fapts = []
            for apt in apts:
                if apt.doctor == sdr:
                    fapts.append(apt)
            context = {'drs': drs, 'apts': fapts}
            print(apts)
            return render(request, 'fordoctors.html', context)
    else:
        return render(request, '/')


def fordoctors(request: HttpRequest):
    context = {'drs': drs}
    return render(request, 'signin.html', context=context)

# def (request):
#     return render(request,)


@login_required
def schedule_apt(request: HttpRequest):
    apt = Appointment(doctor=request.POST['doctor'], patient=request.POST['name'], disease=None,
                      date=request.POST['date'], email=request.POST['email'], phone=request.POST['phone'])
    apt.save()
    messages.success(request, 'Booking Done!')
    return render(request, 'schedule.html')


@login_required
def book(request: HttpRequest, doctor, patient):
    # print('method working',doctor,patient)
    uid = request.user.id
    email = User.objects.get(id=uid)
    apt = Appointment(doctor=doctor, patient=patient, email=email)
    apt.save()
    messages.success(request, 'Booking Done!')
    return render(request, 'services.html')
