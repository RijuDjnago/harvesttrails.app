from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.field.models import *
from apps.farms.models import *
from apps.grower.models import *
from apps.processor.models import *
from apps.processor2.models import *
import csv
from django.db.models import Q
import datetime
# Create your views here.


def get_processor_type(processor_name):
    check_processor = Processor.objects.filter(entity_name=processor_name)
    if check_processor:
        processor_details = {'id':check_processor.first().id,
                             'type':'T1'}        
    else:
        get_processor = Processor2.objects.filter(entity_name=processor_name)
        if get_processor:
            processor = get_processor.first()
            processor_details = {'id':processor.id,
                             'type':processor.processor_type}
        else:
            processor_details = {'id':None,
                                 'type':None}
    return processor_details


def get_Origin(crop,field_id,field_name,bale_id,warehouse_wh_id) :
    if type(field_id) != None and field_id !=  None :
        get_field = Field.objects.get(id=field_id)
    elif type(field_name) != None and field_name !=  None :
        get_field = Field.objects.get(id=field_id)
    else:
        get_field = ''
    variety = get_field.variety if get_field.variety else ''
    field_name = get_field.name if get_field.name else ''
    field_id = get_field.id if get_field.id else ''
    projected_yeild = float(get_field.total_yield) if get_field.total_yield else ''
    reported_yeild = ''
    yield_delta = ''
    harvest_date = get_field.harvest_date if get_field.harvest_date else ''
    water_savings = get_field.gal_water_saved if get_field.gal_water_saved else ''
    water_per_pound_savings = get_field.water_lbs_saved if get_field.water_lbs_saved else ''
    land_use = get_field.land_use_efficiency if get_field.land_use_efficiency else ''
    less_GHG = get_field.ghg_reduction if get_field.ghg_reduction else ''
    co2_eQ_footprint = get_field.co2_eq_reduced if get_field.co2_eq_reduced else ''
    premiums_to_growers = get_field.grower_premium_percentage if get_field.grower_premium_percentage else ''
    surveyscore1 = get_field.get_survey1()
    surveyscore2 = get_field.get_survey2()
    surveyscore3 = get_field.get_survey3()
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
    composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
    if crop == "RICE":
        if composite_score >= 70:
            pf_sus = "Pass"
        elif composite_score < 70:
            pf_sus = "Fail"
    elif crop == "COTTON":
        if composite_score >= 75:
            pf_sus = "Pass"
        elif composite_score < 75:
            pf_sus = "Fail"

    if crop == 'COTTON' :
        get_bale = BaleReportFarmField.objects.filter(bale_id=bale_id,warehouse_wh_id=warehouse_wh_id)
        if len(get_bale) == 1 :
            get_bale_id = [i.id for i in get_bale][0]
            get_bale = BaleReportFarmField.objects.get(id=get_bale_id)
            reported_yeild = float(get_bale.net_wt.strip())
            pf_sus = get_bale.ob5
            level = get_bale.level
            grade = get_bale.gr
            leaf = get_bale.lf
            staple = get_bale.st
            length = get_bale.len_num
            strength = get_bale.str_no
            mic = get_bale.mic
            storage_quanitty = get_bale.net_wt
            if get_field.total_yield :
                projected_yeild = float(get_field.total_yield)
                reported_yeild = reported_yeild
                yield_delta = reported_yeild - projected_yeild
            else :
                projected_yeild = ''
                reported_yeild = reported_yeild
                yield_delta = ''
        #  search by Field 
        else:
            if get_field.total_yield :
                projected_yeild = float(get_field.total_yield)
            else:
                projected_yeild = ''
            reported_yeild = ''
            yield_delta = ''
            level = ''
            grade = ''
            leaf = ''
            staple = ''
            length = ''
            strength = ''
            mic = ''
            storage_quanitty = ''
    if crop == 'RICE' :
        shipment = GrowerShipment.objects.filter(shipment_id=bale_id)
        if shipment.exists() :
            shipment = GrowerShipment.objects.get(shipment_id=bale_id)
            variety = shipment.variety
            field_name = shipment.field.name
            field_id = shipment.field.id
            reported_yeild = shipment.total_amount
            storage_quanitty = shipment.total_amount

            if get_field.total_yield :
                projected_yeild = float(get_field.total_yield)
                reported_yeild = float(reported_yeild)
                yield_delta = reported_yeild - projected_yeild
            else :
                projected_yeild = ''
                reported_yeild = reported_yeild
                yield_delta = ''
        else:
            pass
        level = ''
        grade = ''
        leaf = ''
        staple = ''
        length = ''
        strength = ''
        mic = ''
        storage_quanitty = ''
    return {"get_select_crop":crop,"variety":variety,"field_name":field_name,"field_id":field_id,"grower_name":get_field.grower.name,
        "grower_id":get_field.grower.id,"farm_name":get_field.farm.name,"farm_id":get_field.farm.id,
        "harvest_date":harvest_date,"projected_yeild":projected_yeild,"reported_yeild":reported_yeild,"yield_delta":yield_delta,
        "pf_sus":pf_sus,"water_savings":water_savings,"water_per_pound_savings":water_per_pound_savings,"land_use":land_use,
        "less_GHG":less_GHG,"co2_eQ_footprint":co2_eQ_footprint,"premiums_to_growers":premiums_to_growers,"level":level,
        "grade":grade,"leaf":leaf,"staple":staple,"length":length,"strength":strength,"mic":mic,"storage_quanitty":storage_quanitty}

def get_Origin_deliveryid(crop,field_id,field_name,bale_id,warehouse_wh_id) :
    if type(field_id) != None and field_id !=  None :
        get_field = Field.objects.get(id=field_id)
    elif type(field_name) != None and field_name !=  None :
        get_field = Field.objects.get(id=field_id)
    else:
        get_field = ''
    variety = get_field.variety if get_field.variety else ''
    field_name = get_field.name if get_field.name else ''
    field_id = get_field.id if get_field.id else ''
    projected_yeild = float(get_field.total_yield) if get_field.total_yield else ''
    reported_yeild = ''
    yield_delta = ''
    harvest_date = get_field.harvest_date if get_field.harvest_date else ''
    water_savings = get_field.gal_water_saved if get_field.gal_water_saved else ''
    water_per_pound_savings = get_field.water_lbs_saved if get_field.water_lbs_saved else ''
    land_use = get_field.land_use_efficiency if get_field.land_use_efficiency else ''
    less_GHG = get_field.ghg_reduction if get_field.ghg_reduction else ''
    co2_eQ_footprint = get_field.co2_eq_reduced if get_field.co2_eq_reduced else ''
    premiums_to_growers = get_field.grower_premium_percentage if get_field.grower_premium_percentage else ''
    surveyscore1 = get_field.get_survey1()
    surveyscore2 = get_field.get_survey2()
    surveyscore3 = get_field.get_survey3()
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
    composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
    if crop == "RICE":
        if composite_score >= 70:
            pf_sus = "Pass"
        elif composite_score < 70:
            pf_sus = "Fail"
    elif crop == "COTTON":
        if composite_score >= 75:
            pf_sus = "Pass"
        elif composite_score < 75:
            pf_sus = "Fail"

    if crop == 'COTTON' :
        get_bale = BaleReportFarmField.objects.filter(bale_id=bale_id,warehouse_wh_id=warehouse_wh_id)
        if len(get_bale) == 1 :
            get_bale_id = [i.id for i in get_bale][0]
            get_bale = BaleReportFarmField.objects.get(id=get_bale_id)
            reported_yeild = float(get_bale.net_wt.strip())
            pf_sus = get_bale.ob5
            level = get_bale.level
            grade = get_bale.gr
            leaf = get_bale.lf
            staple = get_bale.st
            length = get_bale.len_num
            strength = get_bale.str_no
            mic = get_bale.mic
            storage_quanitty = get_bale.net_wt
            if get_field.total_yield :
                projected_yeild = float(get_field.total_yield)
                reported_yeild = reported_yeild
                yield_delta = reported_yeild - projected_yeild
            else :
                projected_yeild = ''
                reported_yeild = reported_yeild
                yield_delta = ''
        #  search by Field 
        else:
            if get_field.total_yield :
                projected_yeild = float(get_field.total_yield)
            else:
                projected_yeild = ''
            reported_yeild = ''
            yield_delta = ''
            level = ''
            grade = ''
            leaf = ''
            staple = ''
            length = ''
            strength = ''
            mic = ''
            storage_quanitty = ''
    if crop == 'RICE' :
        shipment = GrowerShipment.objects.filter(shipment_id=bale_id)
        if shipment.exists() :
            shipment = GrowerShipment.objects.get(shipment_id=bale_id)
            variety = shipment.variety
            field_name = shipment.field.name
            field_id = shipment.field.id
            reported_yeild = shipment.total_amount
            storage_quanitty = shipment.total_amount

            if get_field.total_yield :
                projected_yeild = float(get_field.total_yield)
                reported_yeild = float(reported_yeild)
                yield_delta = reported_yeild - projected_yeild
            else :
                projected_yeild = ''
                reported_yeild = reported_yeild
                yield_delta = ''
        else:
            pass
        level = ''
        grade = ''
        leaf = ''
        staple = ''
        length = ''
        strength = ''
        mic = ''
        storage_quanitty = ''
    return [{"get_select_crop":crop,"variety":variety,"field_name":field_name,"field_id":field_id,"grower_name":get_field.grower.name,
        "grower_id":get_field.grower.id,"farm_name":get_field.farm.name,"farm_id":get_field.farm.id,
        "harvest_date":harvest_date,"projected_yeild":projected_yeild,"reported_yeild":reported_yeild,"yield_delta":yield_delta,
        "pf_sus":pf_sus,"water_savings":water_savings,"water_per_pound_savings":water_per_pound_savings,"land_use":land_use,
        "less_GHG":less_GHG,"co2_eQ_footprint":co2_eQ_footprint,"premiums_to_growers":premiums_to_growers,"level":level,
        "grade":grade,"leaf":leaf,"staple":staple,"length":length,"strength":strength,"mic":mic,"storage_quanitty":storage_quanitty}]
    
def Origin_searchby_Grower(crop,search_text,*grower_field_ids):
    return_lst = []
    if crop == 'COTTON' :
        for i in grower_field_ids :
            get_field = Field.objects.get(id=i)
            grower_name = get_field.grower.name
            grower_id = get_field.grower.id
            variety = get_field.variety
            field_name = get_field.name
            field_id = get_field.id
            farm_name = get_field.farm.name
            farm_id = get_field.farm.id
            harvest_date = get_field.harvest_date
            projected_yeild = get_field.total_yield
            storage_quanitty = get_field.total_yield
            water_savings = get_field.gal_water_saved
            land_use = get_field.land_use_efficiency
            less_GHG = get_field.ghg_reduction
            premiums_to_growers = get_field.grower_premium_percentage

            water_per_pound_savings = get_field.water_lbs_saved
            co2_eQ_footprint = get_field.co2_eq_reduced
            surveyscore1 = get_field.get_survey1()
            surveyscore2 = get_field.get_survey2()
            surveyscore3 = get_field.get_survey3()
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
            composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
            if crop == "RICE":
                if composite_score >= 70:
                    pf_sus = "Pass"
                elif composite_score < 70:
                    pf_sus = "Fail"
            elif crop == "COTTON":
                if composite_score >= 75:
                    pf_sus = "Pass"
                elif composite_score < 75:
                    pf_sus = "Fail"
            if projected_yeild :
                projected_yeild = float(get_field.total_yield)
                bale = BaleReportFarmField.objects.filter(ob4=get_field.id)
                
                if bale.exists() :
                    reported_yeild_lst = []
                    for j in bale :
                        var_wt = j.net_wt.strip()
                        
                        try:
                            cotton_net_wt = float(var_wt)
                        except:
                            cotton_net_wt = 0
                        reported_yeild_lst.append(cotton_net_wt)
                    reported_yeild = float(sum(reported_yeild_lst))
                    yield_delta = projected_yeild - reported_yeild
                else:
                    reported_yeild = 'None'
                    yield_delta = 'None'
            else:
                projected_yeild = 'None'
                reported_yeild = 'None'
                yield_delta = 'None'
            return_lst.extend([{"get_select_crop":'COTTON', "variety":variety, "field_name":field_name, "field_id":field_id, 
                                "grower_name":grower_name, "grower_id":grower_id, "farm_name":farm_name, "farm_id":farm_id,
                                "harvest_date":harvest_date, "projected_yeild":projected_yeild, "reported_yeild":reported_yeild,
                                "yield_delta":yield_delta, "storage_quanitty":storage_quanitty,"pf_sus":pf_sus,"water_savings":water_savings,"water_per_pound_savings":water_per_pound_savings,"land_use":land_use,
                                "less_GHG":less_GHG,"co2_eQ_footprint":co2_eQ_footprint,"premiums_to_growers":premiums_to_growers}])
    if crop == 'RICE' :
        for i in grower_field_ids :
            get_field = Field.objects.get(id=i)
            grower_name = get_field.grower.name
            grower_id = get_field.grower.id
            variety = get_field.variety
            field_name = get_field.name
            field_id = get_field.id
            farm_name = get_field.farm.name
            farm_id = get_field.farm.id
            harvest_date = get_field.harvest_date
            projected_yeild = get_field.total_yield
            storage_quanitty = get_field.total_yield
            water_savings = get_field.gal_water_saved
            land_use = get_field.land_use_efficiency
            less_GHG = get_field.ghg_reduction
            premiums_to_growers = get_field.grower_premium_percentage

            water_per_pound_savings = get_field.water_lbs_saved
            co2_eQ_footprint = get_field.co2_eq_reduced

            surveyscore1 = get_field.get_survey1()
            surveyscore2 = get_field.get_survey2()
            surveyscore3 = get_field.get_survey3()
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
            composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
            if crop == "RICE":
                if composite_score >= 70:
                    pf_sus = "Pass"
                elif composite_score < 70:
                    pf_sus = "Fail"
            elif crop == "COTTON":
                if composite_score >= 75:
                    pf_sus = "Pass"
                elif composite_score < 75:
                    pf_sus = "Fail"
            if projected_yeild :
                projected_yeild = float(get_field.total_yield)
                bale = GrowerShipment.objects.filter(field_id=get_field,status="APPROVED")
                if bale.exists() :
                    reported_yeild_lst = []
                    for j in bale :
                        var_wt = j.received_amount.strip()
                        try:
                            rice_net_wt = float(var_wt)
                        except:
                            rice_net_wt = 0
                        reported_yeild_lst.append(rice_net_wt)
                    reported_yeild = float(sum(reported_yeild_lst))
                    yield_delta = projected_yeild - reported_yeild
                else:
                    reported_yeild = 'None'
                    yield_delta = 'None'
            else:
                projected_yeild = 'None'
                reported_yeild = 'None'
                yield_delta = 'None'
            return_lst.extend([{"get_select_crop":'RICE', "variety":variety, "field_name":field_name, "field_id":field_id, 
                                "grower_name":grower_name, "grower_id":grower_id, "farm_name":farm_name, "farm_id":farm_id,
                                "harvest_date":harvest_date, "projected_yeild":projected_yeild, "reported_yeild":reported_yeild,
                                "yield_delta":yield_delta, "storage_quanitty":storage_quanitty,"pf_sus":pf_sus,"water_savings":water_savings,"water_per_pound_savings":water_per_pound_savings,"land_use":land_use,
                                "less_GHG":less_GHG,"co2_eQ_footprint":co2_eQ_footprint,"premiums_to_growers":premiums_to_growers}])
    return return_lst
   
def Origin_searchby_Processor(crop,search_text,*bale_id):
    return_lst = []
    if crop == 'COTTON' :
        for i in bale_id :
            get_bale = BaleReportFarmField.objects.get(id=i)
            variety = get_bale.crop_variety
            field_name = get_bale.field_name
            field_id = get_bale.ob4
            grower_name = get_bale.ob3
            grower_id = get_bale.ob2
            farm_name = get_bale.farm_name
            reported_yeild = get_bale.net_wt
            storage_quanitty = reported_yeild
            farm_id = ''
            harvest_date = ''
            projected_yeild = ''
            yield_delta = ''
            water_savings = ''
            land_use = ''
            less_GHG = ''
            premiums_to_growers = ''
            water_per_pound_savings = ''
            co2_eQ_footprint = ''
            pf_sus = ''
            if field_id :
                try :
                    get_field = Field.objects.get(id=field_id)
                    water_savings = get_field.gal_water_saved
                    land_use = get_field.land_use_efficiency
                    less_GHG = get_field.ghg_reduction
                    premiums_to_growers = get_field.grower_premium_percentage
                    water_per_pound_savings = get_field.water_lbs_saved
                    co2_eQ_footprint = get_field.co2_eq_reduced
                    harvest_date = get_field.harvest_date
                    projected_yeild = get_field.total_yield
                    surveyscore1 = get_field.get_survey1()
                    surveyscore2 = get_field.get_survey2()
                    surveyscore3 = get_field.get_survey3()
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
                    composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
                    if crop == "RICE":
                        if composite_score >= 70:
                            pf_sus = "Pass"
                        elif composite_score < 70:
                            pf_sus = "Fail"
                    elif crop == "COTTON":
                        if composite_score >= 75:
                            pf_sus = "Pass"
                        elif composite_score < 75:
                            pf_sus = "Fail"

                    if projected_yeild :
                        reported_yeild = float(reported_yeild)
                        projected_yeild = float(projected_yeild)
                        yield_delta = reported_yeild - projected_yeild
                except :
                    pass

            return_lst.extend([{"get_select_crop":'COTTON', "variety":variety, "field_name":field_name, "field_id":field_id, 
                                "grower_name":grower_name, "grower_id":grower_id, "farm_name":farm_name, "farm_id":farm_id,
                                "harvest_date":harvest_date, "projected_yeild":projected_yeild, "reported_yeild":reported_yeild,
                                "yield_delta":yield_delta, "storage_quanitty":storage_quanitty, "water_savings":water_savings,
                                "water_per_pound_savings":water_per_pound_savings, "land_use":land_use, "less_GHG":less_GHG,
                                "co2_eQ_footprint":co2_eQ_footprint, "premiums_to_growers":premiums_to_growers,"pf_sus":pf_sus}])
    if crop == 'RICE' :
        for i in bale_id :
            get_bale = GrowerShipment.objects.get(id=i)
            field_id = get_bale.field.id
            get_field = Field.objects.get(id=field_id)
            variety = get_field.variety
            field_name = get_field.name
            grower_name = get_field.grower.name
            # grower_location = get_field.grower.physical_address1
            grower_id = get_field.grower.id
            farm_name = get_field.farm.name
            farm_id = get_field.farm.id
            projected_yeild = get_field.total_yield
            reported_yeild = get_bale.received_amount
            storage_quanitty = reported_yeild
            water_savings = get_field.gal_water_saved
            land_use = get_field.land_use_efficiency
            less_GHG = get_field.ghg_reduction
            premiums_to_growers = get_field.grower_premium_percentage
            water_per_pound_savings = get_field.water_lbs_saved
            co2_eQ_footprint = get_field.co2_eq_reduced
            harvest_date = get_field.harvest_date
            yield_delta =''
            surveyscore1 = get_field.get_survey1()
            surveyscore2 = get_field.get_survey2()
            surveyscore3 = get_field.get_survey3()
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
            composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
            if crop == "RICE":
                if composite_score >= 70:
                    pf_sus = "Pass"
                elif composite_score < 70:
                    pf_sus = "Fail"
            elif crop == "COTTON":
                if composite_score >= 75:
                    pf_sus = "Pass"
                elif composite_score < 75:
                    pf_sus = "Fail"
            try :
                reported_yeild = float(reported_yeild)
                projected_yeild = float(projected_yeild)
                yield_delta = reported_yeild - projected_yeild
            except:
                pass          
            return_lst.extend([{"get_select_crop":'RICE', "variety":variety, "field_name":field_name, "field_id":field_id, 
                                "grower_name":grower_name, "grower_id":grower_id, "farm_name":farm_name, "farm_id":farm_id,
                                "harvest_date":harvest_date, "projected_yeild":projected_yeild, "reported_yeild":reported_yeild,
                                "yield_delta":yield_delta, "storage_quanitty":storage_quanitty, "water_savings":water_savings,
                                "water_per_pound_savings":water_per_pound_savings, "land_use":land_use, "less_GHG":less_GHG,
                                "co2_eQ_footprint":co2_eQ_footprint, "premiums_to_growers":premiums_to_growers,"pf_sus":pf_sus}])
            # print(return_lst,return_lst)

    return return_lst



def outbound1_Wip_Grower(crop,search_text,from_date,to_date,*grower_field_ids) :
    grower_field_ids = list(grower_field_ids)
    return_lst = []
    if crop == 'COTTON' :
        pass
    if crop == 'RICE' :
        # orders = GrowerShipment.objects.filter(Q(process_date__gte=from_date), Q(process_date__lte=to_date))
        get_shipment = GrowerShipment.objects.filter(field_id__in=grower_field_ids,status='').filter(Q(process_date__gte=from_date), Q(process_date__lte=to_date)).order_by('-id').values('id')
        if get_shipment.exists() :
            for i in get_shipment :
                get_shipment = GrowerShipment.objects.get(id=i['id'])
                deliveryid = get_shipment.shipment_id
                process_date = get_shipment.process_date
                quantity = get_shipment.total_amount
                skuid = get_shipment.sku   # add sku id
                transportation = ''
                destination = get_shipment.processor.entity_name
                grower_name = get_shipment.grower.name
                return_lst.extend([{"deliveryid":deliveryid,"source":grower_name,"skuid":skuid,"date":process_date,"quantity":quantity,"transportation":transportation,"destination":destination}])
        
    return return_lst

def outbound1_Wip_field(crop,search_text,from_date,to_date,field_id):
    return_lst = []
    if crop == 'COTTON' :
        pass
        # field = Field.objects.get(id=field_id)
        # get_bale = BaleReportFarmField.objects.filter(field_name=search_text,ob4=field_id).values("id")
        # if get_bale.exists() :
        #     for i in get_bale :
        #         get_bale_id = i["id"]
        #         get_bale = BaleReportFarmField.objects.get(id=get_bale_id)
        #         dt_class = get_bale.dt_class
        #         quantity = get_bale.net_wt
        #         deliveryid = get_bale.bale_id
        #         transportation = ''
        #         destination = get_bale.classing.processor.entity_name
        #         return_lst.extend([{"deliveryid":deliveryid,"date":dt_class,"quantity":quantity,"transportation":transportation,"destination":destination}])
    if crop == 'RICE' :
        get_shipment = GrowerShipment.objects.filter(field_id=field_id,status="").filter(Q(process_date__gte=from_date), Q(process_date__lte=to_date)).order_by('-id').values("id")
        if get_shipment.exists :
            for i in get_shipment :
                get_shipment_id = i["id"]
                get_shipment = GrowerShipment.objects.get(id=get_shipment_id)
                shipment_date = get_shipment.process_date
                quantity = get_shipment.total_amount
                deliveryid = get_shipment.shipment_id
                skuid = get_shipment.sku   # add sku id
                transportation = ''
                destination = get_shipment.processor.entity_name
                grower_name = get_shipment.grower.name
                return_lst.extend([{"deliveryid":deliveryid,"source":grower_name,"skuid":skuid,"date":shipment_date,"quantity":quantity,"transportation":transportation,"destination":destination}])
    return return_lst

def outbound1_Wip_Processor(crop,from_date,to_date,processorid):
    return_lst = []
    if crop == 'COTTON' :
        pass
    if crop == 'RICE' :
        get_shipment = GrowerShipment.objects.filter(processor_id=processorid,status="").filter(Q(process_date__gte=from_date), Q(process_date__lte=to_date)).order_by('-id').values("id")
        for i in get_shipment :
            get_shipment = GrowerShipment.objects.get(id=i["id"])
            shipment_date = get_shipment.process_date
            quantity = get_shipment.total_amount
            deliveryid = get_shipment.shipment_id
            grower_name = get_shipment.grower.name
            
            # skuid = get_shipment.sku   # add sku id
            # module_tag = get_shipment.module_number   # add module tag
            transportation = ''
            destination = get_shipment.processor.entity_name
            return_lst.extend([{"deliveryid":deliveryid,"source":grower_name,"date":shipment_date,"quantity":quantity,"transportation":transportation,"destination":destination}])
    return return_lst

def outbound1_Wip_deliveryid(crop,search_text,warehouse_wh_id,from_date,to_date):
    return_lst = []
    if crop == 'COTTON' :
        get_bale = BaleReportFarmField.objects.filter(bale_id=search_text,warehouse_wh_id=warehouse_wh_id)
        if len(get_bale) == 1 :
            get_bale_id = [i.id for i in get_bale][0]
            get_bale = BaleReportFarmField.objects.get(id=get_bale_id)
            dt_class = get_bale.dt_class
            transportation = ''
            return_lst.extend([{"deliveryid":search_text,"date":dt_class,"transportation":transportation}])
    if crop == 'RICE' :
        get_shipment = GrowerShipment.objects.filter(shipment_id=search_text,status="").filter(Q(process_date__gte=from_date), Q(process_date__lte=to_date))
        if len(get_shipment) == 1 :
            get_shipment_id = [i.id for i in get_shipment][0]
            get_shipment = GrowerShipment.objects.get(id=get_shipment_id)
            shipment_date = get_shipment.process_date
            transportation = ''
            skuid = get_shipment.sku   # add sku id
            quantity = get_shipment.total_amount
            destination = get_shipment.processor.entity_name
            grower_name = get_shipment.grower.name
            return_lst.extend([{"deliveryid":search_text,"source":grower_name,"skuid":skuid,"date":shipment_date,"quantity":quantity,"transportation":transportation,"destination":destination}])
    return return_lst



def t1_Processor_grower(crop,check_grower_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        bale = BaleReportFarmField.objects.filter(ob2=check_grower_id).values("id")
        for i in bale :
            get_bale = BaleReportFarmField.objects.get(id=i["id"])
            # yyyy-mm-dd
            processor_name = get_bale.classing.processor.entity_name
            processor_id = get_bale.classing.processor.id
            deliveryid = get_bale.bale_id
            dt_class = get_bale.dt_class
            # dt_class mm-dd-yy
            if dt_class :
                str_date = str(dt_class)
                if '-' in str_date :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                    else:
                        continue
                elif '/' in str_date :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                    else:
                        continue
                else:
                    continue
            else:
                continue
            
            pounds_shipped = get_bale.net_wt
            pounds_received = get_bale.net_wt
            grower = get_bale.ob3
            field = get_bale.field_name
            field_id = get_bale.ob4
            farm = ''
            if field_id :
                try:
                    get_field = Field.objects.get(id=field_id)
                    farm = get_field.farm.name
                except:
                    farm = ''
            
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"grower":grower,"farm":farm,"field":field,"processor_id":processor_id,"deliveryid":deliveryid,
                                "date":dt_class,"pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta}])
    if crop == 'RICE' :
        get_shipment = GrowerShipment.objects.filter(grower_id=check_grower_id,status="APPROVED").filter(Q(approval_date__gte=from_date), Q(approval_date__lte=to_date)).values("id")
        for i in get_shipment :
            get_shipment = GrowerShipment.objects.get(id=i["id"])
            processor_name = get_shipment.processor.entity_name
            processor_id = get_shipment.processor.id
            deliveryid = get_shipment.shipment_id
            dt_class = get_shipment.approval_date
            pounds_shipped = get_shipment.total_amount
            pounds_received = get_shipment.received_amount
            grower = get_shipment.grower.name
            field = get_shipment.field.name
            field_id = get_shipment.field.id
            get_field = Field.objects.get(id=field_id)
            farm = get_field.farm.name
            skuid = get_shipment.sku   # add sku_id
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"grower":grower,"farm":farm,"field":field,"processor_id":processor_id,"deliveryid":deliveryid,"skuid":skuid,
                                "date":dt_class,"pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta}])
                                
    return return_lst

def t1_Processor_field(crop,field_name,field_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        get_bale = BaleReportFarmField.objects.filter(field_name=field_name,ob4=field_id).values("id")
        if get_bale.exists() :
            for i in get_bale :
                get_bale_id = i["id"]
                get_bale = BaleReportFarmField.objects.get(id=get_bale_id)
                processor_id = get_bale.classing.processor.id
                processor_name = get_bale.classing.processor.entity_name
                deliveryid = get_bale.bale_id
                shipment_date = get_bale.dt_class
                dt_class = get_bale.dt_class
                if dt_class :
                    str_date = str(dt_class)
                    if '-' in str_date :
                        str_date = str_date.split('-')
                        mm = str_date[0]
                        dd = str_date[1]
                        yy = str_date[2]
                        yyyy = f'20{yy}' if len(yy) == 2 else yy
                        finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                        from_date = str(from_date).replace('-','/')
                        to_date = str(to_date).replace('-','/')
                        format = '%Y/%m/%d'
                        # convert from string format to datetime format
                        from_date = datetime.datetime.strptime(from_date, format).date()
                        to_date = datetime.datetime.strptime(to_date, format).date()

                        if finale_date >= from_date and finale_date <= to_date:
                            res = True
                        else:
                            continue
                    elif '/' in str_date :
                        str_date = str_date.split('/')
                        mm = str_date[0]
                        dd = str_date[1]
                        yy = str_date[2]
                        yyyy = f'20{yy}' if len(yy) == 2 else yy
                        finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                        from_date = str(from_date).replace('-','/')
                        to_date = str(to_date).replace('-','/')
                        format = '%Y/%m/%d'
                        # convert from string format to datetime format
                        from_date = datetime.datetime.strptime(from_date, format).date()
                        to_date = datetime.datetime.strptime(to_date, format).date()

                        if finale_date >= from_date and finale_date <= to_date:
                            res = True
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
                pounds_shipped = get_bale.net_wt
                pounds_received = get_bale.net_wt
                pounds_delta = ''
                grower = get_bale.ob3
                field = get_bale.field_name
                field_id = get_bale.ob4
                farm = ''
                if field_id :
                    try:
                        get_field = Field.objects.get(id=field_id)
                        farm = get_field.farm.name
                    except:
                        farm = ''
                try:
                    pounds_delta = float(pounds_shipped) - float(pounds_received)
                except:
                    pounds_delta = ''
                return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":shipment_date,
                                    "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                    "grower":grower,"farm":farm,"field":field}])
    if crop == 'RICE' :
        get_shipment = GrowerShipment.objects.filter(field_id=field_id,status="APPROVED").filter(Q(approval_date__gte=from_date), Q(approval_date__lte=to_date)).values("id")
        if get_shipment.exists :
            for i in get_shipment :
                get_shipment_id = i["id"]
                get_shipment = GrowerShipment.objects.get(id=get_shipment_id)
                processor_name = get_shipment.processor.entity_name
                processor_id = get_shipment.processor.id
                shipment_date = get_shipment.approval_date
                deliveryid = get_shipment.shipment_id
                pounds_shipped = get_shipment.total_amount
                pounds_received = get_shipment.received_amount
                grower = get_shipment.grower.name
                field = get_shipment.field.name
                field_id = get_shipment.field.id
                get_field = Field.objects.get(id=field_id)
                farm = get_field.farm.name
                skuid = get_shipment.sku   # add sku_id
                pounds_delta = ''
                try:
                    pounds_delta = float(pounds_shipped) - float(pounds_received)
                except:
                    pounds_delta = ''
                return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"skuid":skuid,"date":shipment_date,
                                    "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                    "grower":grower,"farm":farm,"field":field,}])
    return return_lst

def t1_Processor_Processor(crop,processor_id,from_date,to_date,*bale_id) :
    return_lst = []
    if crop == 'COTTON' :
        bale_id = list(bale_id)
        check_bale = BaleReportFarmField.objects.filter(id__in=bale_id).values('id')
        for i in check_bale :
            get_bale = BaleReportFarmField.objects.get(id=i['id'])
            processor_id = get_bale.classing.processor.id
            processor_name = get_bale.classing.processor.entity_name
            deliveryid = get_bale.bale_id
            shipment_date = get_bale.dt_class
            dt_class = get_bale.dt_class
            if dt_class :
                str_date = str(dt_class)
                if '-' in str_date :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                    else:
                        continue
                elif '/' in str_date :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                    else:
                        continue
                else:
                    continue
            else:
                continue
            pounds_shipped = get_bale.net_wt
            pounds_received = get_bale.net_wt
            grower = get_bale.ob3
            field = get_bale.field_name
            field_id = get_bale.ob4
            farm = ''
            if field_id :
                try:
                    get_field = Field.objects.get(id=field_id)
                    farm = get_field.farm.name
                except:
                    farm = ''
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                "grower":grower,"farm":farm,"field":field}])
    if crop == 'RICE' :
        check_shipment = list(bale_id)
        get_shipment = GrowerShipment.objects.filter(id__in=check_shipment,status='APPROVED').filter(Q(approval_date__gte=from_date), Q(approval_date__lte=to_date)).values('id')
        for i in get_shipment :
            get_shipment = GrowerShipment.objects.get(id=i['id'])
            processor_name = get_shipment.processor.entity_name
            processor_id = get_shipment.processor.id
            shipment_date = get_shipment.approval_date
            deliveryid = get_shipment.shipment_id
            pounds_shipped = get_shipment.total_amount
            pounds_received = get_shipment.received_amount
            grower = get_shipment.grower.name
            field = get_shipment.field.name
            field_id = get_shipment.field.id
            get_field = Field.objects.get(id=field_id)
            farm = get_field.farm.name
            skuid = get_shipment.sku   # add sku_id
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"skuid":skuid,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                "grower":grower,"farm":farm,"field":field,}])      
    return return_lst

def t1_Processor_deliveryid(crop,search_text,warehouse_wh_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        get_bale = BaleReportFarmField.objects.filter(bale_id=search_text,warehouse_wh_id=warehouse_wh_id)
        if len(get_bale) == 1 :
            get_bale_id = [i.id for i in get_bale][0]
            get_bale = BaleReportFarmField.objects.get(id=get_bale_id)
            processor_name = get_bale.classing.processor.entity_name
            processor_id = get_bale.classing.processor.id
            dt_class = get_bale.dt_class
            if dt_class :
                str_date = str(dt_class)
                if '-' in str_date :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        return return_lst

                elif '/' in str_date :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        return return_lst
                else:
                    return return_lst
            else:
                return return_lst

            pounds_shipped = get_bale.net_wt
            pounds_received = get_bale.net_wt
            grower = get_bale.ob3
            field = get_bale.field_name
            field_id = get_bale.ob4
            farm = ''
            if field_id :
                try:
                    get_field = Field.objects.get(id=field_id)
                    farm = get_field.farm.name
                except:
                    farm = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":search_text,"date":dt_class,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                "grower":grower,"farm":farm,"field":field}])
    if crop == 'RICE' :
        get_shipment = GrowerShipment.objects.filter(shipment_id=search_text,status="APPROVED").filter(Q(approval_date__gte=from_date), Q(approval_date__lte=to_date))
        if len(get_shipment) == 1 :
            get_shipment_id = [i.id for i in get_shipment][0]
            get_shipment = GrowerShipment.objects.get(id=get_shipment_id)
            processor_name = get_shipment.processor.entity_name
            processor_id = get_shipment.processor.id
            shipment_date = get_shipment.approval_date
            pounds_shipped = get_shipment.total_amount
            pounds_received = get_shipment.received_amount
            grower = get_shipment.grower.name
            field = get_shipment.field.name
            field_id = get_shipment.field.id
            get_field = Field.objects.get(id=field_id)
            farm = get_field.farm.name
            skuid = get_shipment.sku   # add sku_id
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":search_text,"skuid":skuid,"date":shipment_date,
                                    "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                    "grower":grower,"farm":farm,"field":field}])
    return return_lst

# 20-03-23
def outbound2_Wip_Grower(crop,check_grower_id,from_date,to_date,*grower_field_ids):
    grower_field_ids = list(grower_field_ids)
    return_lst = []
    if crop == 'COTTON' :
        pass
    if crop == 'RICE' :
        get_processor = GrowerShipment.objects.filter(grower_id=check_grower_id).values('processor_id')
        if get_processor.exists():
            processor_id = [i['processor_id'] for i in get_processor][0]
        else:
            processor_id = ''
        get_shipment = ShipmentManagement.objects.filter(processor_idd=processor_id).filter(Q(date_pulled__gte=from_date), Q(date_pulled__lte=to_date)).values('id').order_by('-id')
        for i in get_shipment :
            get_shipment = ShipmentManagement.objects.get(id=i['id'])
            purchase_order_number = get_shipment.purchase_order_number
            date_pulled = get_shipment.date_pulled
            volume_shipped = get_shipment.volume_shipped
            equipment_type = get_shipment.equipment_type
            bin_location = get_shipment.bin_location
            storage_skuid = get_shipment.storage_bin_send
            receiver_skuid = get_shipment.storage_bin_recive
            destination = get_shipment.processor2_name
            return_lst.extend([{"deliveryid":purchase_order_number,"storage_skuid":storage_skuid,"date":date_pulled,"quantity":volume_shipped,"transportation":equipment_type,"destination":destination}])
    return return_lst

def outbound2_Wip_Field(crop,field_name,field_id,from_date,to_date):
    return_lst = []
    if crop == 'COTTON' :
        pass
    if crop == 'RICE' :
        get_processor = GrowerShipment.objects.filter(field_id=field_id).values('processor_id')
        if get_processor.exists() :
            processor_id = [i['processor_id'] for i in get_processor][0]
        else:
            processor_id = ''
        get_shipment = ShipmentManagement.objects.filter(processor_idd=processor_id).filter(Q(date_pulled__gte=from_date), Q(date_pulled__lte=to_date)).values('id').order_by('-id')
        for i in get_shipment :
            get_shipment = ShipmentManagement.objects.get(id=i['id'])
            purchase_order_number = get_shipment.purchase_order_number
            date_pulled = get_shipment.date_pulled
            volume_shipped = get_shipment.volume_shipped
            equipment_type = get_shipment.equipment_type
            bin_location = get_shipment.bin_location
            storage_skuid = get_shipment.storage_bin_send  # add storage_bin
            return_lst.extend([{"deliveryid":purchase_order_number,"storage_skuid":storage_skuid,"date":date_pulled,"quantity":volume_shipped,"transportation":equipment_type,"destination":bin_location}])
    return return_lst

def outbound2_Wip_Processor(crop,search_text,processor_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        pass
    if crop == 'RICE' :
        get_processor = GrowerShipment.objects.filter(processor_id=processor_id).values('processor_id')
        processor_id = [i['processor_id'] for i in get_processor][0]
        get_shipment = ShipmentManagement.objects.filter(processor_idd=processor_id).filter(Q(date_pulled__gte=from_date), Q(date_pulled__lte=to_date)).values('id').order_by('-id')
        for i in get_shipment :
            get_shipment = ShipmentManagement.objects.get(id=i['id'])
            purchase_order_number = get_shipment.purchase_order_number
            date_pulled = get_shipment.date_pulled
            volume_shipped = get_shipment.volume_shipped
            equipment_type = get_shipment.equipment_type
            bin_location = get_shipment.bin_location
            storage_skuid = get_shipment.storage_bin_send
            receiver_skuid = get_shipment.storage_bin_recive
            equ_id = get_shipment.equipment_id
            destination = get_shipment.processor2_name
            return_lst.extend([{"deliveryid":purchase_order_number,"storage_skuid":storage_skuid,"date":date_pulled,"quantity":volume_shipped,"transportation":equipment_type,"destination":destination,"equ_id":equ_id}])
    return return_lst

def outbound2_Wip_deliveryid(crop,search_text,rice_shipment_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        pass
    if crop == 'RICE' :
        get_processor = GrowerShipment.objects.filter(shipment_id=rice_shipment_id).values('processor_id')
        processor_id = [i['processor_id'] for i in get_processor][0]
        get_shipment = ShipmentManagement.objects.filter(processor_idd=processor_id).filter(Q(date_pulled__gte=from_date), Q(date_pulled__lte=to_date)).values('id').order_by('-id')
        for i in get_shipment :
            get_shipment = ShipmentManagement.objects.get(id=i['id'])
            purchase_order_number = get_shipment.purchase_order_number
            date_pulled = get_shipment.date_pulled
            volume_shipped = get_shipment.volume_shipped
            equipment_type = get_shipment.equipment_type
            bin_location = get_shipment.bin_location
            storage_skuid = get_shipment.storage_bin_send  # add storage_bin
            return_lst.extend([{"deliveryid":purchase_order_number,"storage_skuid":storage_skuid,"date":date_pulled,"quantity":volume_shipped,"transportation":equipment_type,"destination":bin_location}])
    return return_lst

# 20-03-23
def t2_Processor_grower(crop,check_grower_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        bale = AssignedBaleProcessor2.objects.filter(grower_idd=check_grower_id).values("id")
        for i in bale :
            get_bale = AssignedBaleProcessor2.objects.get(id=i["id"])
            processor_name = get_bale.processor2.entity_name
            processor_id = get_bale.processor2.id
            deliveryid = get_bale.assigned_bale
            dt_class = get_bale.dt_class
            if dt_class :
                str_date = str(dt_class)
                if '-' in str_date :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        continue
                elif '/' in str_date :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        continue
                else:
                    continue
            else:
                continue
            pounds_shipped = get_bale.net_wt
            pounds_received = get_bale.net_wt
            grower = get_bale.grower_name
            field = get_bale.field_name
            field_id = get_bale.field_idd
            farm = ''
            if field_id :
                try:
                    get_field = Field.objects.get(id=field_id)
                    farm = get_field.farm.name
                except:
                    farm = ''
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,
                                "grower":grower,"farm":farm,"field":field,"date":dt_class,"pounds_shipped":pounds_shipped,
                                "pounds_received":pounds_received,"pounds_delta":pounds_delta}])
    if crop == 'RICE' :
        # pass
    #     get_shipment = GrowerShipment.objects.filter(grower_id=check_grower_id,status="APPROVED").values("id")
    #     for i in get_shipment :
    #         get_shipment = GrowerShipment.objects.get(id=i["id"])
    #         processor_name = get_shipment.processor.entity_name
    #         processor_id = get_shipment.processor.id
    #         deliveryid = get_shipment.shipment_id
    #         dt_class = get_shipment.approval_date
    #         pounds_shipped = get_shipment.total_amount
    #         pounds_received = get_shipment.received_amount
   
    #         pounds_delta = ''
    #         try:
    #             pounds_delta = float(pounds_shipped) - float(pounds_received)
    #         except:
    #             pounds_delta = ''
    #         return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":dt_class,
    #                             "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,}])
    # return return_lst
        
        get_grower = GrowerShipment.objects.filter(grower_id=check_grower_id,status="APPROVED")
        if get_grower.exists():
            shipment = ShipmentManagement.objects.all()
            for i in range(len(shipment)):
                var = shipment[i].storage_bin_send
                grower_shipment = GrowerShipment.objects.filter(sku = var).filter(grower_id=check_grower_id)
                for r in grower_shipment :
                    del_id = r.shipment_id
                    shipment_date = r.approval_date
                    get_shipment = ShipmentManagement.objects.get(storage_bin_send=var)
                    processor_id = get_shipment.processor2_idd
                    processor_name = get_shipment.processor2_name
                    sku_id = get_shipment._send
                    pounds_shipped = r.total_amount
                    pounds_received = r.received_amount
                    pounds_delta = ''
                    try:
                        pounds_delta = float(pounds_shipped) - float(pounds_received)
                    except:
                        pounds_delta = ''
                    return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":del_id,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,"skuid":sku_id}])

        return return_lst
    

def t2_Processor_field(crop,field_name,field_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        get_bale = AssignedBaleProcessor2.objects.filter(field_name=field_name,field_idd=field_id).values("id")
        if get_bale.exists() :
            for i in get_bale :
                get_bale_id = i["id"]
                get_bale = AssignedBaleProcessor2.objects.get(id=get_bale_id)
                processor_id = get_bale.processor2.id
                processor_name = get_bale.processor2.entity_name
                deliveryid = get_bale.assigned_bale
                shipment_date = get_bale.dt_class
                dt_class = get_bale.dt_class
                if dt_class :
                    str_date = str(dt_class)
                    if '-' in str_date :
                        str_date = str_date.split('-')
                        mm = str_date[0]
                        dd = str_date[1]
                        yy = str_date[2]
                        yyyy = f'20{yy}' if len(yy) == 2 else yy
                        finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                        from_date = str(from_date).replace('-','/')
                        to_date = str(to_date).replace('-','/')
                        format = '%Y/%m/%d'
                        # convert from string format to datetime format
                        from_date = datetime.datetime.strptime(from_date, format).date()
                        to_date = datetime.datetime.strptime(to_date, format).date()

                        if finale_date >= from_date and finale_date <= to_date:
                            res = True
                            print("res",res)
                        else:
                            continue
                    elif '/' in str_date :
                        str_date = str_date.split('/')
                        mm = str_date[0]
                        dd = str_date[1]
                        yy = str_date[2]
                        yyyy = f'20{yy}' if len(yy) == 2 else yy
                        finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                        from_date = str(from_date).replace('-','/')
                        to_date = str(to_date).replace('-','/')
                        format = '%Y/%m/%d'
                        # convert from string format to datetime format
                        from_date = datetime.datetime.strptime(from_date, format).date()
                        to_date = datetime.datetime.strptime(to_date, format).date()

                        if finale_date >= from_date and finale_date <= to_date:
                            res = True
                            print("res",res)
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
                pounds_shipped = get_bale.net_wt
                pounds_received = get_bale.net_wt
                grower = get_bale.grower_name
                field = get_bale.field_name
                field_id = get_bale.field_idd
                farm = ''
                if field_id :
                    try:
                        get_field = Field.objects.get(id=field_id)
                        farm = get_field.farm.name
                    except:
                        farm = ''
                pounds_delta = ''
                try:
                    pounds_delta = float(pounds_shipped) - float(pounds_received)
                except:
                    pounds_delta = ''
                return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":shipment_date,
                                    "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                    "grower":grower,"farm":farm,"field":field}])
    if crop == 'RICE' :
        pass
    #     get_shipment = GrowerShipment.objects.filter(field_id=field_id,status="APPROVED").values("id")
    #     if get_shipment.exists :
    #         for i in get_shipment :
    #             get_shipment_id = i["id"]
    #             get_shipment = GrowerShipment.objects.get(id=get_shipment_id)
    #             processor_name = get_shipment.processor.entity_name
    #             processor_id = get_shipment.processor.id
    #             shipment_date = get_shipment.approval_date
    #             deliveryid = get_shipment.shipment_id
    #             pounds_shipped = get_shipment.total_amount
    #             pounds_received = get_shipment.received_amount
    #             pounds_delta = ''
    #             try:
    #                 pounds_delta = float(pounds_shipped) - float(pounds_received)
    #             except:
    #                 pounds_delta = ''
    #             return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":shipment_date,
    #                                 "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta}])
    # return return_lst
    
        get_shipment_data = GrowerShipment.objects.filter(field_id=field_id,status="APPROVED")
        if get_shipment_data.exists():    
            shipment = ShipmentManagement.objects.all()
            for i in range(len(shipment)):
                var = shipment[i].storage_bin_send
                grower_shipment = GrowerShipment.objects.filter(sku = var).filter(field_id=field_id)
                for r in grower_shipment :
                    del_id = r.shipment_id
                    shipment_date = r.approval_date
                    get_shipment = ShipmentManagement.objects.get(storage_bin_send=var)
                    processor_id = get_shipment.processor2_idd
                    processor_name = get_shipment.processor2_name
                    sku_id = get_shipment.storage_bin_send
                    pounds_shipped = r.total_amount
                    pounds_received = r.received_amount
                    pounds_delta = ''
                    try:
                        pounds_delta = float(pounds_shipped) - float(pounds_received)
                    except:
                        pounds_delta = ''
                    return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":del_id,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,"skuid":sku_id}])

        return return_lst

def t2_Processor_Processor(crop,processor_id,from_date,to_date,*bale_id) :
    return_lst = []
    if crop == 'COTTON' :
        bale_id = list(bale_id)
        check_bale = AssignedBaleProcessor2.objects.filter(bale_id__in=bale_id).values('id')
        for i in check_bale :
            get_bale = AssignedBaleProcessor2.objects.get(id=i['id'])
            processor_id = get_bale.processor2.id
            processor_name = get_bale.processor2.entity_name
            deliveryid = get_bale.assigned_bale
            shipment_date = get_bale.dt_class
            dt_class = get_bale.dt_class
            if dt_class :
                str_date = str(dt_class)
                if '-' in str_date :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        continue
                elif '/' in str_date :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        continue
                else:
                    continue
            else:
                continue
            pounds_shipped = get_bale.net_wt
            pounds_received = get_bale.net_wt
            grower = get_bale.grower_name
            field = get_bale.field_name
            field_id = get_bale.field_idd
            farm = ''
            if field_id :
                try:
                    get_field = Field.objects.get(id=field_id)
                    farm = get_field.farm.name
                except:
                    farm = ''
            pounds_delta = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                "grower":grower,"farm":farm,"field":field}])
    if crop == 'RICE' :
        # pass
        # check_shipment = list(bale_id)
        # get_shipment = GrowerShipment.objects.filter(id__in=check_shipment,status='APPROVED').values('id')
        # for i in get_shipment :
            # get_shipment = GrowerShipment.objects.get(id=i['id'])
            # processor_name = get_shipment.processor.entity_name
            # processor_id = get_shipment.processor.id
            # shipment_date = get_shipment.approval_date
            # deliveryid = get_shipment.shipment_id
            # pounds_shipped = get_shipment.total_amount
            # pounds_received = get_shipment.received_amount
            # pounds_delta = ''

            # try:
            #     pounds_delta = float(pounds_shipped) - float(pounds_received)
            # except:
            #     pounds_delta = ''
            # return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":deliveryid,"date":shipment_date,
            #                 "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,"skuid":skuid}])
        
        
        check_shipment = list(bale_id)
        get_shipment_data = GrowerShipment.objects.filter(id__in=check_shipment,status='APPROVED')
        if get_shipment_data.exists():
            # shipment = ShipmentManagement.objects.all()
            shipment = ShipmentManagement.objects.filter(processor_idd = processor_id)
            # print("shipment============",shipment)
            for i in range(len(shipment)):
                var = shipment[i].storage_bin_send
                grower_shipment = GrowerShipment.objects.filter(sku = var)
                for r in grower_shipment :
                    del_id = r.shipment_id
                    shipment_date = r.approval_date
                    get_shipment = ShipmentManagement.objects.get(storage_bin_send=var)
                    processor_id = get_shipment.processor2_idd
                    processor_name = get_shipment.processor2_name
                    sku_id = get_shipment.storage_bin_send
                    pounds_shipped = r.total_amount
                    pounds_received = r.received_amount
                    pounds_delta = ''
                    try:
                        pounds_delta = float(pounds_shipped) - float(pounds_received)
                    except:
                        pounds_delta = ''
                    return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":del_id,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,"skuid":sku_id}])
        
        return return_lst

def t3_Processor_Processor(crop,processor_id,from_date,to_date,*bale_id) :
    return_lst = []
    if crop == 'RICE' :
        
        check_shipment = list(bale_id)
        get_shipment_data = ShipmentManagement.objects.filter(id__in=check_shipment,status='APPROVED')
        if get_shipment_data.exists():
            # shipment = ShipmentManagement.objects.all()
            shipment = ShipmentManagement.objects.filter(processor_idd = processor_id)
            # print("shipment============",shipment)
            for i in range(len(shipment)):
                var = shipment[i].storage_bin_recive
                grower_shipment = ShipmentManagement.objects.filter(storage_bin_send = var)
                for r in grower_shipment :
                    del_id = r.shipment_id
                    shipment_date = r.approval_date
                    get_shipment = ShipmentManagement.objects.get(storage_bin_send=var)
                    processor_id = get_shipment.processor2_idd
                    processor_name = get_shipment.processor2_name
                    sku_id = get_shipment.storage_bin_send
                    pounds_shipped = r.total_amount
                    pounds_received = r.received_amount
                    pounds_delta = ''
                    try:
                        pounds_delta = float(pounds_shipped) - float(pounds_received)
                    except:
                        pounds_delta = ''
                    return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":del_id,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,"skuid":sku_id}])
        
            return return_lst

def t2_Processor_deliveryid(crop,search_text,warehouse_wh_id,from_date,to_date) :
    return_lst = []
    if crop == 'COTTON' :
        get_bale = AssignedBaleProcessor2.objects.filter(assigned_bale=search_text,warehouse_wh_id=warehouse_wh_id)
        if len(get_bale) == 1 :
            get_bale_id = [i.id for i in get_bale][0]
            get_bale = AssignedBaleProcessor2.objects.get(id=get_bale_id)
            processor_name = get_bale.processor2.entity_name
            processor_id = get_bale.processor2.id
            dt_class = get_bale.dt_class
            if dt_class :
                str_date = str(dt_class)
                if '-' in str_date :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        return return_lst
                elif '/' in str_date :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = datetime.date(int(yyyy), int(mm), int(dd))
                    from_date = str(from_date).replace('-','/')
                    to_date = str(to_date).replace('-','/')
                    format = '%Y/%m/%d'
                    # convert from string format to datetime format
                    from_date = datetime.datetime.strptime(from_date, format).date()
                    to_date = datetime.datetime.strptime(to_date, format).date()

                    if finale_date >= from_date and finale_date <= to_date:
                        res = True
                        print("res",res)
                    else:
                        return return_lst
                else:
                    return return_lst
            else:
                return return_lst
            pounds_shipped = get_bale.net_wt
            pounds_received = get_bale.net_wt
            grower = get_bale.grower_name
            field = get_bale.field_name
            field_id = get_bale.field_idd
            farm = ''
            if field_id :
                try:
                    get_field = Field.objects.get(id=field_id)
                    farm = get_field.farm.name
                except:
                    farm = ''
            try:
                pounds_delta = float(pounds_shipped) - float(pounds_received)
            except:
                pounds_delta = ''
            return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":search_text,"date":dt_class,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,
                                "grower":grower,"farm":farm,"field":field}])
    if crop == 'RICE' :
        # pass
    #     get_shipment = GrowerShipment.objects.filter(shipment_id=search_text,status="APPROVED")
    #     if len(get_shipment) == 1 :
    #         get_shipment_id = [i.id for i in get_shipment][0]
    #         get_shipment = GrowerShipment.objects.get(id=get_shipment_id)
    #         processor_name = get_shipment.processor.entity_name
    #         processor_id = get_shipment.processor.id
    #         shipment_date = get_shipment.approval_date
    #         pounds_shipped = get_shipment.total_amount
    #         pounds_received = get_shipment.received_amount
    #         pounds_delta = ''

    #         try:
    #             pounds_delta = float(pounds_shipped) - float(pounds_received)
    #         except:
    #             pounds_delta = ''
    #         return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":search_text,"date":shipment_date,
    #                                 "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta}])
    # return return_lst
    
        get_shipment_data = GrowerShipment.objects.filter(shipment_id=search_text,status="APPROVED")
        if get_shipment_data.exists():    
            shipment = ShipmentManagement.objects.all()
            for i in range(len(shipment)):
                var = shipment[i].storage_bin_send
                grower_shipment = GrowerShipment.objects.filter(sku = var,).filter(shipment_id=search_text)
                for r in grower_shipment :
                    del_id = r.shipment_id
                    shipment_date = r.approval_date
                    get_shipment = ShipmentManagement.objects.get(storage_bin_send=var)
                    processor_id = get_shipment.processor2_idd
                    processor_name = get_shipment.processor2_name
                    sku_id = get_shipment.storage_bin_send
                    pounds_shipped = r.total_amount
                    pounds_received = r.received_amount
                    pounds_delta = ''
                    try:
                        pounds_delta = float(pounds_shipped) - float(pounds_received)
                    except:
                        pounds_delta = ''
                    return_lst.extend([{"processor_name":processor_name,"processor_id":processor_id,"deliveryid":del_id,"date":shipment_date,
                                "pounds_shipped":pounds_shipped,"pounds_received":pounds_received,"pounds_delta":pounds_delta,"skuid":sku_id}])

        return return_lst
    


@login_required()
def traceability_report_list(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        if request.method == 'POST':
            select_crop= request.POST.get('select_crop')
            crop_year= request.POST.get('crop_year')
            from_date= request.POST.get('from_date')
            to_date= request.POST.get('to_date')
            search_text= request.POST.get('search_text')
            get_search_by= request.POST.get('get_search_by')
            if select_crop and crop_year and from_date and to_date and search_text :
                context['select_crop'] = select_crop
                context['crop_year'] = crop_year
                context['from_date'] = from_date
                context['to_date'] = to_date
                context['search_text'] = search_text
                context['get_search_by'] = get_search_by
                # crop == 'COTTON'
                if select_crop == 'COTTON' :
                    # Origin ........
                    # priority order [grower,field,processor, delivery id]
                    # search by Grower ....
                    if get_search_by and get_search_by == 'grower' :
                        check_grower = Grower.objects.filter(name__icontains=search_text)
                        if check_grower.exists() :
                            check_grower_id = [i.id for i in check_grower][0]
                            check_grower_field_crop = Field.objects.filter(crop='COTTON',grower_id=check_grower_id)
                            if check_grower_field_crop.exists() :
                                grower_field_ids = [i.id for i in check_grower_field_crop]
                                get_Origin_Grower = Origin_searchby_Grower('COTTON',search_text,*grower_field_ids)         
                                context["origin_context"] = get_Origin_Grower
                                context["search_by"] = "grower"
                                outbound1_wip = outbound1_Wip_Grower('COTTON',search_text,from_date,to_date,*grower_field_ids)         
                                context["outbound1_wip"] = outbound1_wip
                                t1_processor = t1_Processor_grower('COTTON',check_grower_id,from_date,to_date)
                                context["t1_processor"] = t1_processor
                                # 20-03-23
                                outbound2_wip = outbound2_Wip_Grower('COTTON',check_grower_id,from_date,to_date,*grower_field_ids)         
                                context["outbound2_wip"] = outbound2_wip
                                t2_processor = t2_Processor_grower('COTTON',check_grower_id,from_date,to_date)
                                context["t2_processor"] = t2_processor
                            else:
                                context['no_rec_found_msg'] = "No Records Found"
                        else:
                            context['no_rec_found_msg'] = "No Records Found"
                    # search by Field ....
                    elif get_search_by and get_search_by == 'field' :
                        check_field = Field.objects.filter(name__icontains=search_text,crop='COTTON')
                        if check_field.exists() :
                            field_id = [i.id for i in check_field][0]
                            field_name = [i.name for i in check_field][0]
                            warehouse_wh_id = ''
                            get_origin_details = get_Origin_deliveryid('COTTON',field_id,field_name,'',warehouse_wh_id)
                            context["origin_context"] = get_origin_details
                            context["search_by"] = "field"
                            outbound1_wip = outbound1_Wip_field('COTTON',search_text,from_date,to_date,field_id)
                            context["outbound1_wip"] = outbound1_wip
                            t1_processor = t1_Processor_field('COTTON',field_name,field_id,field_id,from_date,to_date)
                            context["t1_processor"] = t1_processor
                            # 20-03-23
                            outbound2_wip = outbound2_Wip_Field('COTTON',field_name,field_id,from_date,to_date)         
                            context["outbound2_wip"] = outbound2_wip
                            t2_processor = t2_Processor_field('COTTON',field_name,field_id,from_date,to_date)
                            context["t2_processor"] = t2_processor
                        else:
                            context['no_rec_found_msg'] = "No Records Found"
                    # search by Processor ....
                    elif get_search_by and get_search_by == 'processor' :
                        check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                        if check_processor.exists() :
                            processor_id = [i.id for i in check_processor][0]
                            get_classing = ClassingReport.objects.filter(processor_id=processor_id).values("id")
                            classing_id = [i["id"] for i in get_classing]
                            bale= BaleReportFarmField.objects.filter(classing_id__in=classing_id).values("id")
                            if bale.exists() :
                                bale_id = [i["id"] for i in bale]
                                get_Origin_Processor = Origin_searchby_Processor('COTTON',search_text,*bale_id)         
                                context["origin_context"] = get_Origin_Processor
                                context["search_by"] = "processor"
                                t1_processor = t1_Processor_Processor('COTTON',processor_id,from_date,to_date,*bale_id)
                                context["t1_processor"] = t1_processor
                                # 20-03-23
                                outbound2_wip = outbound2_Wip_Processor('COTTON',search_text,processor_id,from_date,to_date)         
                                context["outbound2_wip"] = outbound2_wip
                                t2_processor =  t2_Processor_Processor('COTTON',processor_id,from_date,to_date,*bale_id) 
                                context["t2_processor"] = t2_processor
                            else:
                                context['no_rec_found_msg'] = "No Records Found"
                        else:
                            context['no_rec_found_msg'] = "No Records Found"
                    # search by Delivery ID ....
                    elif get_search_by and get_search_by == 'deliveryid' :
                        get_delivery_id1 = BaleReportFarmField.objects.filter(bale_id__icontains=search_text)
                        get_delivery_id2 = BaleReportFarmField.objects.filter(bale_id__icontains=f"0{search_text}")
                        if get_delivery_id1.exists() :
                            field_id = [i.ob4 for i in get_delivery_id1][0]
                            field_name = [i.field_name for i in get_delivery_id1][0]
                            warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id1][0]
                            get_origin_details = get_Origin_deliveryid('COTTON',field_id,field_name,search_text,warehouse_wh_id)
                            context["origin_context"] = get_origin_details
                            context["search_by"] = "bale_id"
                            # outbound1_wip = outbound1_Wip_deliveryid('COTTON',search_text,warehouse_wh_id)
                            # context["outbound1_wip"] = outbound1_wip
                            t1_processor = t1_Processor_deliveryid('COTTON',search_text,warehouse_wh_id,from_date,to_date)
                            context["t1_processor"] = t1_processor
                            t2_processor =  t2_Processor_deliveryid('COTTON',search_text,warehouse_wh_id,from_date,to_date)
                            context["t2_processor"] = t2_processor
                        elif get_delivery_id2.exists() :
                            field_id = [i.ob4 for i in get_delivery_id2][0]
                            field_name = [i.field_name for i in get_delivery_id2][0]
                            warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id2][0]
                            get_origin_details = get_Origin_deliveryid('COTTON',field_id,field_name,f"0{search_text}",warehouse_wh_id)
                            context["origin_context"] = get_origin_details
                            context["search_by"] = "bale_id"
                            # outbound1_wip = outbound1_Wip_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id)
                            # context["outbound1_wip"] = outbound1_wip
                            t1_processor = t1_Processor_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id,from_date,to_date)
                            context["t1_processor"] = t1_processor  
                            t2_processor =  t2_Processor_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id,from_date,to_date)
                            context["t2_processor"] = t2_processor
                        else:
                            context['no_rec_found_msg'] = "No Records Found"                   
                    else:
                        context['no_rec_found_msg'] = "No Records Found"
                    
                # crop == 'RICE'
                if select_crop == 'RICE' :
                    # Origin ........
                    # search by Grower ....
                    if get_search_by and get_search_by == 'grower' :
                        check_grower = Grower.objects.filter(name__icontains=search_text)
                        if check_grower.exists() :
                            check_grower_id = [i.id for i in check_grower][0]
                            check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                            if check_grower_field_crop.exists() :
                                grower_field_ids = [i.id for i in check_grower_field_crop]
                                get_Origin_Grower = Origin_searchby_Grower('RICE',search_text,*grower_field_ids)                                              
                                context["origin_context"] = get_Origin_Grower
                                context["search_by"] = "grower"
                                outbound1_wip = outbound1_Wip_Grower('RICE',search_text,from_date,to_date,*grower_field_ids)         
                                context["outbound1_wip"] = outbound1_wip
                                t1_processor = t1_Processor_grower('RICE',check_grower_id,from_date,to_date)
                                context["t1_processor"] = t1_processor
                                # 20-03-23
                                outbound2_wip = outbound2_Wip_Grower('RICE',check_grower_id,from_date,to_date,*grower_field_ids)         
                                context["outbound2_wip"] = outbound2_wip
                                t2_processor = t2_Processor_grower('RICE',check_grower_id,from_date,to_date)
                                context["t2_processor"] = t2_processor
                            else:
                                context['no_rec_found_msg'] = "No Records Found"
                        else:
                            context['no_rec_found_msg'] = "No Records Found"
                    # search by Field ....
                    elif get_search_by and get_search_by == 'field' :
                        check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                        if check_field.exists() :
                            field_name = search_text
                            field_id = [i.id for i in check_field][0]
                            warehouse_wh_id = ''
                            get_origin_details = get_Origin_deliveryid('RICE',field_id,field_name,'',warehouse_wh_id)
                            context["origin_context"] = get_origin_details
                            context["search_by"] = "field"
                            outbound1_wip = outbound1_Wip_field('RICE',search_text,from_date,to_date,field_id)
                            context["outbound1_wip"] = outbound1_wip
                            t1_processor = t1_Processor_field('RICE',search_text,field_id,from_date,to_date)
                            context["t1_processor"] = t1_processor
                            # 20-03-23
                            outbound2_wip = outbound2_Wip_Field('RICE',field_name,field_id,from_date,to_date)         
                            context["outbound2_wip"] = outbound2_wip
                            t2_processor = t2_Processor_field('RICE',field_name,field_id,from_date,to_date)
                            context["t2_processor"] = t2_processor
                        else:
                            context['no_rec_found_msg'] = "No Records Found"
                    # search by Processor ....
                    elif get_search_by and get_search_by == 'processor' :
                        check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                        if check_processor.exists() :
                            processor_id = [i.id for i in check_processor][0]
                            get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                            if get_shipment.exists() :
                                bale_id = [i["id"] for i in get_shipment]  
                                get_Origin_Processor = Origin_searchby_Processor('RICE',search_text,*bale_id)    
                                context["origin_context"] = get_Origin_Processor
                                context["search_by"] = "processor"
                                outbound1_wip = outbound1_Wip_Processor('RICE',from_date,to_date,processor_id)
                                context["outbound1_wip"] = outbound1_wip
                                t1_processor = t1_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id)
                                context["t1_processor"] = t1_processor
                                # 20-03-23
                                outbound2_wip = outbound2_Wip_Processor('RICE',search_text,processor_id,from_date,to_date)         
                                context["outbound2_wip"] = outbound2_wip
                                t2_processor =  t2_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id) 
                                context["t2_processor"] = t2_processor
                                # t3_processor =  t3_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id) 
                                # context["t3_processor"] = t3_processor
                            else:
                                context['no_rec_found_msg'] = "No Records Found"
                        else:
                            context['no_rec_found_msg'] = "No Records Found"
                    # search by Delivery ID ....
                    elif get_search_by and get_search_by == 'deliveryid' :
                        get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                        if get_delivery_id3.exists() :
                            rice_shipment_id = [i.shipment_id for i in get_delivery_id3][0]
                            field_id = [i.field.id for i in get_delivery_id3][0]
                            field_name = [i.field.name for i in get_delivery_id3][0]
                            warehouse_wh_id = ''
                            get_origin_details = get_Origin_deliveryid('RICE',field_id,field_name,search_text,warehouse_wh_id)
                            context["origin_context"] = get_origin_details
                            context["search_by"] = "shipment_id"
                            outbound1_wip = outbound1_Wip_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
                            context["outbound1_wip"] = outbound1_wip
                            t1_processor = t1_Processor_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
                            context["t1_processor"] = t1_processor
                            # 20-03-23
                            outbound2_wip = outbound2_Wip_deliveryid('RICE',search_text,rice_shipment_id,from_date,to_date)         
                            context["outbound2_wip"] = outbound2_wip
                            t2_processor =  t2_Processor_deliveryid('RICE',search_text,warehouse_wh_id,from_date,to_date)
                            context["t2_processor"] = t2_processor
                        else:
                            context['no_rec_found_msg'] = "No Records Found"     
                    else:
                        context['no_rec_found_msg'] = "No Records Found"
                          
        return render (request, 'tracemodule/traceability_report_list.html', context)
    else:
        return redirect ('dashboard')


@login_required()
def autocomplete_suggestions(request,select_search,select_crop_id):
    lst =[]
    if select_search == 'grower' :
        grower_name = Grower.objects.all().order_by('name').values('name')
        lst = [i['name'] for i in grower_name]
    elif select_search == 'field' : 
        field_name = Field.objects.all().order_by('name').values('name')
        lst = [i['name'] for i in field_name]
    elif select_search == 'processor' :    
        processor_name = list(Processor.objects.all().order_by('entity_name').values_list('entity_name', flat=True))
        processor2_name = list(Processor2.objects.all().order_by('entity_name').values_list('entity_name', flat=True))
        lst = processor_name + processor2_name    
    elif select_search == 'deliveryid' :
        if select_crop_id == 'RICE' :
            deliveryid = GrowerShipment.objects.all().order_by('shipment_id').values('shipment_id')
            lst = [i['shipment_id'] for i in deliveryid]
        elif select_crop_id == 'COTTON' :
            deliveryid = BaleReportFarmField.objects.all().order_by('bale_id').values('bale_id')
            lst = [i['bale_id'] for i in deliveryid]

    responce = {'select_search':lst}
    print(responce)
    return JsonResponse(responce)

@login_required()
def showsustainability_metrics(request,get_search_by,field_id):
    get_field = Field.objects.get(id=field_id)
    if get_search_by == 'bale_id' :
        pass
    elif get_search_by == 'shipment_id' :
        pass
    elif get_search_by == 'field' :
        pass
    elif get_search_by == 'grower' :
        pass
    harvest_date = get_field.harvest_date if get_field.harvest_date else ''
    water_savings = get_field.gal_water_saved if get_field.gal_water_saved else ''
    water_per_pound_savings = get_field.water_lbs_saved if get_field.water_lbs_saved else ''
    land_use = get_field.land_use_efficiency if get_field.land_use_efficiency else ''
    less_GHG = get_field.ghg_reduction if get_field.ghg_reduction else ''
    co2_eQ_footprint = get_field.co2_eq_reduced if get_field.co2_eq_reduced else ''
    premiums_to_growers = get_field.grower_premium_percentage if get_field.grower_premium_percentage else ''

    
    crop = get_field.crop
    surveyscore1 = get_field.get_survey1()
    surveyscore2 = get_field.get_survey2()
    surveyscore3 = get_field.get_survey3()
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
    composite_score = round((surveyscore1*0.25)+(surveyscore2*0.50)+(surveyscore3*0.25),2)
    if crop == "RICE":
        if composite_score >= 70:
            pf_sus = "Pass"
        elif composite_score < 70:
            pf_sus = "Fail"
    elif crop == "COTTON":
        if composite_score >= 75:
            pf_sus = "Pass"
        elif composite_score < 75:
            pf_sus = "Fail"
 
    
    responce = {"pf_sus":pf_sus,"harvest_date":harvest_date,"water_savings":water_savings,"water_per_pound_savings":water_per_pound_savings,
                "land_use":land_use,"less_GHG":less_GHG,"co2_eQ_footprint":co2_eQ_footprint,"premiums_to_growers":premiums_to_growers}
    return JsonResponse(responce)

@login_required()
def showquality_metrics(request,get_search_by,delivery_idd):
    responce = {}
    level, grade, leaf, staple, length, strength, mic = '', '', '', '', '', '', ''
    bale1 = BaleReportFarmField.objects.filter(bale_id=delivery_idd)
    bale2 = BaleReportFarmField.objects.filter(bale_id=f'0{delivery_idd}')
    shipment = GrowerShipment.objects.filter(shipment_id=delivery_idd)
    if len(bale1) == 1 :
        bale1_id = [i.id for i in bale1][0]
        bale1 = BaleReportFarmField.objects.get(id=bale1_id)
        grade = bale1.gr
        leaf = bale1.lf
        staple = bale1.st
        length = bale1.len_num
        strength = bale1.str_no
        mic = bale1.mic
        level = bale1.level
    elif len(bale2) == 1 :
        bale2_id = [i.id for i in bale2][0]
        bale2 = BaleReportFarmField.objects.get(id=bale2_id)
        grade = bale2.gr
        leaf = bale2.lf
        staple = bale2.st
        length = bale2.len_num
        strength = bale2.str_no
        mic = bale2.mic
        level = bale2.level
    elif len(shipment) == 1 :
        pass
    
    
    responce = {"level":level,"grade":grade,"leaf":leaf,"staple":staple,"length":length,"strength":strength,"mic":mic}
    
    return JsonResponse(responce)




@login_required()
def traceability_report_Origin_csv_download(request,select_crop,get_search_by,search_text,from_date,to_date):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'Origin.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        if select_crop == 'COTTON' :
            writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                            'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                            'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
            
            
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='COTTON',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        grower_field_ids = [i.id for i in check_grower_field_crop]
                        output = Origin_searchby_Grower('COTTON',search_text,*grower_field_ids)         
                                        
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='COTTON')
                if check_field.exists() :
                    field_id = [i.id for i in check_field][0]
                    field_name = [i.name for i in check_field][0]
                    warehouse_wh_id = ''
                    output = get_Origin_deliveryid('COTTON',field_id,field_name,'',warehouse_wh_id)
                                        
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_classing = ClassingReport.objects.filter(processor_id=processor_id).values("id")
                    classing_id = [i["id"] for i in get_classing]
                    bale= BaleReportFarmField.objects.filter(classing_id__in=classing_id).values("id")
                    if bale.exists() :
                        bale_id = [i["id"] for i in bale]
                        output = Origin_searchby_Processor('COTTON',search_text,*bale_id)         
                               
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id1 = BaleReportFarmField.objects.filter(bale_id__icontains=search_text)
                get_delivery_id2 = BaleReportFarmField.objects.filter(bale_id__icontains=f"0{search_text}")
                if get_delivery_id1.exists() :
                    field_id = [i.ob4 for i in get_delivery_id1][0]
                    field_name = [i.field_name for i in get_delivery_id1][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id1][0]
                    output = get_Origin_deliveryid('COTTON',field_id,field_name,search_text,warehouse_wh_id)
                    
                elif get_delivery_id2.exists() :
                    field_id = [i.ob4 for i in get_delivery_id2][0]
                    field_name = [i.field_name for i in get_delivery_id2][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id2][0]
                    output = get_Origin_deliveryid('COTTON',field_id,field_name,f"0{search_text}",warehouse_wh_id)
            else:
                output = []
            for i in output:
                writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                i["co2_eQ_footprint"],i["water_per_pound_savings"]])
        # crop rice
        if select_crop == 'RICE' :
            writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                            'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                            'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
            
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        grower_field_ids = [i.id for i in check_grower_field_crop]
                        output = Origin_searchby_Grower('RICE',search_text,*grower_field_ids)                                              
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                if check_field.exists() :
                    field_name = search_text
                    field_id = [i.id for i in check_field][0]
                    warehouse_wh_id = ''
                    output = get_Origin_deliveryid('RICE',field_id,field_name,'',warehouse_wh_id)
                    
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                    if get_shipment.exists() :
                        bale_id = [i["id"] for i in get_shipment]
                        output = Origin_searchby_Processor('RICE',search_text,*bale_id)         
                        
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                if get_delivery_id3.exists() :
                    field_id = [i.field.id for i in get_delivery_id3][0]
                    field_name = [i.field.name for i in get_delivery_id3][0]
                    warehouse_wh_id = ''
                    output = get_Origin_deliveryid('RICE',field_id,field_name,search_text,warehouse_wh_id)
            else:
                output = []
            for i in output:
                writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                i["co2_eQ_footprint"],i["water_per_pound_savings"]])
        
        return response
    else:
        return redirect ('dashboard')

@login_required()
def traceability_report_WIP1_csv_download(request,select_crop,get_search_by,search_text,from_date,to_date):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'Outbound 1 WIP.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        if select_crop == 'COTTON' :
            pass
        if select_crop == 'RICE' :
            writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        grower_field_ids = [i.id for i in check_grower_field_crop]
                        output = outbound1_Wip_Grower('RICE',search_text,from_date,to_date,*grower_field_ids)         
            
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                if check_field.exists() :
                    field_name = search_text
                    field_id = [i.id for i in check_field][0]                   
                    output = outbound1_Wip_field('RICE',search_text,from_date,to_date,field_id)
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                    if get_shipment.exists() :
                        bale_id = [i["id"] for i in get_shipment]
                        output = outbound1_Wip_Processor('RICE',from_date,to_date,processor_id)
                        
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                if get_delivery_id3.exists() :
                    rice_shipment_id = [i.shipment_id for i in get_delivery_id3][0]
                    field_id = [i.field.id for i in get_delivery_id3][0]
                    field_name = [i.field.name for i in get_delivery_id3][0]
                    warehouse_wh_id = ''
                    output = outbound1_Wip_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
            else:
                output = []
            for i in output:
                writer.writerow([i["deliveryid"], i["date"], i["quantity"], i["transportation"], i["destination"]])
        return response
    else:
        return redirect ('dashboard')

@login_required()
def traceability_report_T1_Processor_csv_download(request,select_crop,get_search_by,search_text,from_date,to_date):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'T1 Processor.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        if select_crop == 'COTTON' :
            writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                             'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='COTTON',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        
                        output = t1_Processor_grower('COTTON',check_grower_id,from_date,to_date)        
                                        
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='COTTON')
                if check_field.exists() :
                    field_id = [i.id for i in check_field][0]
                    field_name = [i.name for i in check_field][0]
                    warehouse_wh_id = ''
                    output = t1_Processor_field('COTTON',field_name,field_id,from_date,to_date)
   

            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_classing = ClassingReport.objects.filter(processor_id=processor_id).values("id")
                    classing_id = [i["id"] for i in get_classing]
                    bale= BaleReportFarmField.objects.filter(classing_id__in=classing_id).values("id")
                    if bale.exists() :
                        bale_id = [i["id"] for i in bale]
                        output = t1_Processor_Processor('COTTON',processor_id,from_date,to_date,*bale_id)
                  
               
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id1 = BaleReportFarmField.objects.filter(bale_id__icontains=search_text)
                get_delivery_id2 = BaleReportFarmField.objects.filter(bale_id__icontains=f"0{search_text}")
                if get_delivery_id1.exists() :
                    field_id = [i.ob4 for i in get_delivery_id1][0]
                    field_name = [i.field_name for i in get_delivery_id1][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id1][0]
                    output = t1_Processor_deliveryid('COTTON',search_text,warehouse_wh_id,from_date,to_date)

                elif get_delivery_id2.exists() :
                    field_id = [i.ob4 for i in get_delivery_id2][0]
                    field_name = [i.field_name for i in get_delivery_id2][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id2][0]                    
                    output = t1_Processor_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id,from_date,to_date)

            else:
                output = []
            for i in output:
                writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                 i["pounds_received"], i["pounds_delta"]])
            
        if select_crop == 'RICE' :
            writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                             'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        output = t1_Processor_grower('RICE',check_grower_id,from_date,to_date)
       
            
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                if check_field.exists() :
                    field_name = search_text
                    field_id = [i.id for i in check_field][0]
                    warehouse_wh_id = ''
                    output = t1_Processor_field('RICE',search_text,field_id,from_date,to_date)
            
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                    if get_shipment.exists() :
                        bale_id = [i["id"] for i in get_shipment]
                        output = t1_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id)

            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                if get_delivery_id3.exists() :
                    rice_shipment_id = [i.shipment_id for i in get_delivery_id3][0]
                    field_id = [i.field.id for i in get_delivery_id3][0]
                    field_name = [i.field.name for i in get_delivery_id3][0]
                    warehouse_wh_id = ''
                    output = t1_Processor_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
            else:
                output = []
            for i in output:
                writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                 i["pounds_received"], i["pounds_delta"]])
        return response
    else:
        return redirect ('dashboard')

@login_required()
def traceability_report_WIP2_csv_download(request,select_crop,get_search_by,search_text,from_date,to_date):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'Outbound 2 WIP.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
        output = []
        if select_crop == 'COTTON' :
            if get_search_by and get_search_by == 'grower' :
                pass      
                                        
            elif get_search_by and get_search_by == 'field' :
                pass
   
            elif get_search_by and get_search_by == 'processor' :
                pass
                  
            elif get_search_by and get_search_by == 'deliveryid' :
                pass

            else:
                output = []
            for i in output:
                writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["date"], i["pounds_shipped"], 
                                 i["pounds_received"], i["pounds_delta"]])
            
        if select_crop == 'RICE' :
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        grower_field_ids = [i.id for i in check_grower_field_crop]
                        # 20-03-23
                        output = outbound2_Wip_Grower('RICE',check_grower_id,from_date,to_date,*grower_field_ids)               
            
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                if check_field.exists() :
                    field_name = search_text
                    field_id = [i.id for i in check_field][0]
                    output = outbound2_Wip_Field('RICE',field_name,field_id,from_date,to_date)         
                            
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                    if get_shipment.exists() :
                        output = outbound2_Wip_Processor('RICE',search_text,processor_id,from_date,to_date) 

            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                if get_delivery_id3.exists() :
                    rice_shipment_id = [i.shipment_id for i in get_delivery_id3][0]
                    output = outbound2_Wip_deliveryid('RICE',search_text,rice_shipment_id,from_date,to_date) 
                                
            else:
                output = []
            for i in output:
                writer.writerow([i["deliveryid"] , i["date"], i["quantity"], i["transportation"], i["destination"]])
        return response
    else:
        return redirect ('dashboard')

@login_required()
def traceability_report_T2_Processor_csv_download(request,select_crop,get_search_by,search_text,from_date,to_date):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'T2 Processor.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                             'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
        output = []
        if select_crop == 'COTTON' :
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='COTTON',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        output = t2_Processor_grower('COTTON',check_grower_id,from_date,to_date)        
                                        
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='COTTON')
                if check_field.exists() :
                    field_id = [i.id for i in check_field][0]
                    field_name = [i.name for i in check_field][0]
                    warehouse_wh_id = ''
                    output = t2_Processor_field('COTTON',field_name,field_id,from_date,to_date)
   
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_classing = ClassingReport.objects.filter(processor_id=processor_id).values("id")
                    classing_id = [i["id"] for i in get_classing]
                    bale= BaleReportFarmField.objects.filter(classing_id__in=classing_id).values("id")
                    if bale.exists() :
                        bale_id = [i["id"] for i in bale]
                        output = t2_Processor_Processor('COTTON',processor_id,from_date,to_date,*bale_id)
                  
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id1 = BaleReportFarmField.objects.filter(bale_id__icontains=search_text)
                get_delivery_id2 = BaleReportFarmField.objects.filter(bale_id__icontains=f"0{search_text}")
                if get_delivery_id1.exists() :
                    field_id = [i.ob4 for i in get_delivery_id1][0]
                    field_name = [i.field_name for i in get_delivery_id1][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id1][0]
                    output = t2_Processor_deliveryid('COTTON',search_text,warehouse_wh_id,from_date,to_date)

                elif get_delivery_id2.exists() :
                    field_id = [i.ob4 for i in get_delivery_id2][0]
                    field_name = [i.field_name for i in get_delivery_id2][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id2][0]                    
                    output = t2_Processor_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id,from_date,to_date)

            else:
                output = []
            for i in output:
                writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                 i["pounds_received"], i["pounds_delta"]])
            
        if select_crop == 'RICE' :
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        output = t2_Processor_grower('RICE',check_grower_id,from_date,to_date)
       
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                if check_field.exists() :
                    field_name = search_text
                    field_id = [i.id for i in check_field][0]
                    warehouse_wh_id = ''
                    output = t2_Processor_field('RICE',search_text,field_id,from_date,to_date)
            
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                    if get_shipment.exists() :
                        bale_id = [i["id"] for i in get_shipment]
                        output = t2_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id)

            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                if get_delivery_id3.exists() :
                    rice_shipment_id = [i.shipment_id for i in get_delivery_id3][0]
                    field_id = [i.field.id for i in get_delivery_id3][0]
                    field_name = [i.field.name for i in get_delivery_id3][0]
                    warehouse_wh_id = ''
                    output = t2_Processor_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
            else:
                output = []
            for i in output:
                writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                 i["pounds_received"], i["pounds_delta"]])
        return response
    else:
        return redirect ('dashboard')


@login_required()
def traceability_report_all_csv_download(request,select_crop,get_search_by,search_text,from_date,to_date):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'TRACE MODULE.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        # writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
        #                 'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
        #                 'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
        output_origin = []
        if select_crop == 'COTTON' :
            # search by Grower ....
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='COTTON',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        grower_field_ids = [i.id for i in check_grower_field_crop]
                        writer.writerow(["Origin"])
                        writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                            'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                            'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                        get_Origin_Grower = Origin_searchby_Grower('COTTON',search_text,*grower_field_ids)         
                        for i in get_Origin_Grower :
                            writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                            i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                            i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                        writer.writerow([""])
                        writer.writerow(["Outbound 1 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        # outbound1_wip = outbound1_Wip_Grower('COTTON',search_text,from_date,to_date,*grower_field_ids)         
                        writer.writerow([""])
                        writer.writerow(["T1 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t1_processor = t1_Processor_grower('COTTON',check_grower_id,from_date,to_date)
                        for i in t1_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                            i["pounds_received"], i["pounds_delta"]])
                        # 20-03-23
                        writer.writerow([""])
                        writer.writerow(["Outbound 2 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        # outbound2_wip = outbound2_Wip_Grower('COTTON',check_grower_id,from_date,to_date,*grower_field_ids)         
                        writer.writerow([""])
                        writer.writerow(["T2 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t2_processor = t2_Processor_grower('COTTON',check_grower_id,from_date,to_date)
                        for i in t2_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                            i["pounds_received"], i["pounds_delta"]])
 
                    else:
                        pass
                else:
                    pass
            # search by Field ....
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='COTTON')
                if check_field.exists() :
                    field_id = [i.id for i in check_field][0]
                    field_name = [i.name for i in check_field][0]
                    warehouse_wh_id = ''
                    writer.writerow(["Origin"])
                    writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                        'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                        'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                    get_origin_details = get_Origin_deliveryid('COTTON',field_id,field_name,'',warehouse_wh_id)
                    for i in get_origin_details :
                        writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                        i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                        i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                    writer.writerow([""])
                    writer.writerow(["Outbound 1 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    # outbound1_wip = outbound1_Wip_field('COTTON',search_text,from_date,to_date,field_id)
                    writer.writerow([""])
                    writer.writerow(["T1 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t1_processor = t1_Processor_field('COTTON',field_name,field_id,field_id,from_date,to_date)
                    for i in t1_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                        i["pounds_received"], i["pounds_delta"]])
                    # 20-03-23
                    writer.writerow([""])
                    writer.writerow(["Outbound 2 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    # outbound2_wip = outbound2_Wip_Field('COTTON',field_name,field_id,from_date,to_date)         
                    writer.writerow([""])
                    writer.writerow(["T2 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t2_processor = t2_Processor_field('COTTON',field_name,field_id,from_date,to_date)
                    for i in t2_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                        i["pounds_received"], i["pounds_delta"]])
                else:
                    pass
            # search by Processor ....
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_classing = ClassingReport.objects.filter(processor_id=processor_id).values("id")
                    classing_id = [i["id"] for i in get_classing]
                    bale= BaleReportFarmField.objects.filter(classing_id__in=classing_id).values("id")
                    if bale.exists() :
                        bale_id = [i["id"] for i in bale]
                        writer.writerow(["Origin"])
                        writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                            'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                            'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                        get_Origin_Processor = Origin_searchby_Processor('COTTON',search_text,*bale_id)         
                        for i in get_Origin_Processor :
                            writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                            i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                            i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                        writer.writerow([""])
                        writer.writerow(["Outbound 1 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        writer.writerow([""])
                        writer.writerow(["T1 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t1_processor = t1_Processor_Processor('COTTON',processor_id,from_date,to_date,*bale_id)
                        for i in t1_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                            i["pounds_received"], i["pounds_delta"]])
                        # 20-03-23
                        writer.writerow([""])
                        writer.writerow(["Outbound 2 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        # outbound2_wip = outbound2_Wip_Processor('COTTON',search_text,processor_id,from_date,to_date)        
                        writer.writerow([""])
                        writer.writerow(["T2 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])                        
                        t2_processor =  t2_Processor_Processor('COTTON',processor_id,from_date,to_date,*bale_id) 
                        for i in t2_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                            i["pounds_received"], i["pounds_delta"]])
                    else:
                        pass
                else:
                    pass
            # search by Delivery ID ....
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id1 = BaleReportFarmField.objects.filter(bale_id__icontains=search_text)
                get_delivery_id2 = BaleReportFarmField.objects.filter(bale_id__icontains=f"0{search_text}")
                if get_delivery_id1.exists() :
                    field_id = [i.ob4 for i in get_delivery_id1][0]
                    field_name = [i.field_name for i in get_delivery_id1][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id1][0]
                    writer.writerow(["Origin"])
                    writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                        'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                        'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                    get_origin_details = get_Origin_deliveryid('COTTON',field_id,field_name,search_text,warehouse_wh_id)
                    for i in get_Origin_Processor :
                            writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                            i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                            i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                    # outbound1_wip = outbound1_Wip_deliveryid('COTTON',search_text,warehouse_wh_id)
                    # context["outbound1_wip"] = outbound1_wip
                    writer.writerow([""])
                    writer.writerow(["Outbound 1 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    writer.writerow([""])
                    writer.writerow(["T1 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t1_processor = t1_Processor_deliveryid('COTTON',search_text,warehouse_wh_id,from_date,to_date)
                    for i in t1_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                        i["pounds_received"], i["pounds_delta"]])
                    writer.writerow([""])
                    writer.writerow(["Outbound 2 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    writer.writerow([""])
                    writer.writerow(["T2 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])   
                    t2_processor =  t2_Processor_deliveryid('COTTON',search_text,warehouse_wh_id,from_date,to_date)
                    for i in t2_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                        i["pounds_received"], i["pounds_delta"]])
                elif get_delivery_id2.exists() :
                    field_id = [i.ob4 for i in get_delivery_id2][0]
                    field_name = [i.field_name for i in get_delivery_id2][0]
                    warehouse_wh_id = [i.warehouse_wh_id for i in get_delivery_id2][0]
                    writer.writerow(["Origin"])
                    writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                        'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                        'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                    get_origin_details = get_Origin_deliveryid('COTTON',field_id,field_name,f"0{search_text}",warehouse_wh_id)
                    for i in get_Origin_Processor :
                            writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                            i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                            i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                    # outbound1_wip = outbound1_Wip_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id)
                    # context["outbound1_wip"] = outbound1_wip
                    writer.writerow([""])
                    writer.writerow(["Outbound 1 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    writer.writerow([""])
                    writer.writerow(["T1 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t1_processor = t1_Processor_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id,from_date,to_date)
                    for i in t1_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                        i["pounds_received"], i["pounds_delta"]])
                    writer.writerow([""])
                    writer.writerow(["Outbound 2 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    writer.writerow([""])
                    writer.writerow(["T2 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])   
                    t2_processor =  t2_Processor_deliveryid('COTTON',f"0{search_text}",warehouse_wh_id,from_date,to_date)
                    for i in t2_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                        i["pounds_received"], i["pounds_delta"]])
                else:
                    pass                  
            else:
                pass
        if select_crop == 'RICE' :
            if get_search_by and get_search_by == 'grower' :
                check_grower = Grower.objects.filter(name__icontains=search_text)
                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower][0]
                    check_grower_field_crop = Field.objects.filter(crop='RICE',grower_id=check_grower_id)
                    if check_grower_field_crop.exists() :
                        grower_field_ids = [i.id for i in check_grower_field_crop]
                        writer.writerow(["Origin"])
                        writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                        'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                        'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                        get_Origin_Grower = Origin_searchby_Grower('RICE',search_text,*grower_field_ids)                                              
                        for i in get_Origin_Grower:
                            writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                            i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                            i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                        writer.writerow([""])
                        writer.writerow(["Outbound 1 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        outbound1_wip = outbound1_Wip_Grower('RICE',search_text,from_date,to_date,*grower_field_ids)    
                        for i in outbound1_wip:
                            writer.writerow([i["deliveryid"], i["date"], i["quantity"], i["transportation"], i["destination"]])
                        writer.writerow([""])
                        writer.writerow(["T1 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t1_processor = t1_Processor_grower('RICE',check_grower_id,from_date,to_date)
                        for i in t1_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                            i["pounds_received"], i["pounds_delta"]])
                        # 20-03-23
                        writer.writerow([""])
                        writer.writerow(["Outbound 2 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        outbound2_wip = outbound2_Wip_Grower('RICE',check_grower_id,from_date,to_date,*grower_field_ids)         
                        for i in outbound2_wip:
                            writer.writerow([i["deliveryid"] , i["date"], i["quantity"], i["transportation"], i["destination"]])
                        writer.writerow([""])
                        writer.writerow(["T2 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t2_processor = t2_Processor_grower('RICE',check_grower_id,from_date,to_date)
                        for i in t2_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                 i["pounds_received"], i["pounds_delta"]])
                    else:
                        pass
                else:
                    pass
            # search by Field ....
            elif get_search_by and get_search_by == 'field' :
                check_field = Field.objects.filter(name__icontains=search_text,crop='RICE')
                if check_field.exists() :
                    field_name = search_text
                    field_id = [i.id for i in check_field][0]
                    warehouse_wh_id = ''
                    writer.writerow(["Origin"])
                    writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                    'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                    'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                    get_origin_details = get_Origin_deliveryid('RICE',field_id,field_name,'',warehouse_wh_id)
                    for i in get_origin_details:
                        writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                        i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                        i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                    writer.writerow([""])
                    writer.writerow(["Outbound 1 WIP"])
                    outbound1_wip = outbound1_Wip_field('RICE',search_text,from_date,to_date,field_id)
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    for i in outbound1_wip:
                        writer.writerow([i["deliveryid"], i["date"], i["quantity"], i["transportation"], i["destination"]])
                    writer.writerow([""])
                    writer.writerow(["T1 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t1_processor = t1_Processor_field('RICE',search_text,field_id,from_date,to_date)
                    for i in t1_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                        i["pounds_received"], i["pounds_delta"]])

                    # 20-03-23
                    writer.writerow([""])
                    writer.writerow(["Outbound 2 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    outbound2_wip = outbound2_Wip_Field('RICE',field_name,field_id,from_date,to_date)         
                    for i in outbound2_wip:
                        writer.writerow([i["deliveryid"] , i["date"], i["quantity"], i["transportation"], i["destination"]])
                    writer.writerow([""])
                    writer.writerow(["T2 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t2_processor = t2_Processor_field('RICE',field_name,field_id,from_date,to_date)
                    for i in t2_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                i["pounds_received"], i["pounds_delta"]])
                else:
                    pass
            # search by Processor ....
            elif get_search_by and get_search_by == 'processor' :
                check_processor = Processor.objects.filter(entity_name__icontains=search_text)
                if check_processor.exists() :
                    processor_id = [i.id for i in check_processor][0]
                    get_shipment = GrowerShipment.objects.filter(processor_id=processor_id,crop='RICE').values("id")
                    if get_shipment.exists() :
                        bale_id = [i["id"] for i in get_shipment]
                        writer.writerow(["Origin"])
                        writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                        'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                        'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                        get_Origin_Processor = Origin_searchby_Processor('RICE',search_text,*bale_id)         
                        for i in get_Origin_Processor:
                            writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                            i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                            i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                        writer.writerow([""])
                        writer.writerow(["Outbound 1 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        outbound1_wip = outbound1_Wip_Processor('RICE',from_date,to_date,processor_id)
                        for i in outbound1_wip:
                            writer.writerow([i["deliveryid"], i["date"], i["quantity"], i["transportation"], i["destination"]])
                        writer.writerow([""])
                        writer.writerow(["T1 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t1_processor = t1_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id)
                        for i in t1_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                        i["pounds_received"], i["pounds_delta"]])
                        # 20-03-23
                        writer.writerow([""])
                        writer.writerow(["Outbound 2 WIP"])
                        writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                        outbound2_wip = outbound2_Wip_Processor('RICE',search_text,processor_id,from_date,to_date)         
                        for i in outbound2_wip:
                            writer.writerow([i["deliveryid"] , i["date"], i["quantity"], i["transportation"], i["destination"]])
                        writer.writerow([""])
                        writer.writerow(["T2 Processor"])
                        writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                        'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                        t2_processor =  t2_Processor_Processor('RICE',processor_id,from_date,to_date,*bale_id) 
                        for i in t2_processor:
                            writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                i["pounds_received"], i["pounds_delta"]])
                    else:
                        pass
                else:
                    pass
            # search by Delivery ID ....
            elif get_search_by and get_search_by == 'deliveryid' :
                get_delivery_id3 = GrowerShipment.objects.filter(shipment_id__icontains=search_text)
                if get_delivery_id3.exists() :
                    rice_shipment_id = [i.shipment_id for i in get_delivery_id3][0]
                    field_id = [i.field.id for i in get_delivery_id3][0]
                    field_name = [i.field.name for i in get_delivery_id3][0]
                    warehouse_wh_id = ''
                    writer.writerow(["Origin"])
                    writer.writerow(['CROP', 'VARIETY', 'FIELD', 'GROWER', 'FARM', 'HARVEST DATE', 
                    'PROJECTED YIELD', 'ACTUAL YIELD', 'YIELD  DELTA', 'Pass / Fail Sustainability','Water Savings %',
                    'Land Use Efficiency %', 'Less GHG % ', 'Premiums to Growers %', 'CO2 EQ Footprint #','Pounds of Water Per Pound Savings %'])
                    get_origin_details = get_Origin_deliveryid('RICE',field_id,field_name,search_text,warehouse_wh_id)
                    for i in get_Origin_Processor:
                        writer.writerow([i["get_select_crop"], i["variety"], i["field_name"], i["grower_name"], i["farm_name"], i["harvest_date"], 
                        i["projected_yeild"], i["reported_yeild"], i["yield_delta"],i["pf_sus"],i["water_savings"],i["land_use"],i["premiums_to_growers"],
                        i["co2_eQ_footprint"],i["water_per_pound_savings"]])
                    writer.writerow([""])
                    writer.writerow(["Outbound 1 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    outbound1_wip = outbound1_Wip_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
                    for i in outbound1_wip:
                        writer.writerow([i["deliveryid"], i["date"], i["quantity"], i["transportation"], i["destination"]])
                    
                    writer.writerow([""])
                    writer.writerow(["T1 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t1_processor = t1_Processor_deliveryid('RICE',rice_shipment_id,warehouse_wh_id,from_date,to_date)
                    for i in t1_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                                    i["pounds_received"], i["pounds_delta"]])
                    # 20-03-23        
                    writer.writerow([""])
                    writer.writerow(["Outbound 2 WIP"])
                    writer.writerow(['DELIVERY ID OUTBOUND', 'DATE', 'QUANTITY POUNDS', 'TRANSPORTATION MODE (RAIL OR TRUCK)', 'DESTINATION'])
                    outbound2_wip = outbound2_Wip_deliveryid('RICE',search_text,rice_shipment_id,from_date,to_date) 
                    for i in outbound2_wip:
                        writer.writerow([i["deliveryid"] , i["date"], i["quantity"], i["transportation"], i["destination"]])
                    writer.writerow([""])
                    writer.writerow(["T2 Processor"])
                    writer.writerow(['PROCESSOR NAME', 'PROCESSOR ID #', 'DELIVERY ID', 'Grower', 'Farm', 'Field', 'DATE', 'QUANTITY POUNDS SHIPPED', 
                    'QUANTITY POUNDS RECEIVED', 'QUANTITY DELTA'])
                    t2_processor =  t2_Processor_deliveryid('RICE',search_text,warehouse_wh_id,from_date,to_date)
                    for i in t2_processor:
                        writer.writerow([i["processor_name"] , i["processor_id"], i["deliveryid"], i["grower"], i["farm"], i["field"], i["date"], i["pounds_shipped"], 
                            i["pounds_received"], i["pounds_delta"]])
                else:
                    pass 
            else:
                pass
        return response
    else:
        return redirect ('dashboard')

@login_required()
def display_traceability_report(request):
    # try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            if request.method == 'POST':
                select_crop= request.POST.get('select_crop')
                crop_year= request.POST.get('crop_year')
                from_date= request.POST.get('from_date')
                to_date= request.POST.get('to_date')
                search_text= request.POST.get('search_text')
                get_search_by= request.POST.get('get_search_by')
                if select_crop and crop_year and from_date and to_date and search_text :
                    context['select_crop'] = select_crop
                    context['crop_year'] = crop_year
                    context['from_date'] = from_date
                    context['to_date'] = to_date
                    context['search_text'] = search_text
                    context['get_search_by'] = get_search_by
                # shipment_id = request.GET.get('shipment_id')
                # check_shipment = ShipmentManagement.objects.filter(shipment_id=shipment_id).first()
                # sender_processor = check_shipment.processor_idd
                # check_sender = Processor2.objects.filter(id=sender_processor)
                # if check_sender.exists():
                #     get_sender = check_sender.first()
                #     get_sender_values = check_sender.values()
                #     if get_sender.processor_type == "T4":
                #         incoming_shipment_sender = list(ShipmentManagement.objects.filter(processor2_idd=get_sender.id).values("processor_idd"))
                #         if incoming_shipment_sender:
                #             for sender in incoming_shipment_sender:
                #                 check_in_sender = Processor2.objects.filter(id=sender["processor_idd"])
                #                 if check_in_sender:
                #                     get_in_sender = check_in_sender.first()
                #                     if get_in_sender.processor_type == "T3":
                #                         new_senders = list(ShipmentManagement.objects.filter(processor2_idd=get_in_sender.id).values("processor_idd"))
                #                         if new_senders:
                #                             for sndr in new_senders:
                #                                 check_new_sndr = Processor2.objects.filter(id=sndr["processor_idd"], processor_type="T2")
                #                                 if check_new_sndr:
                #                                     get_new_sndr = check_new_sndr.first()                                                
                #                                     t1_senders = ShipmentManagement.objects.filter(processor2_idd=get_new_sndr.id).values("processor_idd")                                                
                #                                     for t1 in t1_senders:
                #                                         check_t1 = Processor.objects.filter(id=t1["processor_idd"]).first()
                #                                         check_growers = list(GrowerShipment.objects.filter(processor_id=check_t1.id).values('grower', 'processor', 'storage','field','crop'))
                #                                 else:
                #                                     get_new_sndr = Processor.objects.filter(id=sndr["processor_idd"]).first()                                           
                #                                     check_growers = list(GrowerShipment.objects.filter(processor_id=get_new_sndr.id).values('grower', 'processor', 'storage','field','crop'))
                                                    
                #                     elif get_in_sender.processor_type == "T2":
                #                         t1_senders = ShipmentManagement.objects.filter(processor2_idd=get_in_sender.id).values("processor_idd")                                                
                #                         for t1 in t1_senders:
                #                             check_t1 = Processor.objects.filter(id=t1["processor_idd"]).first()
                #                             check_growers = list(GrowerShipment.objects.filter(processor_id=check_t1.id).values('grower', 'processor', 'storage','field','crop'))
                                            
                #                     else:
                #                         pass
                #                 else:
                #                     get_in_sender = Processor.objects.filter(id=sender["processor_idd"]).first()
                #                     check_growers = list(GrowerShipment.objects.filter(processor_id=get_in_sender.id).values('grower', 'processor', 'storage','field','crop'))
                                    

                #     elif get_sender.processor_type == "T3":
                #         new_senders = list(ShipmentManagement.objects.filter(processor2_idd=get_sender.id).values("processor_idd"))
                #         if new_senders:
                #             for sndr in new_senders:
                #                 check_new_sndr = Processor2.objects.filter(id=sndr["processor_idd"], processor_type="T2")
                #                 if check_new_sndr:
                #                     get_new_sndr = check_new_sndr.first()                                                
                #                     t1_senders = ShipmentManagement.objects.filter(processor2_idd=get_new_sndr.id).values("processor_idd")                                                
                #                     for t1 in t1_senders:
                #                         check_t1 = Processor.objects.filter(id=t1["processor_idd"]).first()
                #                         check_growers = list(GrowerShipment.objects.filter(processor_id=check_t1.id).values('grower', 'processor', 'storage','field','crop'))
                                        
                #                 else:
                #                     get_new_sndr = Processor.objects.filter(id=sndr["processor_idd"]).first()                                           
                #                     check_growers = list(GrowerShipment.objects.filter(processor_id=get_new_sndr.id).values('grower', 'processor', 'storage','field','crop'))
                #     else:
                #         t1_senders = ShipmentManagement.objects.filter(processor2_idd=get_sender.id).values("processor_idd")                                                
                #         for t1 in t1_senders:
                #             check_t1 = Processor.objects.filter(id=t1["processor_idd"]).first()
                #             check_growers = list(GrowerShipment.objects.filter(processor_id=check_t1.id).values('grower', 'processor', 'storage','field','crop'))
                # else:
                #     get_sender = Processor.objects.filter(id=sender_processor).first()
                #     check_growers = list(GrowerShipment.objects.filter(processor_id=get_sender.id).values('grower', 'processor', 'storage','field','crop'))
                # print(check_growers)
                # context["growers"] = check_growers
            return render(request, 'tracemodule/traceability_report.html', context)
        else:
            return redirect('login')    
    # except Exception as e:
    #     return HttpResponse(e)   
