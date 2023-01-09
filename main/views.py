from django.shortcuts import render
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
            
        context = {'students':students, 'institute':institute, 'department':department, 'session':session}
        
        return render(request, 'main/batch_view.html', context)
    
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


def test(request, institute, department, session, reg_no):    
    institute = institute.replace("_", " ")    # replacing all '_' with <space>
    department = department.replace("_", " ")  # replacing all '_' with <space>
    session = session.replace("_", " ")        # replacing all '_' with <space>
    student_record = GradeSheet.objects.get(institute=institute, department=department, session=session, reg_no=reg_no)
    results = json.loads(student_record.results)
    name = student_record.name
    
    gradesheet = list()
    cumulative_credits, cumulative_point = float(0), float(0)   # for the overall result of all semesters
    for semester_result in results:
        a_semester = dict()
        this_semester_credits, this_semester_point = float(0), float(0)   # for only a particular semester
        course_results = list()
        for cour in semester_result:
            GP = float(cour[3])
            LG = calculate_LG(GP)
            cour.append(LG)
            if GP >= 2:            # checking if the obtained GP >= 2 
                this_semester_credits += float(cour[2])  # cumulative_credits += course_credits
                this_semester_point += GP * float(cour[2])  # cumulative_point += GP * course_credits 
            course_results.append(cour) 
            
        a_semester['course_results'] = course_results
        a_semester['this_semester_credits'] = this_semester_credits
        this_semester_GP = round((this_semester_point/this_semester_credits), 2)
        a_semester['this_semester_GP'] = this_semester_GP
        a_semester['this_semester_LG'] = calculate_LG(this_semester_GP)
        cumulative_credits += this_semester_credits
        a_semester['cumulative_credits'] = cumulative_credits
        cumulative_point += this_semester_point
        cumulative_GP = round((cumulative_point/cumulative_credits), 2)
        a_semester['cumulative_GP'] = cumulative_GP
        a_semester['cumulative_LG'] = calculate_LG(cumulative_GP)
        
        gradesheet.append(a_semester)
            
    return render(request, 'main/gradesheet_view.html', {'session':session, 'reg_no':reg_no, 'student_name':name, 'gradesheet':gradesheet})


def calculate_LG(GP):
    if GP == 4.00 : LG = "A+"
    elif GP >= 3.75 : LG = "A"
    elif GP >= 3.50 : LG = "A-" 
    elif GP >= 3.25 : LG = "B+"
    elif GP >= 3.00 : LG = "B"
    elif GP >= 2.75 : LG = "B-"
    elif GP >= 2.50 : LG = "C+"
    elif GP >= 2.25 : LG = "C"
    elif GP >= 2.00 : LG = "C-" 
    else: LG = "F"
    return LG 