from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import *
from django.http import HttpResponse, Http404
from selection.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime,calendar
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Student.objects.create(user=user)
            cd = form.cleaned_data
            print(str(cd))
            current_site = get_current_site(request)
            mail_subject = 'Activate your HMS account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            return render(request, 'reg_form.html', {'form': form})
    else:
        form = UserForm()
        return render(request, 'reg_form.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request, 'email_confirm.html')
    else:
        return HttpResponse('Activation link is invalid!')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password'])
            if user is not None:
                if user.is_warden:
                    return HttpResponse('Invalid Login')
                if user.is_active:
                    login(request, user)
                    return redirect('../student_profile/')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


def warden_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password'])
            print(cd['username'],cd['password'])
            print(user)
            if user is not None:
                if not user.is_warden:
                    return HttpResponse('Invalid Login')
                elif user.is_active:
                    login(request, user)
                    # print('True')
                    # room_list = request.user.warden.hostel.room_set.all()
                    # context = {'rooms': room_list}
                    # return render(request, 'warden.html', context)
                    return redirect('../warden_profile/')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})


def warden_profile(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        elif user.is_active:
            login(request, user)
            print('True')
            room_list = request.user.warden.hostel.room_set.all().order_by('no')
            context = {'rooms': room_list}
            return render(request, 'warden.html', context)
        else:
            return HttpResponse('Disabled account')
    else:
        return HttpResponse('Invalid Login')


def student_profile(request):
    user = request.user
    if user is not None:
        if user.is_warden:
            return HttpResponse('Invalid Login')
        if user.is_active:
            login(request, user)
            student = request.user.student
            return render(request, 'profile.html', {'student': student})
        else:
            return HttpResponse('Disabled account')
    else:
        return HttpResponse('Invalid Login')



@login_required
def edit(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=request.user.student)
        if form.is_valid():
            form.save()
            student = request.user.student
            return render(request, 'profile.html', {'student': student})
        else:
            form = RegistrationForm()
            return render(request, 'edit.html', {'form': form})
    else:
        form = RegistrationForm(instance=request.user.student)
        return render(request, 'edit.html', {'form': form})


@login_required
def select(request):

    if request.method == 'POST':
        if request.user.student.room:
            room_id_old = request.user.student.room_id

        if not request.user.student.no_dues:
            return HttpResponse('You have dues. Please contact your Hostel Caretaker or Warden')
        form = SelectionForm(request.POST, instance=request.user.student)
        if form.is_valid():
            if request.user.student.room_id:
                # stud = form.save(commit=False)
                # print(request.user.student.room_id, stud.room_id)
                request.user.student.room_allotted = True
                r_id_after = request.user.student.room_id
                room = Room.objects.get(id=r_id_after)
                room.vacant = False
                room.save()
                try:
                    room = Room.objects.get(id=room_id_old)
                    room.vacant = True
                    room.save()
                except BaseException:
                    pass
            else:
                request.user.student.room_allotted = False
                try:
                    room = Room.objects.get(id=room_id_old)
                    room.vacant = True
                    room.save()
                except BaseException:
                    pass
            student  = form.save()
            print(student.room_id)
            student = request.user.student
            return render(request, 'profile.html', {'student': student})
    else:
        if not request.user.student.no_dues:
            return HttpResponse('You have dues. Please contact your Hostel Caretaker or Warden')
        form = SelectionForm(instance=request.user.student)
        student_year_of_study = request.user.student.year_of_study
        student_course = request.user.student.course
        if student_course is None:
            return HttpResponse('No Course Selected <br> '
                                '<h3><a href = \'..\edit\' style = "text-align: center; color: Red ;"> Update Profile </a> </h3> ')
        student_room_type = request.user.student.course.room_type
        hostel = Hostel.objects.filter(
            year_of_study=student_year_of_study).order_by('name')
        print(student_year_of_study)
        x = Room.objects.none()
        #if student_room_type == 'A':
            # print(student_room_type)
            # for i in range(len(hostel)):
            #     h_id = hostel[i].id
        #    x = Room.objects.filter(
        #        hostel__id=hostel, room_type=['S','D','T'], vacant=True).order_by('no')

            # x = x | a
       # else:
            # for i in range(len(hostel)):
            #     h_id = hostel[i].id
        x = Room.objects.filter(
            hostel_id__in=hostel,vacant=True).order_by('hostel_id','no')
        print(x)
            # x = x | a
        form.fields["room"].queryset = x
        print('x',x)
        return render(request, 'select_room.html', {'form': form})


def repair(request):
    if request.method == 'POST':
        form = RepairForm(request.POST)
        if form.is_valid() & request.user.student.room_allotted:

            rep = form.cleaned_data['repair']
            room = request.user.student.room
            room.repair = rep
            room.save()
            return HttpResponse('<h3>Complaint Registered</h3> <br> <a href = \'../../student_profile\''
                                ' style = "text-align: center; color: Red ;"> Go Back to Profile </a>')
        elif not request.user.student.room_allotted:
            return HttpResponse('<h3>First Select a Room </h3> <br> <a href = \'../select\''
                                ' style = "text-align: center; color: Red ;"> SELECT ROOM </a> ')

        else:
            form = RepairForm()
            room = request.user.student.room
            return render(request, 'repair_form.html', {'form': form, 'room': room})
    else:
        if not request.user.student.room_allotted:
            return HttpResponse('<h3>First Select a Room </h3> <br> <a href = \'../select\''
                                ' style = "text-align: center; color: Red ;"> SELECT ROOM </a> ')
        else:
            form = RepairForm()
            room = request.user.student.room
            return render(request, 'repair_form.html', {'form': form,'room': room})


# @login_required
def warden_dues(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            students = Student.objects.all()
            return render(request, 'dues.html', {'students': students})
    else:
        return HttpResponse('Invalid Login')


# @login_required
def warden_add_due(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            if request.method == "POST":
                form = DuesForm(request.POST)
                if form.is_valid():
                    student = form.cleaned_data.get('choice')
                    student.no_dues = False
                    student.save()
                    return HttpResponse('Done')
            else:
                form = DuesForm()
                return render(request, 'add_due.html', {'form': form})
    else:
        return HttpResponse('Invalid Login')


# @login_required
def warden_remove_due(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        else:
            if request.method == "POST":
                form = NoDuesForm(request.POST)
                if form.is_valid():
                    student = form.cleaned_data.get('choice')
                    student.no_dues = True
                    student.save()
                    return HttpResponse('Done')
            else:
                form = NoDuesForm()
                return render(request, 'remove_due.html', {'form': form})
    else:
        return HttpResponse('Invalid Login')


def empty_rooms(request):
    user = request.user
    if user is not None:
        if not user.is_warden:
            return HttpResponse('Invalid Login')
        elif user.is_active:
            room_list = request.user.warden.hostel.room_set.filter(vacant=True).order_by('no')
            context = {'rooms': room_list}
            return render(request, 'empty_rooms.html', context)
        else:
            return HttpResponse('Disabled account')
    else:
        return HttpResponse('Invalid Login')


def logout_view(request):
    logout(request)
    return redirect('/')


def hostels(request):
    hostels_all = Hostel.objects.order_by('name')
    return render(request, 'hostels_all.html', {'hostels':hostels_all})


def hostel_detail_view(request, hostel_name):
    try:
        this_hostel = Hostel.objects.get(name=hostel_name)
    except Hostel.DoesNotExist:
        raise Http404("Invalid Hostel Name")
    context = {
        'hostel': this_hostel,
        'rooms': Room.objects.filter(
            hostel=this_hostel).order_by('name')}
    return render(request, 'hostels.html', context)