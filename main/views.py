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
                a_student = list(df.iloc[std])
                course = []
                obtained = []
                for i in range(2, len(a_student)):
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
                print('nai')
                std = {}
                std['name'] = str(students[i]['name'])
                std['results'] = []
                for j in range(0, len(students)):
                    if str(students[j]['regi']) == str(students[i]['regi']):
                        course = students[j]['course']
                        obtained = students[j]['obtained']
                        one_sem = []
                        for k in range(0, len(course)):
                            cnct = course[k] + '-' + obtained[k]
                            splited = cnct.split('-')
                            nice = []
                            nice.append(splited[0] + '-' + splited[1])
                            nice.append(splited[3])
                            nice.append(splited[2])
                            nice.append(splited[4])
                            print(nice)
                            one_sem.append(nice)
                        std['results'].append(one_sem)
                dic[str(students[i]['regi'])] = std
            else:
                print('ache')
        context['data'] = dic
        # print(dic)
            
        return render(request, 'main/batch_view.html', {'data':dic})
            
    return render(request, 'main/upload.html', context)

