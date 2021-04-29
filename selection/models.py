from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class User(AbstractUser):
    is_warden = models.BooleanField(default=False)


class Student(models.Model):
    user = models.OneToOneField(
        User,
        default=None,
        null=True,
        on_delete=models.CASCADE)
    year_choices = [('I','First'),('II', 'Second'), ('III', 'Third'), ('IV', 'Fourth')]
    student_name = models.CharField(max_length=200, null=True)
    father_name = models.CharField(max_length=200, null=True)
    smart_card_id = models.CharField(max_length=20, unique=True, null=True)
    course = models.ForeignKey(
        'Course',
        null=True,
        default=None,
        on_delete=models.CASCADE)
    dob = models.DateField(
        max_length=10,
        help_text="format : YYYY-MM-DD",
        null=True)
    year_of_study = models.CharField(
        choices=year_choices,
        max_length=3,
        default='I',null=True)
    room = models.OneToOneField(
        'Room',
        blank=True,
        on_delete= models.SET_NULL,
        null=True)
    room_allotted = models.BooleanField(default=False)
    no_dues = models.BooleanField(default=False)

    def __str__(self):
        return str(self.smart_card_id)

    def delete(self, *args, **kwargs):
        room_del = Room.objects.filter(student__room=self.room)
        print('pppppppppppppppppppppppppppppppppppppppp')
        for s in room_del:
            s.vacant = True
            s.save()
            print('***********')
        super(Student, self).delete(*args, **kwargs)


class Room(models.Model):
    room_choice = [('D', 'Double Occupancy'), ('T', 'Triple Occupancy'), ('Q', 'Quadruple vacancy'),('A', 'All Double, Quadruple and Triple Occupancy')]
    no = models.CharField(max_length=5)
    name = models.CharField(max_length=10)
    room_type = models.CharField(choices=room_choice, max_length=1, default=None)
    vacant = models.BooleanField(default=False)
    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE)
    repair = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return '%s %s' %(self.name, self.hostel)

    def delete(self, *args, **kwargs):
        stud = Student.objects.filter(room=self)
        print('pppppppppppppppppppppppppppppppppppppppp')
        for s in stud:
            s.room_allotted = False
            s.save()
            print('***********')
        super(Room, self).delete(*args, **kwargs)


class Hostel(models.Model):
    name = models.CharField(max_length=50)
    year_choices = [('I','First'),('II', 'Second'), ('III', 'Third'), ('IV', 'Fourth')]
    year_of_study = models.CharField(
        choices=year_choices,
        max_length=3,
        default=None,null=True)
    course = models.ManyToManyField('Course', default=None, blank=True)
    caretaker = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return self.name


class Course(models.Model):

    code = models.CharField(max_length=100, default=None)
    room_choice = [('D', 'Double Occupancy'), ('T', 'Triple Occupancy'), ('Q', 'Quadruple vacancy'),('A', 'All Double, Quadruple and Triple Occupancy')]
    room_type = models.CharField(choices=room_choice, max_length=1, default='A')

    def __str__(self):
        return self.code


class Warden(models.Model):
    user = models.OneToOneField(
        User,
        default=None,
        null=True,
        on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    hostel = models.ForeignKey('Hostel',default=None,null=True,
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.user.is_warden is False:  # Set default reference
            self.user.is_warden = True
            self.user.save()
        super(Warden, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.is_warden = False
        self.user.save()
        print('pppppppppppppppppppppppppppppppppppppppp')

        super(Warden, self).delete(*args, **kwargs)


class Leave(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=100,blank = False)
    accept = models.BooleanField(default=False)
    reject = models.BooleanField(default=False)
    confirm_time = models.DateTimeField(auto_now_add=True)