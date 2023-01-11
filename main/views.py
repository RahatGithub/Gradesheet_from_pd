from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from .models import GradeSheet
import os
import numpy as np
import pandas as pd
import json

# class Home(TemplateView):
#     template_name = 'home.html'

def upload(request):
    context = {}
    # semesters = []
    if request.method == "POST":
        if request.POST['form_name'] == 'file_upload_form':
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
                    # print('nai')
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
                                one_sem.append(nice)
                            std['results'].append(one_sem)
                    dic[str(students[i]['regi'])] = std
            
            institute = request.POST['institute']
            department = request.POST['department']
            session = request.POST['session']
            for student,info in dic.items():
                print(student, info, end="\n\n")
                reg_no = student 
                name = info['name']
                results = json.dumps(info['results'])
                GradeSheet.objects.create(reg_no=reg_no,
                                        name=name,
                                        institute=institute,
                                        department=department,
                                        session=session,
                                        results=results )
            students = []
            try:
                gradesheets = GradeSheet.objects.filter(institute=institute, department=department, session=session)
                for gs in gradesheets:
                    students.append([gs.reg_no, gs.name])
            except:
                pass
                
            return redirect(f"batch_view/{institute}/{department}/{session}/", {'students':students})
    
    # Dividing the gradesheets into categories based on <institute, department, session>
    gradesheet_category_obj = GradeSheet.objects.values('institute', 'department', 'session')
    gradesheet_categories = list()
    for gs_dict in gradesheet_category_obj:
        gradesheets = GradeSheet.objects.filter(institute=gs_dict['institute'], department=gs_dict['department'], session=gs_dict['session'])
        num_of_gs = len(gradesheets)
        li = [gs_dict['institute'], gs_dict['department'], gs_dict['session'], num_of_gs]        
        if li not in gradesheet_categories:
            gradesheet_categories.append(li)
    
    return render(request, 'main/upload.html', {'gradesheet_categories':gradesheet_categories})



def batch_view(request, institute, department, session):
    students = []
    try:
        gradesheets = GradeSheet.objects.filter(institute=institute, department=department, session=session)
        for gs in gradesheets:
            students.append([gs.reg_no, gs.name])
    except:
        pass
        
    context = {'students':students, 'institute':institute, 'department':department, 'session':session}
    
    return render(request, 'main/batch_view.html', context)



def delete_record(request, institute, department, session):
    # if request.method == 'POST':
    #     if request.POST['form_name'] == 'delete_record_form':
    #         institute = request.POST['institute']
    #         department = request.POST['department']
    #         session = request.POST['session']
    #         records = GradeSheet.objects.filter(institute=institute, department=department, session=session)
    #         for record in records:
    #             record.delete()
    #         print(records)
    #         return redirect("/")

    #     print("not from 'delete_record_form'")
    
    # print("not a post request")
    
    records = GradeSheet.objects.filter(institute=institute, department=department, session=session)
    for record in records:
        record.delete()
    print(records)
    return redirect("/")