from django.views.generic.base import View
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.db.models import Q, Sum, Count, Max
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from apps.survey.models import QuestionAnswer, Survey, SurveyType, QuestionFile
from apps.questions.models import Option, Question
from apps.accounts.models import User
from apps.farms.models import Farm
from apps.field.models import Field,FieldUpdated,FieldActivity
from apps.processor.models import *
from apps.grower.models import Consultant, Grower
from apps.growersurvey.models import TypeSurvey, QuestionSurvey, OptionSurvey, SustainabilitySurvey, NameSurvey, Evidence, SurveyCsvTable
import json
from apps.growersurvey.models import InputSurvey
from django.db.models import Sum
#from .models import NameSurvey
from django.core import serializers
from urllib.parse import urlparse
import datetime
from django.db.models import Count
from django.db.models import Avg
import csv
from reportlab.pdfgen    import canvas
from reportlab.lib.utils import ImageReader

from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    #context = Context(context_dict)
    html  = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors')

# Create your views here.


class GrowerSurveyView(LoginRequiredMixin, CreateView):
    '''Generic Class Based view of type survey '''
    model = TypeSurvey
    fields = "__all__"
    template_name = 'growersurvey/growers-take-survey.html'
    success_url = reverse_lazy('type-survey')

    def get_context_data(self, **kwargs):
        #print(self.request.user.email)
        grower_id = Grower.objects.get(email=self.request.user.email).id
        farms_list = Farm.objects.filter(grower=grower_id)
        type_survey = TypeSurvey.objects.all()
        context = {'farms_lists': farms_list}
        # print(context)
        context['type_surveys'] = type_survey
        return context


class GrowerSurveyCreate(LoginRequiredMixin, CreateView):
    #model = TypeSurvey
    #fields = "__all__"
    #template_name = 'growersurvey/create-survey.html'
    #success_url = reverse_lazy('create-survey')

    def get(self, request):
        '''Default function for get request'''
        type_survey = TypeSurvey.objects.all()
        year_dropdown = []
        for y in range(2020, (datetime.datetime.now().year + 29)):
            year_dropdown.append(y)

        return render(request, 'growersurvey/create-survey.html', {
            'type_survey': type_survey,
            'year_dropdown': year_dropdown,
        })


class GetQuestion(LoginRequiredMixin, CreateView):

    def get(self, request):
        '''Default function for get request'''
        namesurvey_id = int(request.GET.get('namesurvey_id', 0))
        question_data = QuestionSurvey.objects.filter(
            namesurvey_id=namesurvey_id).order_by('questionorder')
        return render(request, 'growersurvey/get-question.html', {
            'question_data': question_data
        })

def change_qoestion_order(request):
    if request.POST.get('down_arrow_1'):
        question_id = request.POST.get('down_arrow_1')
        namesurvey = request.POST.get('namesurvey_id')
        q_obj = QuestionSurvey.objects.get(pk=question_id)
        q_order = q_obj.questionorder
        obj = QuestionSurvey.objects.filter(namesurvey_id=namesurvey).order_by('questionorder')
        pk_lst = []
        for i in obj:
            get_pk = (i.pk)
            pk_lst.append(get_pk)
        (QuestionSurvey.objects.filter(pk=pk_lst[0])).update(questionorder=q_order+1)
        (QuestionSurvey.objects.filter(pk=pk_lst[1])).update(questionorder=q_order)
        return redirect(request.META['HTTP_REFERER'])
    elif request.POST.get('up_arrow_1'):
        question_id = request.POST.get('up_arrow_1')
        namesurvey = request.POST.get('namesurvey_id')
        q_obj = QuestionSurvey.objects.get(pk=question_id)
        q_order = q_obj.questionorder
        obj = QuestionSurvey.objects.filter(namesurvey_id=namesurvey).order_by('questionorder')
        pk_lst = []
        for i in obj:
            get_pk = (i.pk)
            pk_lst.append(get_pk)
        (QuestionSurvey.objects.filter(pk=pk_lst[-1])).update(questionorder=q_order-1)
        (QuestionSurvey.objects.filter(pk=pk_lst[-2])).update(questionorder=q_order)
        return redirect(request.META['HTTP_REFERER'])
    elif request.POST.get('down_arrow_2'):
        question_id = request.POST.get('down_arrow_2')
        namesurvey = request.POST.get('namesurvey_id')
        q_obj = QuestionSurvey.objects.get(pk=question_id)
        q_order = q_obj.questionorder
        obj = QuestionSurvey.objects.filter(namesurvey_id=namesurvey).order_by('questionorder')
        pk_lst = []
        for i in obj:
            get_pk = (i.pk)
            pk_lst.append(get_pk)
        for i in  range(len(pk_lst)):
            if int(question_id) == pk_lst[i]:
                q_pk_str_id = (i)
        (QuestionSurvey.objects.filter(pk=pk_lst[q_pk_str_id])).update(questionorder=q_order+1)
        (QuestionSurvey.objects.filter(pk=pk_lst[q_pk_str_id+1])).update(questionorder=q_order)
        return redirect(request.META['HTTP_REFERER'])
    elif request.POST.get('up_arrow_2'):
        question_id = request.POST.get('up_arrow_2')
        namesurvey = request.POST.get('namesurvey_id')
        q_obj = QuestionSurvey.objects.get(pk=question_id)
        q_order = q_obj.questionorder
        obj = QuestionSurvey.objects.filter(namesurvey_id=namesurvey).order_by('questionorder')
        pk_lst = []
        for i in obj:
            get_pk = (i.pk)
            pk_lst.append(get_pk)
        for i in  range(len(pk_lst)):
            if int(question_id) == pk_lst[i]:
                q_pk_str_id = (i)
        (QuestionSurvey.objects.filter(pk=pk_lst[q_pk_str_id])).update(questionorder=q_order-1)
        (QuestionSurvey.objects.filter(pk=pk_lst[q_pk_str_id-1])).update(questionorder=q_order)
        return redirect(request.META['HTTP_REFERER'])
    return redirect(request.META['HTTP_REFERER'])

class CheckSurveyStatus(LoginRequiredMixin, CreateView):

    def get(self, request):
        '''Default function for get request'''
        namesurvey_id = int(request.GET.get('survey_year', 0))
        farm_id = int(request.GET.get('farm_id', 0))
        field_id = int(request.GET.get('field_id', 0))
        logged_grower_id = int(request.GET.get('logged_grower_id', 0))
        first_question_id = int(request.GET.get('first_question_id', 0))
        #print('first_question_id',first_question_id)

        check_status_data = SustainabilitySurvey.objects.filter(grower_id=logged_grower_id, namesurvey_id=namesurvey_id, farm_id=farm_id, field_id=field_id)

        if check_status_data.count() > 0:
            status = check_status_data[0].status
            last_question_id = check_status_data[0].last_question_id
            
            last_question_order=QuestionSurvey.objects.get(id=last_question_id).questionorder
            if status == 'completed':
                # do something
                message = "This survey is already completed/closed by you."
                next_question = ""
            else:
                message =""
                #next_question_data = QuestionSurvey.objects.filter(namesurvey_id=namesurvey_id, id__gt=last_question_id).order_by('id')[0:1]
                next_question_data = QuestionSurvey.objects.filter(namesurvey_id=namesurvey_id, questionorder__gt=last_question_order).order_by('questionorder')[0:1]

                if next_question_data.count() > 0:
                    next_question = next_question_data[0].id
                    message =""
                else:
                    message =""
                    next_question = first_question_id
        else:
            message =""
            next_question = first_question_id


        return JsonResponse({'message': message, 'next_question': next_question})


class EditViewQuestionOptions(LoginRequiredMixin, UpdateView):

    def get(self, request):
        '''Default function for get request'''
        question_id = int(request.GET.get('question_id', 0))

        Question_Survey_data = QuestionSurvey.objects.get(id=question_id)
        Option_Survey_data = OptionSurvey.objects.filter(
            questionsurvey_id=question_id).order_by('id')
        Option_Survey_data_count = OptionSurvey.objects.filter(
            questionsurvey_id=question_id).count()

        if Option_Survey_data_count == 0:
            option_count = 1
        else:
            option_count = Option_Survey_data_count

        return render(request, 'growersurvey/get-question-options.html', {
            'Question_Survey_data': Question_Survey_data,
            'Option_Survey_data': Option_Survey_data,
            'Option_Survey_data_count': option_count
        })


class GetAllSurvey(LoginRequiredMixin, ListView):
    def get(self, request):
        '''Default function for get request'''
        survey_data = NameSurvey.objects.all().order_by('id')
        # print(survey_data)
        return render(request, 'growersurvey/survey-listing.html', {
            'survey_data': survey_data
        })


class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    def get(self, request, pk):
        '''Default function for get request'''
        name_survey_data = NameSurvey.objects.get(pk=pk)

        type_survey = TypeSurvey.objects.all()
        year_dropdown = []
        for y in range(2020, (datetime.datetime.now().year + 29)):
            year_dropdown.append(y)

        return render(request, 'growersurvey/update-survey.html', {
            'type_survey': type_survey,
            'year_dropdown': year_dropdown,
            'name_survey_data': name_survey_data,
        })


def CheckSurveyDb(request):
    nmsurv_id = int(request.GET.get('nmsurv_id', 0))
    type_survey = int(request.GET.get('type_survey', 0))
    survey_year = request.GET.get('survey_year', '')

    #print(nmsurv_id)

    if nmsurv_id == 0:
        chk_survey_data = NameSurvey.objects.filter(typesurvey_id=type_survey, surveyyear=survey_year).count()
    else:
        chk_survey_data = NameSurvey.objects.exclude(id=nmsurv_id).filter(typesurvey_id=type_survey, surveyyear=survey_year).count()

    print(chk_survey_data)
    
    return HttpResponse(chk_survey_data)

def get_first_question(request):
    name_survey_id = int(request.GET.get('name_survey_id', 0))\
    #  first_question = QuestionSurvey.objects.filter(namesurvey=name_survey_id)[0]
    first_question = QuestionSurvey.objects.filter(namesurvey=name_survey_id).order_by('questionorder')[0]

    return HttpResponse(first_question.id)


def SurveyDelete(request):
    namesurvey_id = int(request.POST.get('namesurvey_id', 0))
    name_survey = NameSurvey.objects.get(id=namesurvey_id)
    name_survey.delete()
    return HttpResponse(1)


def QuestionDelete(request):
    question_id = int(request.POST.get('question_id', 0))
    Question_Survey = QuestionSurvey.objects.get(id=question_id)
    var = Question_Survey.namesurvey.id
    question_quary_set = QuestionSurvey.objects.filter(namesurvey=var).order_by('questionorder')
    Question_Survey.delete()
    pk_lst = []
    for i in question_quary_set:
        get_pk = (i.pk)
        pk_lst.append(get_pk)
        a = 0
    for i in pk_lst:
        while a <= len(question_quary_set):
            QuestionSurvey.objects.filter(pk=i).update(questionorder=a+1)
            a=a+1
            break
    
    return HttpResponse(1)
    # Question_Survey.delete()
    # sdp code ..



def SaveSurvey(request):
    data = json.loads(request.body)
    type_survey = int(data['type_survey'])
    survey_year = data['survey_year']
    survey_end_date = data['survey_end_date']
    survey_start_date = data['survey_start_date']

    namesurvey = NameSurvey(typesurvey_id=type_survey, surveyyear=survey_year,
                            start_date=survey_start_date, end_date=survey_end_date)
    namesurvey.save()

    try:
        getdata = NameSurvey.objects.filter(
            typesurvey_id=type_survey, surveyyear=survey_year).latest('id')
    except NameSurvey.DoesNotExist:
        getdata = None

    return JsonResponse({'id': getdata.id})

def SaveSurveyEdit(request):
    data = json.loads(request.body)
    nmsurv_id = int(data['nmsurv_id'])
    type_survey = int(data['type_survey'])
    survey_year = data['survey_year']
    survey_end_date = data['survey_end_date']
    survey_start_date = data['survey_start_date']

    print(nmsurv_id)

    namesurvey = NameSurvey(id=nmsurv_id,typesurvey_id=type_survey, surveyyear=survey_year,
                            start_date=survey_start_date, end_date=survey_end_date)
    namesurvey.save()

    try:
        getdata = NameSurvey.objects.filter(
            typesurvey_id=type_survey, surveyyear=survey_year).latest('id')
    except NameSurvey.DoesNotExist:
        getdata = None

    return JsonResponse({'id': getdata.id})


def save_question_option(request):
    mydata = dict(request.POST)
    question = mydata['question'][0]
    selction_type = mydata['selction_type'][0]
    max_score = int(mydata['max_score'][0])
    namesurvey_id = int(mydata['namesurvey_id'][0])
    evidence_requird = mydata.get('evidence_requird', 0)

    if evidence_requird == 0:
        evidence_requird_chk = False
        evidence_descr_chk = ""
    else:
        evidence_requird_chk = True
        evidence_descr_chk = mydata['evidence_descr'][0]

    try:
        get_max_order = QuestionSurvey.objects.filter(
            namesurvey_id=namesurvey_id).aggregate(Max('questionorder'))
        get_max_order_number = get_max_order['questionorder__max']
    except QuestionSurvey.DoesNotExist:
        get_max_order_number = None

    if get_max_order_number:
        get_next_order_to_db = get_max_order_number + 1
    else:
        get_next_order_to_db = 1

    Question_Survey = QuestionSurvey(questionname=question, namesurvey_id=namesurvey_id, questiontotalscore=max_score,
                                     questionorder=get_next_order_to_db, selection_type=selction_type, evidence_requird=evidence_requird_chk, evidence_descr=evidence_descr_chk)
    Question_Survey.save()

    inserted_question = QuestionSurvey.objects.latest('id')
    inserted_question_id = inserted_question.id

    # OptionSurvey
    option_name = mydata['option_name']
    points = mydata['points']

    for counter, opt in enumerate(option_name):
        Option_Survey = OptionSurvey(
            optionname=opt, questionsurvey_id=inserted_question_id, optionscore=points[counter])
        Option_Survey.save()

    return HttpResponse(namesurvey_id)


def SaveQuestionOptionEdit(request):
    mydata = dict(request.POST)
    question_id_edit = int(mydata['question_id_edit'][0])
    # Question_Survey = QuestionSurvey.objects.get(id=question_id_edit)
    # Question_Survey.delete()

    namesurvey_id_edit = int(mydata['namesurvey_id_edit'][0])
    question_edit = mydata['question_edit'][0]
    selction_type_edit = mydata['selction_type_edit'][0]
    max_score_edit = int(mydata['max_score_edit'][0])

    evidence_requird_edit = mydata.get('evidence_requird_edit', 0)

    if evidence_requird_edit == 0:
        evidence_requird_chk = False
        evidence_descr_chk = ""
    else:
        evidence_requird_chk = True
        evidence_descr_chk = mydata['evidence_descr_edit'][0]

    # try:
    #     get_max_order = QuestionSurvey.objects.filter(namesurvey_id=namesurvey_id_edit).aggregate(Max('questionorder'))
    #     get_max_order_number = get_max_order['questionorder__max']
    # except QuestionSurvey.DoesNotExist:
    #     get_max_order_number = None

    # if get_max_order_number:
    #     get_next_order_to_db = get_max_order_number + 1
    # else:
    #     get_next_order_to_db = 1

    get_cur_order = QuestionSurvey.objects.get(id=question_id_edit)

    Question_Survey = QuestionSurvey(id=question_id_edit, questionname=question_edit, namesurvey_id=namesurvey_id_edit, questiontotalscore=max_score_edit,
                                     questionorder=get_cur_order.questionorder, selection_type=selction_type_edit, evidence_requird=evidence_requird_chk, evidence_descr=evidence_descr_chk)
    Question_Survey.save()

    # inserted_question = QuestionSurvey.objects.latest('id')
    # inserted_question_id = inserted_question.id

    inserted_question_id = question_id_edit

    option_delete = OptionSurvey.objects.filter(
        questionsurvey_id=inserted_question_id)
    option_delete.delete()

    # OptionSurvey
    #option_id_edit = int(mydata['option_id_edit'])
    option_name_edit = mydata['option_name_edit']
    points_edit = mydata['points_edit']

    for counter, opt in enumerate(option_name_edit):
        Option_Survey = OptionSurvey(
            optionname=opt, questionsurvey_id=inserted_question_id, optionscore=points_edit[counter])
        Option_Survey.save()

    return HttpResponse(namesurvey_id_edit)


class GrowerSurveyQuestionsView(LoginRequiredMixin, CreateView):
    '''Generic Class Based view for question survey '''
    model = QuestionSurvey
    fields = "__all__"
    template_name = 'growersurvey/growers-take-survey-questions.html'
    success_url = reverse_lazy('type-questions')

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        print(pk)
        frmid = self.kwargs.get('frmid')
        fldid = self.kwargs.get('fldid')
        nmsrvid = self.kwargs.get('nmsrvid')

        # getting URL ID

        context = super(GrowerSurveyQuestionsView,self).get_context_data(**kwargs)
                        
        questionnewid = pk
        context["questionnewid"] = pk
        namesurvey_id = nmsrvid
        context["namesurvey_id"] = namesurvey_id
        # for survey type name

        survey_data = NameSurvey.objects.get(id=namesurvey_id)
        context["surveytypename"] = survey_data.typesurvey
        context["surveyyear"] = survey_data.surveyyear
        context["total_questions"] = QuestionSurvey.objects.filter(namesurvey=namesurvey_id).count()

        # data0 = QuestionSurvey.objects.raw(
        #     "select id,name from growersurvey_typesurvey where id=1")
        # sname_ids = [id.id for id in data0]
        # sname_names = [id.name for id in data0]
        # surveytypename = sname_names[0]
        # context["surveytypename"] = surveytypename

        # data1 = QuestionSurvey.objects.raw(
        #     "select * from growersurvey_namesurvey where typesurvey_id=%s", (sname_ids))
        # syear_ids = [id.surveyyear for id in data1]
        # surveyyear = syear_ids[0]
        # context["surveyyear"] = surveyyear

        # for question name, order and id
        # data = QuestionSurvey.objects.raw("select * from growersurvey_questionsurvey where namesurvey_id=%s and id=%s order by id ASC limit 0,1", (namesurvey_id, questionnewid))

        data = QuestionSurvey.objects.filter(id=questionnewid, namesurvey_id=namesurvey_id)[0:1]
        
        question_ids = [id.id for id in data]
        question_names = [id for id in data]
        
        
        options = OptionSurvey.objects.filter(
            questionsurvey_id__in=question_ids)
        context["question_names"] = question_names[0]
        context["option"] = options

        if self.request.user.is_superuser:
            context['logged_grower_id'] = ""
        elif self.request.user.is_consultant:
            context['logged_grower_id'] = ""
        else:
            context['logged_grower_id'] = Grower.objects.get(
                email=self.request.user.email).id
        # print(context['logged_grower_id'])

        # for next question ID
        # data2 = QuestionSurvey.objects.raw("select * from growersurvey_questionsurvey where namesurvey_id=%s and id>%s order by id ASC limit 0,1", (namesurvey_id, question_ids[0]))
        
        # Testing..
        que = QuestionSurvey.objects.get(id =question_ids[0])
        q_order = que.questionorder
      
        all_question = QuestionSurvey.objects.filter(namesurvey_id=namesurvey_id).order_by('questionorder')
       
        pk=[]
        for i in all_question:
            var = i.id
            pk.append(var)

        # ...........
        
        # data2 = QuestionSurvey.objects.filter(id__gt=question_ids[0],namesurvey_id=namesurvey_id).order_by('questionorder')[0:1]
        data2 = QuestionSurvey.objects.filter(questionorder__gt=q_order,namesurvey_id=namesurvey_id).order_by('questionorder')[0:1]
    
        question2_ids = [id.id for id in data2]
        if(question2_ids):
            # nextquestion= QuestionSurvey.objects.filter(questionorder__gt=q_order,namesurvey_id=namesurvey_id).order_by('questionorder')[0:1]
            # print(nextquestion)
            nextquestion = question2_ids[0]
            context["nextquestion"] = nextquestion
            # code
            # next_q = QuestionSurvey.objects.get(id = question2_ids[0])
            # next_q_order = next_q.questionorder
        else:
            context["nextquestion"] = ""

        context["growersurvey_farm_id"] = frmid
        context["growersurvey_feild_id"] = fldid
        growersurvey_farm_names = Farm.objects.filter(id=frmid)
        growersurvey_field_names = Field.objects.filter(id=fldid)

        context["growersurvey_farm_name"] = growersurvey_farm_names
        context["growersurvey_field_name"] = growersurvey_field_names
        

        return context


def InsertoptValue(request):
    evidence_requird= request.POST['evidence_requird']
    uploaded_files = request.FILES.getlist('file')
    growerid_val= request.POST['growerid']
    question_id_val= request.POST['question_id']
    optionvalue_val= request.POST['optionvalue']
    option_id = request.POST['option_id']
    namesurvey_id_val= request.POST['namesurvey_id']
    nextquestionid_val= request.POST['nextquestionid']
    growersurvey_farm_id_val= request.POST['growersurvey_farm_id']
    growersurvey_feild_id_val= request.POST['growersurvey_feild_id']
    questionspkvalue= request.POST['questionspkvalue']

    questionspkvalue = int(questionspkvalue)
    # print(questionspkvalue)
    status = request.POST['status']
    save_status = int(request.POST['save_status'])

    check_input_survey = InputSurvey.objects.filter(grower_id=growerid_val,namesurvey_id=namesurvey_id_val,farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val, questionsurvey_id=question_id_val)

    # print(check_input_survey[0])

    if check_input_survey.count() == 0:
        inputsurvey = InputSurvey(optionscore=optionvalue_val, questionsurvey_id=question_id_val, grower_id=growerid_val, 
        namesurvey_id=namesurvey_id_val, farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val, status=status, 
        optionscore_ids=option_id)
        inputsurvey.save()
        print("inputsurvey1",inputsurvey)
        gid = growerid_val
        gna = Grower.objects.get(id=growerid_val).name
        fid = growersurvey_feild_id_val
        fna = Field.objects.get(id=growersurvey_feild_id_val).name
        crop = Field.objects.get(id=growersurvey_feild_id_val).crop
        fmid = growersurvey_farm_id_val
        fmname = Farm.objects.get(id=growersurvey_farm_id_val).name
        namesurvey_id = namesurvey_id_val
        survey_nameeee = NameSurvey.objects.get(id=namesurvey_id_val).typesurvey.id
        type_name = TypeSurvey.objects.get(id=survey_nameeee).name
        survey_name = f"{type_name} - 2022"
        question_name = QuestionSurvey.objects.get(id=question_id_val).questionname
        ans_id = option_id
        if ans_id :
            var_split = option_id.split(',')              
            answ = OptionSurvey.objects.filter(id__in=var_split)
            answ_w = [j.optionname for j in answ]
            ans_name = str(answ_w)[1:-1]
        else:
            ans_name = ""
        ans_score = optionvalue_val
        attachment = QuestionSurvey.objects.get(id=question_id_val).evidence_requird
        status = status
        created_date = inputsurvey.created_date.strftime("%m/%d/%y")
       
        sur_tab = SurveyCsvTable(grower_id=gid,grower_idd=gid,grower_namee=gna,field_id=fid,field_idd=fid,field_namee=fna,farm_id=fmid,farm_idd=fmid,
        farm_namee=fmname,namesurvey_id=namesurvey_id,survey_name=survey_name,question_name=question_name,ans_name=ans_name,ans_score=ans_score,
        attachment=attachment,status=status,created_date=created_date,crop=crop)
        sur_tab.save()
        print("sur_tab1",sur_tab)
        
    else:
        input_survey_id = check_input_survey[0].id
        inputsurvey = InputSurvey(id=input_survey_id, optionscore=optionvalue_val, questionsurvey_id=question_id_val, 
        grower_id=growerid_val, namesurvey_id=namesurvey_id_val, farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val, 
        status=status, optionscore_ids=option_id)
        inputsurvey.save()
        print("inputsurvey2",inputsurvey)
        gid = growerid_val
        gna = Grower.objects.get(id=growerid_val).name
        fid = growersurvey_feild_id_val
        fna = Field.objects.get(id=growersurvey_feild_id_val).name
        crop = Field.objects.get(id=growersurvey_feild_id_val).crop
        fmid = growersurvey_farm_id_val
        fmname = Farm.objects.get(id=growersurvey_farm_id_val).name
        namesurvey_id = namesurvey_id_val
        survey_nameeee = NameSurvey.objects.get(id=namesurvey_id_val).typesurvey.id
        type_name = TypeSurvey.objects.get(id=survey_nameeee).name
        survey_name = f"{type_name} - 2022"
        question_name = QuestionSurvey.objects.get(id=question_id_val).questionname
        ans_id = option_id
        if ans_id :
            var_split = ans_id.split(',')              
            answ = OptionSurvey.objects.filter(id__in=var_split)
            answ_w = [j.optionname for j in answ]
            ans_name = str(answ_w)[1:-1]
        else:
            ans_name = ""
        ans_score = optionvalue_val
        attachment = QuestionSurvey.objects.get(id=question_id_val).evidence_requird
        status = status
        created_date = inputsurvey.created_date.strftime("%m/%d/%y")
       
        sur_tab = SurveyCsvTable(grower_id=gid,grower_idd=gid,grower_namee=gna,field_id=fid,field_idd=fid,field_namee=fna,farm_id=fmid,farm_idd=fmid,
        farm_namee=fmname,namesurvey_id=namesurvey_id,survey_name=survey_name,question_name=question_name,ans_name=ans_name,ans_score=ans_score,
        attachment=attachment,status=status,created_date=created_date,crop=crop)
        sur_tab.save()
        print("sur_tab2",sur_tab)
    del_eve_file = Evidence.objects.filter(inputsurvey_id=inputsurvey.id)
    del_eve_file.delete()


    for evd_file in uploaded_files:
        set_evd_files = Evidence(inputsurvey_id=inputsurvey.id, file=evd_file)
        set_evd_files.save()
    


    

    #opt_score_minor = InputSurvey.objects.filter(namesurvey_id=namesurvey_id_val,grower_id=growerid_val).latest('id')[:8]
    # print(opt_score_minor)
    #optionscore_val_sum = opt_score_minor.aggregate(Sum('optionscore'))
    #opscoresum = optionscore_val_sum['optionscore__sum']

    # if nextquestionid_val == "":
    #     actual_status = 'completed'
    # else:
    #     actual_status = status

    last_eight = InputSurvey.objects.filter(namesurvey_id=namesurvey_id_val, grower_id=growerid_val, farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val)
    optionscore_val_sum = last_eight.aggregate(Sum('optionscore'))
    # print(len(last_eight))
    opscoresum = optionscore_val_sum['optionscore__sum']
    # print(opscoresum)

    totalscore_val_sum = QuestionSurvey.objects.filter(
        namesurvey_id=namesurvey_id_val).aggregate(Sum('questiontotalscore'))
    totalscoresum = totalscore_val_sum['questiontotalscore__sum']
    # print(totalscoresum)

    suspercentage_calc = (opscoresum/totalscoresum)*100
    suspercentage = round(suspercentage_calc, 0)

    chk_sustainabilitysurvey = SustainabilitySurvey.objects.filter(farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val, grower_id=growerid_val, namesurvey_id=namesurvey_id_val)
    
    if chk_sustainabilitysurvey.count() == 0:

        sustainabilitysurvey = SustainabilitySurvey(surveyscore=opscoresum, totalscore=totalscoresum, sustainabilityscore=suspercentage, farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val, grower_id=growerid_val, namesurvey_id=namesurvey_id_val, status=status, last_question_id=question_id_val)
        sustainabilitysurvey.save()

    else:
        sustainabilitysurvey_id = chk_sustainabilitysurvey[0].id
        sustainabilitysurvey = SustainabilitySurvey(id=sustainabilitysurvey_id, surveyscore=opscoresum, totalscore=totalscoresum, sustainabilityscore=suspercentage, farm_id=growersurvey_farm_id_val, field_id=growersurvey_feild_id_val, grower_id=growerid_val, namesurvey_id=namesurvey_id_val, status=status, last_question_id=question_id_val)
        sustainabilitysurvey.save()

    if save_status > 0:
        grower_data = Grower.objects.get(id=growerid_val)
        survey_type_data = NameSurvey.objects.get(id=namesurvey_id_val)
        type_survey_data = TypeSurvey.objects.get(id=survey_type_data.typesurvey_id)
        if suspercentage > 100 :
            suspercentage = 100
        else:
            suspercentage = suspercentage
        return JsonResponse({'status': True, 'grower_name': grower_data.name, 'survey_type_name': type_survey_data.name, 'survey_year': survey_type_data.surveyyear, 'suspercentage': suspercentage, 'exit_status': save_status})

    return JsonResponse({'status': True, 'exit_status': save_status})


class GrowerSurveyResultScore(LoginRequiredMixin, CreateView):
    model = SustainabilitySurvey
    fields = "__all__"
    template_name = 'growersurvey/growers-sustain-result.html'

    def get_context_data(self, **kwargs):
        context = super(GrowerSurveyResultScore,
                        self).get_context_data(**kwargs)

        if self.request.user.is_superuser:
            context['logged_grower_id'] = ""
            growerId = ""

        elif self.request.user.is_consultant:
            context['logged_grower_id'] = ""
            growerId = ""
        else:
            growerId = Grower.objects.get(email=self.request.user.email).id
            context['logged_grower_id'] = growerId
            # print(growerId)

            #"select * from growersurvey_sustainabilitysurvey where grower_id=%s", (46)
        try:
            data = SustainabilitySurvey.objects.filter(
                grower_id=growerId).latest('id')
        except SustainabilitySurvey.DoesNotExist:
            data = None

        # print(data)
        #sustaindata = [id.surveyscore for id in data]
        # surveyscorefinal=sustaindata[0]

        if(data):
            sustainabilityscorefinal = data.sustainabilityscore
            namesurvey_id = data.namesurvey_id
            # print(namesurvey_id)
            #survey_type_data = TypeSurvey.objects.get(id=namesurvey_id)
            #year_data = NameSurvey.objects.filter(typesurvey=namesurvey_id)

            survey_data = NameSurvey.objects.get(id=namesurvey_id)

            grower_data = Grower.objects.get(id=growerId)
            context["survey_year"] = survey_data.surveyyear
            context["survey_name"] = survey_data.typesurvey
            context["grower_name"] = grower_data.name
            context["sustainabilityscorefinal"] = sustainabilityscorefinal
            farmfield = SustainabilitySurvey.objects.filter(
                grower_id=growerId).latest('id')
            # print(farmfield)
            farmnamevar = farmfield.farm_id
            fieldnamevar = farmfield.field_id
            growersurvey_farm_names = Farm.objects.filter(id=farmnamevar)
            growersurvey_field_names = Field.objects.filter(id=fieldnamevar)
            context["growersurvey_farm_name"] = growersurvey_farm_names
            context["growersurvey_field_name"] = growersurvey_field_names
            context["hasdata"] = True
        else:
            context["hasdata"] = False

        return context


def SurveytypeGetyear(request):
    some_date = datetime.date.today()
    Survey_Type_ID = request.GET.get('surveyTypeid')
    name_survey = NameSurvey.objects.filter(typesurvey=Survey_Type_ID, start_date__lte=some_date, end_date__gte=some_date)
    name_survey_data = [(data.surveyyear, data.id) for data in name_survey]
    return JsonResponse({'status': True, 'data': name_survey_data})


def SurveytypeGetfarm(request):
    grower_id = Grower.objects.get(email=request.GET.get('auth_user')).id
    farm_ID = request.GET.get('farmTypeid')
    field_list = Field.objects.filter(farm=farm_ID).filter(grower=grower_id)
    field_lists = [(data.name, data.id) for data in field_list]
    # print(field_lists)
    return JsonResponse({'status': True, 'data': field_lists})

class GetAllFarm(LoginRequiredMixin, ListView):
    def get(self, request):
        '''Default function for get request'''
        grower_id = int(request.GET.get('grower_id', 0))
        farm_data = Farm.objects.filter(grower_id=grower_id)
        farm_list = [(farm.name, farm.id) for farm in farm_data]

        return JsonResponse({'farm_list': farm_list})

class GetAllField(LoginRequiredMixin, ListView):
    def get(self, request):
        '''Default function for get request'''
        farm_id = int(request.GET.get('farm_id', 0))
        field_data = Field.objects.filter(farm_id=farm_id)
        field_list = [(field.name, field.id) for field in field_data]

        return JsonResponse({'field_list': field_list})

class GrowerSustainabilty(LoginRequiredMixin, ListView):
    def get(self, request):
        '''Default function for get request'''

        # survey_year_list = NameSurvey.objects.all()

        survey_year_list = (NameSurvey.objects.values('surveyyear').annotate(dcount=Count('surveyyear')).order_by())

        survey_year_data = NameSurvey.objects.all()
        survey_type = []
        survey_score_data = []
        line_survey_grower_arr = []

        survey_current_year_data = NameSurvey.objects.filter(surveyyear=datetime.datetime.now().year)
        # print(survey_current_year_data)
        
        if 'Grower' in request.user.get_role() and not request.user.is_superuser:
            # do something grower
            
            grower_id=request.user.grower.id
            get_growers = Grower.objects.filter(id=grower_id).order_by('name')
        
            for name_survey in survey_year_data:
                survey_type.append(name_survey.typesurvey.name)
                sustain_data = SustainabilitySurvey.objects.filter(grower__in=get_growers,namesurvey=name_survey)
                if sustain_data.count() > 0:
                    Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                    Avg_Percentage_Score = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                else:
                    Avg_Percentage_Score = 0
                
                survey_score_data.append(Avg_Percentage_Score)
                
        else:
            if request.user.is_consultant:
                # do something consultant
                consultant_id = Consultant.objects.get(email= request.user.email).id
                get_growers = Grower.objects.filter(consultant=consultant_id).order_by('name')

                for name_survey in survey_year_data:
                    survey_type.append(name_survey.typesurvey.name)
                    sustain_data = SustainabilitySurvey.objects.filter(grower__in=get_growers,namesurvey=name_survey)

                    if sustain_data.count() > 0:
                        Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                        Avg_Percentage_Score = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                    else:
                        Avg_Percentage_Score = 0

                    survey_score_data.append(Avg_Percentage_Score)

            else:
                # do something allpower
                get_growers = Grower.objects.all().order_by('name')

                for name_survey in survey_year_data:
                    survey_type.append(name_survey.typesurvey.name)
                    sustain_data = SustainabilitySurvey.objects.filter(grower__in=get_growers,namesurvey=name_survey)

                    if sustain_data.count() > 0:
                        Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                        Avg_Percentage_Score = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                    else:
                        Avg_Percentage_Score = 0

                    survey_score_data.append(Avg_Percentage_Score)

                    # line_survey_grower_object = sustain_data.annotate(dcount=Count('grower_id')).order_by()
                    # line_survey_grower_list = [grw_data.grower.name for grw_data in line_survey_grower_object]
                    # print(line_survey_grower_list)

        
        # survey_type.append('')
        # survey_score_data.append(0)
        


        var = survey_score_data
        # For Rice
        r1 = var[0]
        r2 = var[2]
        r3 = var[5]
        # For Cotton
        r4 = var[1]
        r5 = var[3]
        r6 = var[4]

        composite_s = round((r1 * 0.3) + (r2 * 0.68) + (r3 * 0.02) + (r4 * 0.3) + (r5 * 0.68) + (r6 * 0.02),2)
    
        return render(request, 'growersurvey/sustainability-dashboard.html', {
            'get_growers': get_growers,
            'survey_year_list': survey_year_list,
            'survey_type': survey_type,
            'survey_score_data': survey_score_data,
            'line_survey_grower_list': '',
            'composite_s':composite_s,
        })

class GetSustainabilityResult(LoginRequiredMixin, ListView):
    def get(self, request):
        '''Default function for get request'''
        
        apply_growers = int(request.GET.get('apply_growers', 0))
        apply_farm = int(request.GET.get('apply_farm', 0))
        apply_field = int(request.GET.get('apply_field', 0))
        apply_year = int(request.GET.get('apply_year', 0))
        
        try:
            name_survey_data = NameSurvey.objects.filter(surveyyear=apply_year)
            name_survey_ids = [name_survey.id for name_survey in name_survey_data]
            type_survey_data = [name_survey_type.typesurvey for name_survey_type in name_survey_data]
        except NameSurvey.DoesNotExist:
            name_survey_ids = []
            type_survey_data = []

        try:
            sustain_data = SustainabilitySurvey.objects.filter(grower_id=apply_growers, farm_id=apply_farm, field_id=apply_field, namesurvey_id__in=name_survey_ids)
            conpleted_name_survey_ids = [comp_name_survey.namesurvey_id for comp_name_survey in sustain_data]
        except SustainabilitySurvey.DoesNotExist:
            conpleted_name_survey_ids = []

        completed_input_survey_data = InputSurvey.objects.filter(grower_id=apply_growers, farm_id=apply_farm, field_id=apply_field, namesurvey_id__in=conpleted_name_survey_ids)

        # type_survey_data = TypeSurvey.objects.all().order_by('name')

        # print(type_survey_data)
        grower_data = Grower.objects.get(id=apply_growers)
        farm_data = Farm.objects.get(id=apply_farm)
        field_data = Field.objects.get(id=apply_field)

        return render(request, 'growersurvey/get-question-answer-marks.html', {
            'completed_input_survey_data': completed_input_survey_data,
            'type_survey_data': type_survey_data,
            'grower_data': grower_data,
            'farm_data' : farm_data,
            'field_data': field_data,
            'apply_year':apply_year

        })

class GetChartResult(LoginRequiredMixin, ListView):
    def get(self, request):
        '''Default function for get request'''
        
        apply_growers = int(request.GET.get('apply_growers', 0))
        apply_farm = int(request.GET.get('apply_farm', 0))
        apply_field = int(request.GET.get('apply_field', 0))
        apply_year = int(request.GET.get('apply_year', 0))

        name_survey_data = NameSurvey.objects.filter(surveyyear=apply_year)
        name_survey_ids = [name_survey.id for name_survey in name_survey_data]
        
        sustain_data = SustainabilitySurvey.objects.filter(grower_id=apply_growers, farm_id=apply_farm, field_id=apply_field, namesurvey_id__in=name_survey_ids)

        if sustain_data.count() > 0:
            Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
            Avg_Percentage_Score = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
        else:
            Avg_Percentage_Score = 0

        # request.session['fav_color'] = 'blue'
        # fav_color = request.session.get('fav_color', 'red')

        # print(fav_color)
            

        return render(request, 'growersurvey/set-chart-data.html', {
            'sustain_data': sustain_data,
            'Avg_Percentage_Score': Avg_Percentage_Score,
        })


# class SetChartImage(LoginRequiredMixin, ListView):
#     def get(self, request):
#         '''Default function for get request'''
#         chart_data = request.GET.get('chart_data')
#         request.session['chart_data'] = chart_data
#         # chart_data = request.session.get('chart_data', '')

#         # print(fav_color)
#         return HttpResponse(chart_data)

def SetChartImage(request):
    '''Default function for get request'''
    chart_data = request.POST.get('chart_data')
    request.session['chart_data'] = chart_data
    # chart_data = request.session.get('chart_data', '')

    # print(fav_color)
    return HttpResponse(chart_data)



class MyView(LoginRequiredMixin, ListView):
    def get(self, request, **kwargs):
        
        apply_growers = int(self.kwargs.get('apply_growers', 0))
        apply_farm = int(self.kwargs.get('apply_farm', 0))
        apply_field = int(self.kwargs.get('apply_field', 0))
        apply_year = int(self.kwargs.get('apply_year', 0))

        grower_data = Grower.objects.get(id=apply_growers)
        some_date = datetime.date.today()

        #print(grower_data)
        #print(some_date)
        
        
        #Retrieve data or whatever you need table data
        try:
            name_survey_data = NameSurvey.objects.filter(surveyyear=apply_year)
            name_survey_ids = [name_survey.id for name_survey in name_survey_data]
            type_survey_data = [name_survey_type.typesurvey for name_survey_type in name_survey_data]
        except NameSurvey.DoesNotExist:
            name_survey_ids = []
            type_survey_data = []

        try:
            sustain_data = SustainabilitySurvey.objects.filter(grower_id=apply_growers, farm_id=apply_farm, field_id=apply_field, namesurvey_id__in=name_survey_ids)
            conpleted_name_survey_ids = [comp_name_survey.namesurvey_id for comp_name_survey in sustain_data]
        except SustainabilitySurvey.DoesNotExist:
            conpleted_name_survey_ids = []

        completed_input_survey_data = InputSurvey.objects.filter(grower_id=apply_growers, farm_id=apply_farm, field_id=apply_field, namesurvey_id__in=conpleted_name_survey_ids)


        
        #Retrieve data or whatever you need table data end

        #Retrieve data or whatever you need chart data start

        name_survey_data_chart = NameSurvey.objects.filter(surveyyear=apply_year)
        name_survey_ids_chart = [name_survey.id for name_survey in name_survey_data_chart]
        
        sustain_data_chart = SustainabilitySurvey.objects.filter(grower_id=apply_growers, farm_id=apply_farm, field_id=apply_field, namesurvey_id__in=name_survey_ids_chart)

        if sustain_data_chart.count() > 0:
            Avg_Percentage_Score_data_chart = sustain_data_chart.aggregate(Avg('sustainabilityscore'))
            Avg_Percentage_Score_chart = int(Avg_Percentage_Score_data_chart['sustainabilityscore__avg'])
        else:
            Avg_Percentage_Score_chart = 0

        #Retrieve data or whatever you need chart data end
        chart_data = request.session.get('chart_data', '')
        
        # return render(request,
        #         'growersurvey/mytemplate.html',
        #         {
        #             'pagesize':'A4',
        #             'sustain_data': sustain_data_chart,
        #             'Avg_Percentage_Score': Avg_Percentage_Score_chart,
        #             'completed_input_survey_data': completed_input_survey_data,
        #             'type_survey_data': type_survey_data,
        #             'chart_data': chart_data,
        #         }
        #     )

        

        return render_to_pdf(
                'growersurvey/mytemplate.html',
                {
                    'pagesize':'A4',
                    'sustain_data': sustain_data_chart,
                    'Avg_Percentage_Score': Avg_Percentage_Score_chart,
                    'completed_input_survey_data': completed_input_survey_data,
                    'type_survey_data': type_survey_data,
                    'chart_data': chart_data,
                    'grower_data': grower_data,
                    'some_date': some_date,
                }
            )

def pdf_dw(request):                                  

    # Create the HttpResponse object 
    response = HttpResponse(content_type='application/pdf') 

    # This line force a download
    response['Content-Disposition'] = 'attachment; filename="1.pdf"' 

    # READ Optional GET param
    get_param = request.GET.get('name', 'World')

    # Generate unique timestamp
    # ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    p = canvas.Canvas(response)

    # Write content on the PDF 
    p.drawString(100, 500, "Hello " + get_param + " (Dynamic PDF) - " ) 

    # Close the PDF object. 
    p.showPage() 
    p.save() 

    # Show the result to the user    
    return response

class GrowerSustainComparison(LoginRequiredMixin, ListView):
    def get(self, request):
        type_survey_data = TypeSurvey.objects.all().order_by('name')
        if 'Grower' in request.user.get_role() and not request.user.is_superuser:
            # do something grower
            grower_id=request.user.grower.id
            grower_obj = Grower.objects.filter(id=grower_id).order_by('name')
            
        else:
            if request.user.is_consultant:
                # do something consultant
                consultant_id = Consultant.objects.get(email= request.user.email).id
                grower_obj = Grower.objects.filter(consultant=consultant_id).order_by('name')
                
            else:
                # do something allpower
                grower_obj = Grower.objects.all().order_by('name')

        comparison_arr = []

        grower_id = [i.id for i in grower_obj]
        field =Field.objects.filter(grower_id__in=grower_id)
        for i in field:
            grower_field = i.name
            grower_name = i.grower.name
            grower_id = i.grower.id
            grower_farm = i.farm.name
            farm_id = i.farm.id
            field_id = i.id
            crop = i.crop
            state = i.farm.state
            city = i.farm.town
            acres = i.acreage
            if i.crop == 'RICE':
                projected_yield = round(i.acreage * 8300,2)
                actual_yield = i.total_yield
                if actual_yield == None:
                    yield_var = "N/A"
                else:
                    yield_var = projected_yield - actual_yield
                
            elif i.crop == 'COTTON':
                projected_yield = i.acreage * 900
                actual_yield = 'N/A'
                yield_var = 'N/A'
            
            surveyscore1 = i.get_survey1()
            surveyscore2 = i.get_survey2()
            surveyscore3 = i.get_survey3()
            if surveyscore1 != '' and surveyscore1 != None :
                surveyscore1 = float(surveyscore1)
            else:
                surveyscore1 = 0
            if surveyscore2 != '' and surveyscore2 != None :
                surveyscore2 = float(surveyscore2)
            else:
                surveyscore2 = 0
            if surveyscore3 != '' and surveyscore3 != None :
                surveyscore3 = float(surveyscore3)
            else:
                surveyscore3 = 0
            year = '2022'
            sus = SustainabilitySurvey.objects.filter(grower_id=grower_id).filter(field_id=i.id)
            
            # name_survey_type_id = [i.namesurvey.typesurvey.id for i in sus][0]
            name_survey_type_id = 1
            composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
            if crop == "RICE":
                if composite_score >= 70:
                    certificate = "Pass"
                elif composite_score < 70:
                    certificate = "Fail"
            elif crop == "COTTON":
                if composite_score >= 75:
                    certificate = "Pass"
                elif composite_score < 75:
                    certificate = "Fail"
            
            else:
                if composite_score >= 70:
                    certificate = "Pass"
                elif composite_score < 70:
                    certificate = "Fail"
            sustain_res = {
                    'grower_name' : grower_name,
                    'crop' : crop,
                    'grower_farm': grower_farm,
                    'grower_field': grower_field,
                    'survey_year': year,
                    'acres': acres,
                    'grower_id': grower_id,
                    'name_survey_type_id': name_survey_type_id,
                    'farm_id': farm_id,
                    'field_id': field_id,
                    'crop': crop,
                    'state': state,
                    'city': city,
                    "projected_yield":projected_yield,
                    "actual_yield":actual_yield,
                    "yield_var":yield_var,
                    "composite_score":composite_score,
                    "certificate":certificate,
                    "surveyscore1":surveyscore1,
                    "surveyscore2":surveyscore2,
                    "surveyscore3":surveyscore3,
                    
                }
            comparison_arr.append(sustain_res)
                
        return render(request, 'growersurvey/grower_comparison.html', {
                    'comparison_arr':comparison_arr,
                    'grower_obj':grower_obj,
                    'type_survey_data':type_survey_data,
                })


@login_required()
def download_all_survey_record(request):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        survey_rec = SurveyCsvTable.objects.all()
        filename = 'Survey_Records.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Grower', 'Field', 'Field ID', 'Survey', 'Questions','Answer','Answer Score','Attachments', 'Status', 'Date'])
        for i in survey_rec :
            g_n = i.grower_namee
            g_f = i.field_namee
            g_f_i = i.field_idd
            question_name = i.question_name
            ans_name = i.ans_name
            ans_score = i.ans_score
            attachment = i.attachment
            status = i.status
            created_date = i.created_date
            survey_name = i.survey_name
            if ans_name :
                writer.writerow([g_n, g_f, g_f_i, survey_name, question_name, ans_name, ans_score, attachment, status, created_date])

        return response


def updatesurvey_forcsv(request):
    survey_rec = InputSurvey.objects.all()[40000:]
    for i in survey_rec :
        gid = i.grower.id
        gna = i.grower.name
        fid = i.field.id
        fna = i.field.name
        fmid = i.farm.id
        fmname = i.farm.name
        namesurvey_id = i.namesurvey.id
        survey_name = f"{i.namesurvey.typesurvey.name} - 2022"
        question_name = i.questionsurvey.questionname
        ans_id = i.optionscore_ids
        if ans_id :
            var_split = ans_id.split(',')              
            answ = OptionSurvey.objects.filter(id__in=var_split)
            answ_w = [j.optionname for j in answ]
            ans_name = str(answ_w)[1:-1]
        else:
            ans_name = ""
        ans_score = i.optionscore
        attachment = i.questionsurvey.evidence_requird
        status = i.status
        created_date = i.created_date.strftime("%m/%d/%y")
        crop = i.field.crop

        sur_tab = SurveyCsvTable(grower_id=gid,grower_idd=gid,grower_namee=gna,field_id=fid,field_idd=fid,field_namee=fna,farm_id=fmid,farm_idd=fmid,
        farm_namee=fmname,namesurvey_id=namesurvey_id,survey_name=survey_name,question_name=question_name,ans_name=ans_name,ans_score=ans_score,
        attachment=attachment,status=status,created_date=created_date,crop=crop)
        sur_tab.save()
    return HttpResponse ("Input Survey Updated")


login_required()
def field_level_sustainability(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        # fields = Field.objects.all().order_by('name')
        # context['fields'] = fields
        context['growers'] = Grower.objects.all().order_by("name")
        if request.method == 'POST':
            fieldid = request.POST.get('fieldid')
            yearid = request.POST.get('yearid')
            growerid = request.POST.get('growerid')
            if growerid and growerid !="all" :
                fields = Field.objects.filter(grower_id=growerid).order_by('name')
                context['fields'] = fields
                context['selectedGrower'] = Grower.objects.get(id=growerid)
            
            if fieldid and fieldid !="all" :
                get_field = Field.objects.get(id=fieldid)
            # try:
            #     get_field = Field.objects.get(name__icontains=fieldid)
            # except:
            #     messages.error(request,'please select a vaild field')
            #     return render (request,'growersurvey/field_level_sustainability.html',context)
            print(fieldid,yearid,growerid)
            if fieldid and yearid != 'all' and fieldid != "all" and growerid and growerid !="all" :
                get_field = Field.objects.get(id=fieldid)
                context["selectedField"] = get_field
                context["selectedYear"] = yearid

                with_year_field = FieldUpdated.objects.filter(field_id=get_field.id,crop_year=yearid).values('id')
                if with_year_field.exists():
                    with_year_field_ids = [i['id'] for i in with_year_field]
                    context["updatedField_id"] = with_year_field_ids[0]
                    get_field_activity = FieldActivity.objects.filter(field_updated_id__in=with_year_field_ids)

                    field_activity_Burndown_Chemical = get_field_activity.filter(field_activity='Burndown_Chemical')
                    context["field_activity_Burndown_Chemical"] = field_activity_Burndown_Chemical
                    
                    field_activity_Preemergence_Chemical = get_field_activity.filter(field_activity='Preemergence_Chemical')
                    context["field_activity_Preemergence_Chemical"] = field_activity_Preemergence_Chemical

                    field_activity_Post_Emergence_Chemical = get_field_activity.filter(field_activity='Post_Emergence_Chemical')
                    context["field_activity_Post_Emergence_Chemical"] = field_activity_Post_Emergence_Chemical

                    field_activity_Emergence_Chemical = get_field_activity.filter(field_activity='Emergence_Chemical')
                    context["field_activity_Emergence_Chemical"] = field_activity_Emergence_Chemical

                    field_activity_Fungicide_Micro_Nutrients = get_field_activity.filter(field_activity='Fungicide_Micro_Nutrients')
                    context["field_activity_Fungicide_Micro_Nutrients"] = field_activity_Fungicide_Micro_Nutrients

                    field_activity_Insecticide_Application = get_field_activity.filter(field_activity='Insecticide_Application')
                    context["field_activity_Insecticide_Application"] = field_activity_Insecticide_Application

                    field_activity_Litter = get_field_activity.filter(field_activity='Litter')
                    context["field_activity_Litter"] = field_activity_Litter

                    field_activity_Sodium_Chlorate = get_field_activity.filter(field_activity='Sodium_Chlorate')
                    context["field_activity_Sodium_Chlorate"] = field_activity_Sodium_Chlorate

                    field_activity_Measure_Water = get_field_activity.filter(field_activity='Measure_Water')
                    context["field_activity_Measure_Water"] = field_activity_Measure_Water

                    field_activity_npk = get_field_activity.filter(field_activity='NPK_Application')
                    context["field_activity_npk"] = field_activity_npk

                    sum_nitrogen = sum([i.n_nitrogen for i in field_activity_npk])
                    context["sum_nitrogen"] = sum_nitrogen

                    sum_phosporus = sum([i.p_phosporus for i in field_activity_npk])
                    context["sum_phosporus"] = sum_phosporus

                    sum_potassium = sum([i.k_potassium for i in field_activity_npk])
                    context["sum_potassium"] = sum_potassium
                else:
                    context["updatedField_id"] = 'all'
                field_name = get_field.name
                year = yearid
                crop = get_field.crop
                variety = get_field.variety
                farm = get_field.farm.name
                grower = get_field.grower.name
                acreage = get_field.acreage
                yield_per_acre = get_field.yield_per_acre
                total_yield = get_field.total_yield
                context["report"] = [{'field_name':field_name,'year':year,'crop':crop,'variety':variety,'farm':farm,'grower':grower,
                                      'acreage':acreage,'yield_per_acre':yield_per_acre,'total_yield':total_yield}]
            
            elif fieldid == "all" and yearid == 'all' and growerid == "all" :
                messages.error(request,'please select Grower')
                # context["selectedField"] = get_field       
            elif fieldid != "all" and yearid == 'all' and growerid != "all" :
                if get_field :
                    context["selectedField"] = get_field
                
                messages.error(request,'please select Crop Year')
            elif fieldid == "all" and yearid == 'all' and growerid != "all" :
                messages.error(request,'please select Field and Crop Year')
        return render (request,'growersurvey/field_level_sustainability.html',context)
    else:
        return redirect ('dashboard')

login_required()
def field_level_sustainability_csv(request,field_id,yearid):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        current_date_time = datetime.date.today()
        try :
            with_year_field = FieldUpdated.objects.filter(field_id=field_id,crop_year=yearid).values('id','crop_year')
            get_field = Field.objects.get(id=field_id)
            crop_year = yearid
            filename = f"{get_field.name}_level_sustainability_{current_date_time}.csv"
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
            )
            writer = csv.writer(response)
            writer.writerow(['Field Info'])
            writer.writerow(['Field', 'Crop Year', 'Crop', 'Variety', 'Farm','Grower','Acreage','Yield Per Acre', 'Total Yield'])
            writer.writerow([get_field.name,crop_year, get_field.crop, get_field.variety, get_field.farm.name, get_field.grower.name, get_field.acreage, get_field.yield_per_acre, get_field.total_yield])
            
            # All applied nutrients
            if with_year_field.exists():
                    with_year_field_ids = [i['id'] for i in with_year_field]
                    get_field_activity = FieldActivity.objects.filter(field_updated_id__in=with_year_field_ids)
                    field_activity_Burndown_Chemical = get_field_activity.filter(field_activity='Burndown_Chemical')
                    if field_activity_Burndown_Chemical.exists():
                        writer.writerow([''])
                        writer.writerow(['Burndown Chemical'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Burndown_Chemical :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Preemergence_Chemical = get_field_activity.filter(field_activity='Preemergence_Chemical')
                    if field_activity_Preemergence_Chemical.exists():
                        writer.writerow([''])
                        writer.writerow(['Preemergence Chemical'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Preemergence_Chemical :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Post_Emergence_Chemical = get_field_activity.filter(field_activity='Post_Emergence_Chemical')
                    if field_activity_Post_Emergence_Chemical.exists():
                        writer.writerow([''])
                        writer.writerow(['Post Emergence Chemical'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Post_Emergence_Chemical :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Emergence_Chemical = get_field_activity.filter(field_activity='Emergence_Chemical')
                    if field_activity_Emergence_Chemical.exists():
                        writer.writerow([''])
                        writer.writerow(['Emergence Chemical'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Emergence_Chemical :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Fungicide_Micro_Nutrients = get_field_activity.filter(field_activity='Fungicide_Micro_Nutrients')
                    if field_activity_Fungicide_Micro_Nutrients.exists():
                        writer.writerow([''])
                        writer.writerow(['Fungicide / Micro Nutrients'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Fungicide_Micro_Nutrients :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Insecticide_Application = get_field_activity.filter(field_activity='Insecticide_Application')
                    if field_activity_Insecticide_Application.exists():
                        writer.writerow([''])
                        writer.writerow(['Insecticide Application'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Insecticide_Application :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Litter = get_field_activity.filter(field_activity='Litter')
                    if field_activity_Litter.exists():
                        writer.writerow([''])
                        writer.writerow(['Litter'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Litter :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Sodium_Chlorate = get_field_activity.filter(field_activity='Sodium_Chlorate')
                    if field_activity_Sodium_Chlorate.exists():
                        writer.writerow([''])
                        writer.writerow(['Sodium Chlorate'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Sodium_Chlorate :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_Measure_Water = get_field_activity.filter(field_activity='Measure_Water')
                    if field_activity_Measure_Water.exists():
                        writer.writerow([''])
                        writer.writerow(['Measured Water Use'])
                        writer.writerow(['Date of Activity', 'Mode of Application', 'Label Name', 'Amount Per Acre', 'UoM','Special Notes'])
                        for i in field_activity_Measure_Water :
                            writer.writerow([i.date_of_activity, i.mode_of_application, i.label_name, i.amount_per_acre, i.unit_of_acre,i.special_notes])
                    
                    field_activity_npk = get_field_activity.filter(field_activity='NPK_Application')
                    if field_activity_npk.exists():
                        writer.writerow([''])
                        writer.writerow(['NPK Application'])
                        writer.writerow(['Date of Activity', 'Activity Type', 'Mode', 'N-Nitrogen', 'P-Phosporus','K-Potassium','UoM','Special Notes'])
                        for i in field_activity_npk :
                            writer.writerow([i.date_of_activity, i.type_of_application, i.mode_of_application, i.n_nitrogen, i.p_phosporus,i.k_potassium,'LBS / acre',i.special_notes])

                        sum_nitrogen = sum([i.n_nitrogen for i in field_activity_npk])
                        sum_phosporus = sum([i.p_phosporus for i in field_activity_npk])
                        sum_potassium = sum([i.k_potassium for i in field_activity_npk])
                        writer.writerow(['Total', '', '', sum_nitrogen, sum_phosporus,sum_potassium,'LBS / acre'])
            # All applied nutrients
            if get_field.crop == 'COTTON':
                get_bale = BaleReportFarmField.objects.filter(ob4=get_field.id).values('bale_id','level')
                writer.writerow([''])
                writer.writerow(['All bale/shipment IDs'])
                writer.writerow(['Bale IDs','Level'])
                for i in get_bale:
                    writer.writerow([i['bale_id'],i['level']])
            elif get_field.crop == 'RICE':
                get_shipment = GrowerShipment.objects.filter(field_id=get_field.id).values('shipment_id','status')
                writer.writerow([''])
                writer.writerow(['All bale/shipment IDs'])
                writer.writerow(['shipment IDs','Status'])
                for i in get_shipment:
                    writer.writerow([i['shipment_id'],i['status']])
            return response
        except:
            filename = f'level_sustainability_{current_date_time}.csv'
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
            )
            writer = csv.writer(response)
            return response
    else:
        return redirect ('dashboard')
    

login_required()
def field_autocomplete_suggestions(request):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        all_field = Field.objects.all().values('name').order_by('name')
        lst = [i['name'] for i in all_field]
        responce = {'select_search':lst}
        return JsonResponse(responce)
    else:
        return redirect ('dashboard')