{'2018331501': 
    {'name': 'Abdullah Al Naseeh', 
     '1': {
         'course': "['CSE-202-3.00-Object Oriented Programming', 'CSE-202-1.5-I dont know the name', 'MATH-201-3.0-vector analysis', 'CSE-401-3.0-Operating System', 'CSE-402-1.5-Operating system sessional']", 
         'obtained': "['4.0', '3.25', '3.5', '4.0', '3.75', '3.75', '3.45']"
        }, 
     '2': {
         'course': "['CSE-101-3.00-intro to programming', 'CSE-102-1.5-C program sessional', 'MATH-101-3.0-differential calculus', 'CSE-105-3.0-Intro to computer science']", 
         'obtained': "['2.75', '3.25', '3.25', '3.5', '3.83', '3.65']"}}, '2018331502': {'name': 'Greebani Paul Shashi', '1': {'course': "['CSE-202-3.00-Object Oriented Programming', 'CSE-202-1.5-I dont know the name', 'MATH-201-3.0-vector analysis', 'CSE-401-3.0-Operating System', 'CSE-402-1.5-Operating system sessional']", 'obtained': "['3.75', '4.0', '3.25', '3.5', '3.75', '3.49', '3.86']"}, '2': {'course': "['CSE-101-3.00-intro to programming', 'CSE-102-1.5-C program sessional', 'MATH-101-3.0-differential calculus', 'CSE-105-3.0-Intro to computer science']", 'obtained': "['3.5', '4.0', '3.5', '3.5', '3.45', '3.59']"}}, '2018331503': {'name': 'Lukman Chowdhury', '1': {'course': "['CSE-202-3.00-Object Oriented Programming', 'CSE-202-1.5-I dont know the name', 'MATH-201-3.0-vector analysis', 'CSE-401-3.0-Operating System', 'CSE-402-1.5-Operating system sessional']", 'obtained': "['3.75', '3.25', '3.25', '3.0', '2.5', '3.5', '3.54']"}, '2': {'course': "['CSE-101-3.00-intro to programming', 'CSE-102-1.5-C program sessional', 'MATH-101-3.0-differential calculus', 'CSE-105-3.0-Intro to computer science']", 'obtained': "['4.0', '3.25', '3.75', '2.75', '3.75', '3.66']"}}}




{
'2018331501' : {
                'name' : 'Abdullah Al Naseeh',
                'results' : [
                                [
                                    {'CSE-101':['Intro to programming', 3.00, 3.75]},  # or a list: ['CSE-101', 'Intro to programming', 3.00, 3.75]
                                    {'CSE-102':['C programming sessional', 1.50, 3.50]}
                                ],
                                [
                                    {'CSE-201':['Intro to programming', 3.00, 3.75]},
                                    {'MATH-203':['C programming sessional', 1.50, 3.50]}
                                ],
                                [
                                    {'CSE-301':['Intro to programming', 3.00, 3.75]},
                                    {'CSE-302':['C programming sessional', 1.50, 3.50]}
                                ]
                            ]
                },
'2018331501' : {
                'name' : 'Abdullah Al Naseeh',
                'results' : [
                                [
                                    {'CSE-101':['Intro to programming', 3.00, 3.75]},
                                    {'CSE-102':['C programming sessional', 1.50, 3.50]}
                                ],
                                [
                                    {'CSE-201':['Intro to programming', 3.00, 3.75]},
                                    {'MATH-203':['C programming sessional', 1.50, 3.50]}
                                ],
                                [
                                    {'CSE-301':['Intro to programming', 3.00, 3.75]},
                                    {'CSE-302':['C programming sessional', 1.50, 3.50]}
                                ]
                            ]
                }
}


from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from .models import GradeSheet
import os
import numpy as np
import pandas as pd

class Home(TemplateView):
    template_name = 'home.html'

def upload(request):
    context = {}
    semesters = []
    if request.method == "POST":
        context['ok'] = True
        sem = 1
        students = []
        # uploded_file = request.FILES['document']
        for uploded_file in request.FILES.getlist('document'):
            uploded_file.read()
            fs = FileSystemStorage()
            name = fs.save(uploded_file.name, uploded_file)
            url = fs.url(name)
            path = './' + url
            df = pd.read_csv(path)
            cols = list(df.columns.values)
            
            for std in range(0, df.shape[0]):
                student = {}
                a_student = list(df.iloc[std])  # taking the whole row as a student
                course = []
                obtained = []
                for i in range(2, len(a_student)):  # playing with data after 'regi no' and 'name', so range starts from 2
                    if (str(a_student[i]) != 'nan'):
                        if i < len(a_student) - 2:
                            course.append(str(cols[i]))
                        obtained.append(str(a_student[i]))
                student['regi'] = str(a_student[0])
                student['name'] = str(a_student[1])
                student['semester'] = str(sem)
                student['course'] = course
                student['obtained'] = obtained
                if os.path.isfile(path):
                    os.remove(path)
                students.append(student)
            sem = sem + 1
        dic = {}
        for i in range(0, len(students)):
            if str(students[i]['regi']) not in dic:
                # print('nai')
                std = {}
                std['name'] = str(students[i]['name'])
                for j in range(0, len(students)):
                    if str(students[j]['regi']) == str(students[i]['regi']):
                        grd = {}
                        grd['course'] = str(students[j]['course'])
                        grd['obtained'] = str(students[j]['obtained'])
                        std[str(students[j]['semester'])] = grd
                dic[str(students[i]['regi'])] = std
            else:
                # print('ache')
                pass
        context['data'] = dic
        # print(dic)
        for student,info in dic.items():
            session=request.POST['session']
            # GradeSheet.objects.create(reg_no=student,
            #                           name=student.name,
            #                           session=session,
            #                           )
            
            print(session)
            print(student)
            print(info['name'])
            print(info)
            # print(dic['course']) #??????????
            
    return render(request, 'main/upload.html', context)

