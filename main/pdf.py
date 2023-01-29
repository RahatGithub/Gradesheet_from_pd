from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa 
from .models import GradeSheet
import json


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO() 
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None



def generate_pdf(request, institute, department, session, reg_no):  
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

        context = {'gradesheet' : gradesheet, 
                   'session' : session,
                   'reg_no' : reg_no,
                   'name' : name }
        
        pdf = render_to_pdf('main/old_gradesheet.html')
        
        if pdf:
            response = HttpResponse(pdf, content_type="application/pdf")
            content = "inline; filename=GradeSheet.pdf"
            response['Content-Disposition'] = content 
            return response 
        
        return HttpResponse("Not found")
    
    except:
        return HttpResponse("Not found...") 






def download_pdf(request, institute, department, session, reg_no):
    try:
        institute = institute.replace("_", " ")    # replacing all '_' with <space>
        department = department.replace("_", " ")  # replacing all '_' with <space>
        session = session.replace("_", " ")        # replacing all '_' with <space>
        student_record = GradeSheet.objects.get(institute=institute, department=department, session=session, reg_no=reg_no)
        # ************experimental*********
        student_record.status == True
        student_record.save()
        # *********************************
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
            
        context = {'gradesheet' : gradesheet, 
                'session' : session,
                'reg_no' : reg_no,
                'name' : name }
        
        pdf = render_to_pdf('main/old_gradesheet.html', context)
        
        if pdf:
            response = HttpResponse(pdf, content_type="application/pdf")
            # content = "attachment; filename=.pdf"
            content = "attachment; filename=%s.pdf" %(reg_no)
            response['Content-Disposition'] = content 
            return response 
        
        return HttpResponse("Not found")
    
    except:
        return HttpResponse("Not found")


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