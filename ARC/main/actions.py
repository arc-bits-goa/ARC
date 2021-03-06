import re
from main.models import *
# from main.views import map_options

from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from main.forms import MapsForm, SingleCDCForm
from django import forms


def single_option_CDC(modeladmin, request, queryset):
    form = SingleCDCForm()
    form.fields["students"].initial=queryset
    context = modeladmin.admin_site.each_context(request)
    context["form"] = form
    context['opts'] = modeladmin.model._meta
    return TemplateResponse(request, "maps/single_option_CDC_select.html", context)


single_option_CDC.short_description = "Generate single option CDC data."

def single_option_CDC_logic(students, year, sem):
    
    for student in students:
        # i=i+1
        stuYear = year
        # print(student.CAMPUS_ID)
        branches = get_branch(student.CAMPUS_ID) 
        # print(branches)
        for branch in branches:
            CDCs = get_cdcs(branch, stuYear, sem)
            # print(CDCs)
            for cdc in CDCs:
                if check_if_single_option_CDC(str(int(float(cdc.comp_codes)))):
                    generate_output(cdc.comp_codes, student, cdc)
            stuYear -= 1


def apply_maps(modeladmin, request, queryset):
    form = MapsForm()
    form.fields["students"].initial = queryset
    context = modeladmin.admin_site.each_context(request)
    context["form"] = form
    context['opts'] = modeladmin.model._meta
    return TemplateResponse(request, "maps/map_options.html", context)


apply_maps.short_description = "Apply pre-defined maps"

# def get_maps(maps):
#     map_names = [map.name]
#     for val in CourseSlot.objects.all():
#         if if val in Map.courseSlots.all()

def apply_maps_logic(students, maps):
    
    for student in students:
        for m in maps.all():
            print(m)
            for course in m.courseSlots.all():
                generate_output_maps(course, student)

def get_branch(CAMPUS_ID):
    branches = []
    for i in [CAMPUS_ID[4:6], CAMPUS_ID[6:8]]:
        if i[0] == "A" or i[0] == "B":
            branches.append(i)
    return branches


def get_cdcs(branch, year, sem):
    print ("get_cdcs")
    return CDC.objects.filter(
        tag=branch + "CDC").filter(year__icontains=year).filter(sem__icontains=sem)


def check_if_single_option_CDC(comp_codes):
    print(comp_codes)
    # logic to check if single option
    # course_slots = get_course_slots(comp_codes)

    nP = len(CourseSlot.objects.filter(
        course_id__icontains=comp_codes).filter(section__startswith="P"))
    nL = len(CourseSlot.objects.filter(
        course_id__icontains=comp_codes).filter(section__startswith="L"))
    nG = len(CourseSlot.objects.filter(
        course_id__icontains=comp_codes).filter(section__startswith="G"))

    print(nP, nL, nG)
    if nP <= 1 and nL <= 1 and nG <= 1:
        return True

    return False


def get_course_slots(comp_codes):

    return CourseSlot.objects.filter(course_id__endswith=str(int(float(comp_codes))))


def generate_output(comp_codes, student, cdc):
    # print(123)  # , comp_codes, cdc)
    # print(comp_codes[:2])
    courseslots = get_course_slots(comp_codes)
    # print(courseslots)
    for slot in courseslots:
        # print(slot)
        output = Output(EMPLID=student.id,
                        CAMPUS_ID=student.CAMPUS_ID,
                        CRSE_ID=int(float(cdc.comp_codes)),
                        SUBJECT=re.split('\W+', cdc.course_code)[0],
                        CATALOG_NBR=re.split('\W+', cdc.course_code)[1],
                        DESCR=cdc.course_name,
                        CLASS_NBR=int(float(slot.class_nbr)),
                        CLASS_SECTION=slot.section)
        # print(output)
        output.save()

def generate_output_maps(courseslot, student):
    # print(123)  # , comp_codes, cdc)
    # print(comp_codes[:2])
    # courseslots = get_course_slots(comp_codes)
    # print(courseslots)
    # for slot in courseslots:
        # print(slot)
    output = Output(EMPLID=student.id,
                    CAMPUS_ID=student.CAMPUS_ID,
                    CRSE_ID=int(float(courseslot.course_id[1:])),
                    SUBJECT=courseslot.subject,
                    CATALOG_NBR=re.split('\W+', courseslot.catalog)[0],
                    DESCR=courseslot.course_title,
                    CLASS_NBR=int(float(courseslot.class_nbr)),
                    CLASS_SECTION=courseslot.section)
    print(output)
    output.save()
