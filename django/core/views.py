from django.conf import settings
from django.shortcuts import render, redirect
from core.models import *
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import BadHeaderError, send_mail, EmailMultiAlternatives

import re



# Create your views here.


def home(request):
    """Homepage with identification"""

    if request.method == 'POST':
        
        if request.POST['agent'] and request.POST['wello'] and request.POST['raspberry']:
            agent = Agent.objects.get(registration_number=request.POST['agent'])
            wello = Wello.objects.get(plate_number=request.POST['wello'])
            connected_assistant = ConnectedAssistant.objects.get(serial_number=request.POST['raspberry'])
            
            if agent and wello and connected_assistant:
                connected_assistant.turn_on = True
                connected_assistant.save()

                patrol = Patrol(agent=agent, wello=wello, connected_assistant=connected_assistant)
                patrol.save()

                request.session['patrol_id'] = patrol.id

            return redirect('dashboard')

    return render(request, 'core/home.html')

def get_assistant_status(request, serial_number):
    """Handles get request to start the program"""
    
    if request.method == 'GET':
        connected_assistant = ConnectedAssistant.objects.get(serial_number=serial_number)

        if connected_assistant:
            return HttpResponse(connected_assistant.turn_on)

@csrf_exempt
def set_listenning_status(request, serial_number):
    """Handles get request to set program listenning 
    status in database"""
    
    if request.method == 'GET':
        connected_assistant = ConnectedAssistant.objects.get(serial_number=serial_number)
        
        if connected_assistant:
            connected_assistant.listenning = True
            connected_assistant.save()
            return HttpResponse(connected_assistant.listenning)
    

def dashboard(request):
    context = {}
    patrol_id = request.session.get('patrol_id')
    if patrol_id:
        patrol_obj = Patrol.objects.get(id=patrol_id)
        context['patrol'] = patrol_obj
        #context['detection'] = Detection.objects.get(patrol=patrol_obj).last()
        return render(request, 'core/dashboard.html', context)
    else:
        return redirect('home')

def get_listenning_status(request):
    """Handles get request to set program listenning 
    status in database"""
    patrol_id = request.session.get('patrol_id')
    patrol = Patrol.objects.get(id=patrol_id)
    return HttpResponse(patrol.connected_assistant.listenning)
    

@csrf_exempt
def set_sound_detected(request):
    
    if request.method == 'POST':

        if request.POST['sound_nature'] and request.POST['serial_number']:
            patrol = Patrol.objects.filter(connected_assistant__serial_number=request.POST['serial_number']).last()
            
            if patrol:
                
                detection = Detection(
                    sound_nature = request.POST['sound_nature'],
                    patrol=patrol
                )
                detection.save()

                return HttpResponse(patrol)


def get_sound_detected(request):
    context = {}
    patrol_id = request.session.get('patrol_id')
    print(patrol_id)
    if Detection.objects.filter(patrol=patrol_id):
        last_detection = Detection.objects.filter(patrol=patrol_id,
                                                false_positive=False,
                                                confirmed_by_agent=False).reverse()[0:1]
        data = serializers.serialize("json", last_detection)
    else:
        data = '[]'
    
    return HttpResponse(data, content_type="application/json")
    

@csrf_exempt
def confirm_alert(request, detection_id):

    if Detection.objects.filter(id=detection_id):
        detection = Detection.objects.get(id=detection_id)

        if request.method == 'GET':
            detection.seen_by_agent = True
            detection.save()
        else:
            if request.POST['value']:                
                detection.comment = request.POST['value']
                detection.confirmed_by_agent = True
                identified_code = re.search('\d+',detection.comment).group(0)
                if identified_code and AlertTemplate.objects.filter(alert_code=int(identified_code)):
                    alert_message = AlertTemplate.objects.get(alert_code=int(identified_code)).alert_message
                    receiver = detection.patrol.wello.police_station.email
                    send_mail(
                    "Signalement Alerte : {0}".format(alert_message),
                    alert_message,
                    settings.EMAIL_HOST_USER,
                    [receiver],
                    fail_silently=False)
                                    
                    detection.message_sent = True
                    detection.save()
                
                
                    


    return render(request, 'core/confirm_alert.html')

def cancel_alert(request):
    if request.method == 'POST' and request.POST.get('detection_id'):
        detection_id = request.POST.get('detection_id')
        if Detection.objects.filter(id=detection_id):
            Detection.objects.filter(id=detection_id).update(false_positive=True)
            

    context = {}
    return HttpResponse('Alert deleted')


def backup_call(request):
    context = {}
    return render(request, 'core/confirm_alert.html', context)
