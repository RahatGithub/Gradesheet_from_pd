from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from .models import GradeSheet
import os
import numpy as np
import pandas as pd
import json


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
        if not li in gradesheet_categories:
            gradesheet_categories.append(li)
    
    return render(request, 'main/upload.html', {'gradesheet_categories':gradesheet_categories})




def batch_view(request, institute, department, session):
    if request.method == "POST":    
        reg_no = request.POST['reg_no']
        print(institute, department, session, reg_no)
        try:
            gradesheet = GradeSheet.objects.get(institute=institute, department=department, session=session, reg_no=reg_no)
            gradesheet.status = True
            gradesheet.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            return HttpResponse("Not found")
    
    students = []
    try:
        gradesheets = GradeSheet.objects.filter(institute=institute, department=department, session=session)
        for gs in gradesheets:
            students.append([gs.reg_no, gs.name, gs.status])
    except:
        pass
        
    context = {'students':students, 'institute':institute, 'department':department, 'session':session}
    
    return render(request, 'main/batch_view.html', context)




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


def gradesheet_view(request, institute, department, session, reg_no):
    try:
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

        # context = {'gradesheet' : gradesheet, 
        #            'session' : session,
        #            'reg_no' : reg_no,
        #            'name' : name }

        return HttpResponse(gradesheet)

    
    except:
        return HttpResponse("Not found...$") 
    
    # ################################################



    # student = Student.objects.get(reg_no=reg_no)
    # session = student.session
    # batch = Batch.objects.get(session=session)
    # batch_no = batch.batch_no
    # student = Student.objects.get(reg_no=reg_no)
    # student_name = student.name

    # gradesheet = list()
    # semester_results = Result.objects.filter(reg_no=reg_no)
    # cumulative_credits, cumulative_point, cumulative_LG = float(
    #     0), float(0), 'NA'   # for the overall result of all semesters
    # inc = 1
    # for result in semester_results:
    #     a_semester = dict()
    #     course_results = json.loads(result.course_results)
    #     course_results_info = list()
    #     this_semester_credits, this_semester_point, this_semester_LG = float(
    #         0), float(0), 'NA'   # for only a particular semester
    #     for cour in course_results.items():
    #         course_info = list()
    #         # pushing the course_code at index=0
    #         course_info.append(cour[0])
    #         course = Course.objects.filter(
    #             batch_no=batch_no, course_code=cour[0]).first()
    #         # pushing the course_title at index=1
    #         course_info.append(course.course_title)
    #         # pushing the course_credits at index=2
    #         course_info.append(course.course_credits)
    #         # pushing the obtained GP at index=3
    #         course_info.append(cour[1]['GP'])
    #         # pushing the obtained LG at index=4
    #         course_info.append(cour[1]['LG'])
    #         # checking if the obtained GP >= 2
    #         if float(course_info[3]) >= 2:
    #             # cumulative_credits += course_credits
    #             this_semester_credits += course_info[2]
    #             # cumulative_point += GP * course_credits
    #             this_semester_point += float(course_info[3]) * course_info[2]
    #         course_results_info.append(course_info)

    #     a_semester['this_semester_name'] = semester_name(inc)
    #     inc += 1
    #     a_semester['this_semester_credits'] = this_semester_credits
    #     a_semester['course_results_info'] = course_results_info

    #     this_semester_GP = round(
    #         (this_semester_point/this_semester_credits), 2)
    #     a_semester['this_semester_GP'] = this_semester_GP

    #     if this_semester_GP == 4.00:
    #         this_semester_LG = "A+"
    #     elif this_semester_GP >= 3.75:
    #         this_semester_LG = "A"
    #     elif this_semester_GP >= 3.50:
    #         this_semester_LG = "A-"
    #     elif this_semester_GP >= 3.25:
    #         this_semester_LG = "B+"
    #     elif this_semester_GP >= 3.00:
    #         this_semester_LG = "B"
    #     elif this_semester_GP >= 2.75:
    #         this_semester_LG = "B-"
    #     elif this_semester_GP >= 2.50:
    #         this_semester_LG = "C+"
    #     elif this_semester_GP >= 2.25:
    #         this_semester_LG = "C"
    #     elif this_semester_GP >= 2.00:
    #         this_semester_LG = "C-"
    #     else:
    #         this_semester_LG = "F"
    #     a_semester['this_semester_LG'] = this_semester_LG

    #     cumulative_credits += this_semester_credits
    #     a_semester['cumulative_credits'] = cumulative_credits
    #     cumulative_point += this_semester_point
    #     cumulative_GP = round((cumulative_point/cumulative_credits), 2)
    #     a_semester['cumulative_GP'] = cumulative_GP

    #     if cumulative_GP == 4.00:
    #         cumulative_LG = "A+"
    #     elif cumulative_GP >= 3.75:
    #         cumulative_LG = "A"
    #     elif cumulative_GP >= 3.50:
    #         cumulative_LG = "A-"
    #     elif cumulative_GP >= 3.25:
    #         cumulative_LG = "B+"
    #     elif cumulative_GP >= 3.00:
    #         cumulative_LG = "B"
    #     elif cumulative_GP >= 2.75:
    #         cumulative_LG = "B-"
    #     elif cumulative_GP >= 2.50:
    #         cumulative_LG = "C+"
    #     elif cumulative_GP >= 2.25:
    #         cumulative_LG = "C"
    #     elif cumulative_GP >= 2.00:
    #         cumulative_LG = "C-"
    #     else:
    #         cumulative_LG = "F"
    #     a_semester['cumulative_LG'] = cumulative_LG

    #     gradesheet.append(a_semester)

    # # for gs in gradesheet:
    # #     print(gs, end="\n\n")

    # li = []
    # a = []
    # for i in range(len(gradesheet)):
    #     if i % 2 == 0:
    #         a = gradesheet[i]
    #     else:
    #         try:
    #             b = []
    #             b.append(a)
    #             b.append(gradesheet[i])
    #             li.append(b)
    #         except:
    #             li.append(a)
    # if len(gradesheet) % 2 == 1:
    #     b = []
    #     b.append(a)
    #     li.append(b)

    # for couple in li:
    #     for single in couple:
    #         print(single)

    # return render(request, 'main/gradesheet_view.html', {'session': session, 'reg_no': reg_no, 'student_name': student_name, 'gradesheet': gradesheet, 'collection': li})





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