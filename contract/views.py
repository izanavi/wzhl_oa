# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from contract.models import table, detail
from vacation.models import user_table
from wzhl_oa.settings import BASE_DIR
import json
import datetime
import os
from libs.common import Num2MoneyFormat
from django import forms

@login_required
def contract_apply(request):
    path = request.path.split('/')[1]
    return render(request, 'contract/contract_table.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'contract',
                                                 'path2':path,
                                                 'page_name1':u'合同管理',
                                                 'page_name2':u'合同申请',},
                                                context_instance=RequestContext(request))




@login_required
def contract_apply_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['contract_uuid','apply_time','name','contract_class','party_b','contract_name','contract_amount_figures','status','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.all()
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    else:
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.all()
            sSearch_list = sSearch.split()
            for i in range(len(sSearch_list)):
                result_data = result_data.filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i]))

                iTotalRecords = result_data.filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                Q(party_b__contains=sSearch_list[i]) | \
                                                Q(contract_name__contains=sSearch_list[i])).count()
            result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]


    for i in  result_data:
        aaData.append({
                       '0':i.contract_uuid,
                       '1':str(i.apply_time),
                       '2':i.name,
                       '3':i.contract_class,
                       '4':i.party_b,
                       '5':i.contract_name,
                       '6':i.contract_amount_figures,
                       '7':i.status,
                       '8':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")




@login_required
def contract_set_session(request):
    _id = request.POST.get('id')
    commit = request.POST.get('commit')
    if _id == '0':
        try:
            request.session.pop('contract_id')
        except KeyError:
            pass
    elif _id:
        request.session['contract_id'] = int(_id)
    if commit:
        request.session['contract_commit'] = commit
    return HttpResponse(json.dumps('OK'),content_type="application/json")



@login_required
def contract_apply_detail(request):
    path = request.path.split('/')[1]
    contract_uuid = request.POST.get('contract_uuid')
    origin_contract_uuid = request.POST.get('origin_contract_uuid')
    party_a = request.POST.get('party_a')
    # name = request.POST.get('name')
    # department = request.POST.get('department')
    finance_class = request.POST.get('finance_class')
    contract_class = request.POST.get('contract_class')
    contract_name = request.POST.get('contract_name')
    party_b = request.POST.get('party_b')
    address = request.POST.get('address')
    contacts = request.POST.get('contacts')
    e_mail = request.POST.get('e_mail')
    phone_1 = request.POST.get('phone_1')
    phone_2 = request.POST.get('phone_2')
    fax = request.POST.get('fax')
    bank = request.POST.get('bank')
    bank_account = request.POST.get('bank_account')
    contract_detail = request.POST.get('contract_detail')
    contract_amount_figures = request.POST.get('contract_amount_figures')
    special_requirements = request.POST.get('special_requirements')
    contract_begin_time = request.POST.get('begin')
    contract_end_time = request.POST.get('end')
    partner_qualification = request.POST.get('partner_qualification')
    comment = request.POST.get('comment')
    _id = request.POST.get('id')
    commit = request.POST.get('commit')

    user_info_orm = user_table.objects.get(name=request.user.first_name)

    name = user_info_orm.name
    department = user_info_orm.department
    apply_time = ''
    contract_amount_words = ''
    stamp_status = 0
    archive_status = 0
    status = 0

    print contract_uuid,origin_contract_uuid,party_a,name,finance_class,contract_class,contract_name,party_b,address,contacts,e_mail,phone_1,phone_2,\
          fax,bank,bank_account,contract_detail,contract_amount_figures,special_requirements,contract_begin_time,contract_end_time,\
          partner_qualification,comment,_id


    try:
        request.session.pop('contract_result')
    except KeyError:
        pass

    table_id =  request.session.get('contract_id')
    if not table_id:
        if party_a and party_b:
            try:
                if party_a == u'上海六界信息技术有限公司':
                    uuid_a = 'SHLJ'
                elif party_a == u'竹筏科技（北京）科技有限公司':
                    uuid_a = 'BJZF'

                uuid_b = {u'商务合作':'SWHZ',
                          u'艺人经纪':'YRJJ',
                          u'市场框架':'SCKJ',
                          u'技术开发':'JSKF',
                          u'行政':'XZ',
                          u'人事':'RS',
                          u'财务':'CW',
                          u'法务':'FW',
                          u'其他':'QT'}

                if len(table.objects.all()) == 0:
                    uuid_c = str(datetime.datetime.now().year) + '0001'
                else:
                    uuid_c_orm = table.objects.all().order_by('id').reverse()[0]
                    uuid_c = str(int(str(datetime.datetime.now().year) + uuid_c_orm.contract_uuid.split('-')[2][4:]) + 1)

                contract_uuid = '-'.join([uuid_a, uuid_b[contract_class], uuid_c])
                print contract_uuid

                contract_amount_words = Num2MoneyFormat(float(contract_amount_figures))

                approve_now = user_info_orm.principal

                if party_a == u'上海六界信息技术有限公司':
                    if finance_class == u'无金额':
                        process_type = 'l'
                    else:
                        if float(contract_amount_figures) >= 100000:
                            process_type = 'l'
                        else:
                            process_type = 's'
                elif party_a == u'竹筏科技（北京）科技有限公司':
                    if finance_class == u'无金额':
                        process_type = 'l'
                    if finance_class == u'收':
                        if float(contract_amount_figures) >= 500000:
                            process_type = 'l'
                        else:
                            process_type = 's'
                    if finance_class == u'支':
                        if float(contract_amount_figures) >= 200000:
                            process_type = 'l'
                        else:
                            process_type = 's'

                orm = table(party_a=party_a,name=name,department=department,finance_class=finance_class,contract_class=contract_class,\
                            contract_uuid=contract_uuid,origin_contract_uuid=origin_contract_uuid,contract_name=contract_name,\
                            party_b=party_b,address=address,contacts=contacts,e_mail=e_mail,phone_1=phone_1,phone_2=phone_2,\
                            fax=fax,bank=bank,bank_account=bank_account,comment=comment,contract_detail=contract_detail,\
                            contract_amount_figures=contract_amount_figures,contract_amount_words=contract_amount_words,\
                            special_requirements=special_requirements,contract_begin_time=contract_begin_time,\
                            contract_end_time=contract_end_time,partner_qualification=partner_qualification,stamp_status=0,\
                            archive_status=0,status=1,approve_now=approve_now,commit_time=datetime.datetime.now(),process_type=process_type)

                orm.save()
                request.session['contract_result'] = u'保存成功'
            except Exception,e:
                print e
                request.session['contract_result'] = e
        else:
            if commit == '1':
                request.session['contract_result'] = u'星号为必填项'
    else:
        try:
            orm = table.objects.get(id=table_id)
            commit = request.session.get('contract_commit')
            print commit
            if orm.status == 0:
                orm.status = 1
            if commit != '0':
                orm.party_a = party_a
                orm.finance_class = finance_class
                orm.contract_class = contract_class
                orm.origin_contract_uuid = origin_contract_uuid
                orm.contract_name = contract_name
                orm.party_b = party_b
                orm.address = address
                orm.contacts = contacts
                orm.e_mail = e_mail
                orm.phone_1 = phone_1
                orm.phone_2 = phone_2
                orm.fax = fax
                orm.bank = bank
                orm.bank_account = bank_account
                orm.comment = comment
                orm.contract_detail = contract_detail
                orm.contract_amount_figures = contract_amount_figures
                orm.special_requirements = special_requirements
                orm.contract_begin_time = contract_begin_time
                orm.contract_end_time = contract_end_time
                orm.partner_qualification = partner_qualification
                orm.apply_time = datetime.datetime.now()
                orm.comment = comment
                orm.save()
                request.session['contract_result'] = u'保存成功'
            # try:
            #     request.session.pop('contract_commit')
            # except KeyError:
            #     pass
            return render(request, 'contract/contract_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                     'path1':'contract',
                                                     'path2':path,
                                                     'page_name1':u'合同管理',
                                                     'page_name2':u'合同信息',
                                                     'name':orm.name,
                                                     'department':orm.department,
                                                     'apply_time':str(orm.apply_time),
                                                     'party_a':orm.party_a,
                                                     'finance_class':orm.finance_class,
                                                     'contract_uuid':orm.contract_uuid,
                                                     'origin_contract_uuid':orm.origin_contract_uuid,
                                                     'contract_class':orm.contract_class,
                                                     'party_b':orm.party_b,
                                                     'contacts':orm.contacts,
                                                     'contract_name':orm.contract_name,
                                                     'address':orm.address,
                                                     'e_mail':orm.e_mail,
                                                     'phone_1':orm.phone_1,
                                                     'phone_2':orm.phone_2,
                                                     'fax':orm.fax,
                                                     'bank':orm.bank,
                                                     'bank_account':orm.bank_account,
                                                     'comment':orm.comment,
                                                     'contract_detail':orm.contract_detail,
                                                     'contract_amount_figures':orm.contract_amount_figures,
                                                     'contract_amount_words':orm.contract_amount_words,
                                                     'special_requirements':orm.special_requirements,
                                                     'contract_begin_time':str(orm.contract_begin_time),
                                                     'contract_end_time':str(orm.contract_end_time),
                                                     'partner_qualification':orm.partner_qualification,
                                                     'stamp_status':orm.stamp_status,
                                                     'archive_status':orm.archive_status,
                                                     'status':orm.status,
                                                     },
                                                    context_instance=RequestContext(request))
        except Exception,e:
            print e
            request.session['contract_result'] = e
    return render(request, 'contract/contract_table_detail.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                     'path1':'contract',
                                                     'path2':path,
                                                     'page_name1':u'合同管理',
                                                     'page_name2':u'合同信息',
                                                     'name':name,
                                                     'department':department,
                                                     'apply_time':apply_time,
                                                     'contract_amount_words':contract_amount_words,
                                                     'stamp_status':stamp_status,
                                                     'archive_status':archive_status,
                                                     'status':status,
                                                     },
                                                    context_instance=RequestContext(request))



@login_required
def contract_approve(request):
    path = request.path.split('/')[1]
    return render(request, 'contract/contract_approve.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                 'path1':'contract',
                                                 'path2':path,
                                                 'page_name1':u'合同管理',
                                                 'page_name2':u'合同审批',},
                                                context_instance=RequestContext(request))




@login_required
def contract_approve_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['contract_uuid','apply_time','name','contract_class','party_b','contract_name','contract_amount_figures','status','id']

    subordinate = []
    subordinate_orm = user_table.objects.filter(principal=request.user.first_name)
    for i in subordinate_orm:
        subordinate.append(i.name)

    if request.user.has_perm('contract.can_view_all'):
        if  sSortDir_0 == 'asc':
            if sSearch == '':
                result_data = table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = table.objects.all().count()
            else:
                result_data = table.objects.all()
                sSearch_list = sSearch.split()
                for i in range(len(sSearch_list)):
                    result_data = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i]))

                    iTotalRecords = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i])).count()
                result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
        else:
            if sSearch == '':
                result_data = table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = table.objects.all().count()
            else:
                result_data = table.objects.all()
                sSearch_list = sSearch.split()
                for i in range(len(sSearch_list)):
                    result_data = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i]))

                    iTotalRecords = result_data.all().filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i])).count()
                result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
    else:
        if  sSortDir_0 == 'asc':
            if sSearch == '':
                result_data = table.objects.filter(name__in=subordinate).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = table.objects.filter(name__in=subordinate).count()
            else:
                result_data = table.objects.all()
                sSearch_list = sSearch.split()
                for i in range(len(sSearch_list)):
                    result_data = result_data.filter(name__in=subordinate).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i]))

                    iTotalRecords = result_data.filter(name__in=subordinate).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i])).count()
                result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
        else:
            if sSearch == '':
                result_data = table.objects.filter(name__in=subordinate).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
                iTotalRecords = table.objects.filter(name__in=subordinate).count()
            else:
                result_data = table.objects.all()
                sSearch_list = sSearch.split()
                for i in range(len(sSearch_list)):
                    result_data = result_data.filter(name__in=subordinate).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i]))

                    iTotalRecords = result_data.filter(name__in=subordinate).filter(Q(contract_uuid__contains=sSearch_list[i]) | \
                                                    Q(party_b__contains=sSearch_list[i]) | \
                                                    Q(contract_name__contains=sSearch_list[i])).count()
                result_data = result_data.order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]


    for i in  result_data:
        export = '''
                    <a class="btn btn-sm green">
                        生成Excel文件 <i class="fa fa-level-down"></i>
                    </a>
                '''
        approve = '''
                    <a class="btn btn-sm blue">
                        审批 <i class="fa"></i>
                    </a>
                 '''
        aaData.append({
                       '0':i.contract_uuid,
                       '1':str(i.apply_time),
                       '2':i.name,
                       '3':i.contract_class,
                       '4':i.party_b,
                       '5':i.contract_name,
                       '6':i.contract_amount_figures,
                       '7':i.status,
                       '8':export,
                       '9':approve,
                       '10':i.id,
                       '11':i.process_type,
                       '12':i.approve_now
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

@login_required
def handle_uploaded_file(request,f):
    file_name = ''
    try:
        path = 'media/'
        # file_name = path + f.name
        today = datetime.datetime.now()
        os.system('mkdir -p {0}{1}/{2}/{3}/'.format(path, today.year, today.month, today.day))
        full_name = '{0}{1}/{2}/{3}/{4}'.format(path, today.year, today.month, today.day, f.name)
        if os.path.isfile(full_name):
            time = datetime.datetime.now().strftime('%H%M%S')
            full_name =  '{0}{1}/{2}/{3}/{4}_{5}'.format(path, today.year, today.month, today.day, time, f.name)
            # orm = upload_files.objects.get(file_name=f.name)
            # orm.file_name = f.name + '_' + time
            # orm.save()
        file = open(full_name, 'wb+')
        for chunk in f.chunks():
            file.write(chunk)
        file.close()
        file_size = os.path.getsize(full_name)
        # upload_files.objects.create(file_name=f.name,file_size=file_size,upload_user=request.user.username)

        request.session['contract_upload_file'] = full_name
        result_code = 0
    except Exception, e:
        import traceback
        print traceback.format_exc()
        # logger.error(e)
        result_code = 1
    return result_code

@login_required
def contract_get_upload(request):
    file = request.FILES.get('file')
    if not file == None:
        result_code = handle_uploaded_file(request,file)
        if result_code == 0:
            return HttpResponse(json.dumps({'msg': "上传成功", "code": 0}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'msg': "上传失败", "code": 1}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({'msg': "上传失败", "code": 1}),content_type="application/json")



@login_required
def contract_approve_process(request):
    flag = request.POST.get('flag')
    _id = request.POST.get('id')
    status = request.POST.get('status')
    process_type = request.POST.get('process_type')
    comment = request.POST.get('comment')
    add_process = request.POST.get('add_process')

    status_owner = {2: u'龚晓芸',
                    3: u'高茹',
                    4: u'张莉莹',
                    6: u'王娟',
                    7: u'曹津',
                    8: u'张莉莹',
                    9: u'张莉莹'}

    try:
        try:
            archive_path = request.session['contract_upload_file']
            request.session['contract_upload_file'] = ''
        except KeyError:
            archive_path = ''

        orm = table.objects.get(id=_id)

        if request.user.first_name != orm.approve_now:
            return HttpResponse(json.dumps({'code':1,'msg':u'您不是审批人'}),content_type="application/json")

        detail_orm = detail.objects.filter(parent_id=_id)
        if flag == '1':
            if status == '0':
                principal_orm = user_table.objects.get(name=orm.name)
                orm.status = 1
                orm.approve_now = principal_orm.principal

            if status == '1':
                for i in detail_orm:
                    if status_owner[2] == i.name:
                        if process_type == 'l':
                            orm.status = 3
                        else:
                            orm.status = 4
                        break
                else:
                    orm.status = 2
                orm.approve_now = status_owner[orm.status]

            if status == '2':
                for i in detail_orm:
                    if process_type == 'l':
                        if status_owner[3] == i.name:
                            orm.status = 4
                            break
                        else:
                             orm.status = 3
                    else:
                        if status_owner[4] == i.name:
                            orm.status = 6
                            break
                        else:
                            orm.status = 4
                orm.approve_now = status_owner[orm.status]

            if status == '3':
                for i in detail_orm:
                    if status_owner[4] == i.name:
                        orm.status = 6
                        break
                else:
                    orm.status = 4
                orm.approve_now = status_owner[orm.status]

            if status == '4':
                if add_process:
                    orm.status = 5
                    orm.approve_now = add_process
                else:
                    if process_type == 'l':
                        for i in detail_orm:
                            if status_owner[6] == i.name:
                                orm.status = 7
                                break
                        else:
                            orm.status = 6
                    else:
                        orm.status = 8
                    orm.approve_now = status_owner[orm.status]

            if status == '5':
                if process_type == 'l':
                    for i in detail_orm:
                        if status_owner[6] == i.name:
                            orm.status = 7
                            break
                    else:
                        orm.status = 6
                else:
                    orm.status = 8
                orm.approve_now = status_owner[orm.status]

            if status == '6':
                for i in detail_orm:
                    if status_owner[7] == i.name:
                        orm.status = 8
                        break
                else:
                    orm.status = 7
                orm.approve_now = status_owner[orm.status]

            if status == '7':
                orm.status = 8
                orm.approve_now = status_owner[orm.status]

            if status == '8':
                orm.status = 9
                orm.approve_now = status_owner[orm.status]
                orm.stamp_status = 1

            if status == '9':
                orm.status = 10
                orm.approve_now = ''
                orm.archive_status = 1

        if flag == '-1':
            if status >= 4:
                orm.status = 0
                orm.approve_now = ''
            else:
                orm.status = 4
                orm.approve_now = status_owner[orm.status]

        if flag == '0':
            orm.status = 11
            orm.approve_now = ''

        orm.apply_time = datetime.datetime.now()
        orm.save()

        orm2 = detail(name=request.user.first_name,operation=flag,archive_path=archive_path,comment=comment,parent_id=_id)
        orm2.save()

        return HttpResponse(json.dumps({'code':0,'msg':u'审批成功'}),content_type="application/json")
    except Exception,e:
        import traceback
        print traceback.format_exc()
        print e
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")



@login_required
def contract_process_detail_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['apply_time','name','operation','archive_path','comment','id']

    try:
        parent_id = request.session['contract_id']
    except KeyError:
        parent_id = None
    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = detail.objects.filter(parent_id=parent_id).order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = detail.objects.filter(parent_id=parent_id).count()
        else:
            result_data = detail.objects.filter(parent_id=parent_id).filter(Q(name__contains=sSearch) | \
                                                                                          Q(archive_path__contains=sSearch) | \
                                                                                          Q(comment__contains=sSearch) | \
                                                                                          Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = detail.objects.filter(parent_id=parent_id).filter(Q(name__contains=sSearch) | \
                                                                                          Q(archive_path__contains=sSearch) | \
                                                                                          Q(comment__contains=sSearch) | \
                                                                                          Q(id__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = detail.objects.filter(parent_id=parent_id).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = detail.objects.filter(parent_id=parent_id).count()
        else:
            result_data = detail.objects.filter(parent_id=parent_id).filter(Q(name__contains=sSearch) | \
                                                                                          Q(archive_path__contains=sSearch) | \
                                                                                          Q(comment__contains=sSearch) | \
                                                                                          Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = detail.objects.filter(parent_id=parent_id).filter(Q(name__contains=sSearch) | \
                                                                                          Q(archive_path__contains=sSearch) | \
                                                                                          Q(comment__contains=sSearch) | \
                                                                                          Q(id__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':str(i.apply_time),
                       '1':i.name,
                       '2':i.operation,
                       '3':i.archive_path,
                       '4':i.comment,
                       '5':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")