# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from order_form.models import user,order
from django.db.models.query_utils import Q
from django.utils.log import logger
from libs.get_client_ip import get_ip
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import simplejson,datetime



######################员工花名册#############################
# def staff(request):
#     path = request.path.split('/')[1]
#     return render_to_response('order_form/staff.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
#                                                        'path1':'order_manage',
#                                                        'path2':path,
#                                                        'page_name1':u'订餐管理',
#                                                        'page_name2':u'员工花名册'})
#
# def staff_data(request):
#     sEcho =  request.POST.get('sEcho') #标志，直接返回
#     iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
#     iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
#     iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
#     sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
#     sSearch = request.POST.get('sSearch')#高级搜索
#
#     aaData = []
#     sort = ['name','department','comment','id']
#
#     if  sSortDir_0 == 'asc':
#         if sSearch == '':
#             result_data = order.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
#             iTotalRecords = order.objects.all().count()
#         else:
#             result_data = order.objects.filter(Q(name__contains=sSearch) | \
#                                                Q(type__contains=sSearch) | \
#                                                Q(comment__contains=sSearch)) \
#                                             .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
#             iTotalRecords = order.objects.filter(Q(name__contains=sSearch) | \
#                                                Q(department__contains=sSearch) | \
#                                                Q(comment__contains=sSearch)).count()
#     else:
#         if sSearch == '':
#             result_data = order.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
#             iTotalRecords = order.objects.all().count()
#         else:
#             result_data = order.objects.filter(Q(name__contains=sSearch) | \
#                                                Q(department__contains=sSearch) | \
#                                                Q(comment__contains=sSearch)) \
#                                             .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
#             iTotalRecords = order.objects.filter(Q(name__contains=sSearch) | \
#                                                Q(department__contains=sSearch) | \
#                                                Q(comment__contains=sSearch)).count()
#     for i in  result_data:
#         aaData.append({
#                        '0':i.name,
#                        '1':i.department,
#                        '2':i.comment,
#                        '3':i.id
#                       })
#     result = {'sEcho':sEcho,
#                'iTotalRecords':iTotalRecords,
#                'iTotalDisplayRecords':iTotalRecords,
#                'aaData':aaData
#     }
#     return HttpResponse(simplejson.dumps(result),content_type="application/json")
#
# def staff_save(request):
#     _id = request.POST.get('id')
#     name = request.POST.get('name')
#     department = request.POST.get('department')
#     comment = request.POST.get('comment')
#
#     orm = user.objects.filter(name=name)
#     if orm:
#         return HttpResponse(simplejson.dumps({'code':1,'msg':u'该员工已存在'}),content_type="application/json")
#
#     if _id =='':
#         orm = user(name=name,department=department,comment=comment)
#     else:
#         orm = user.objects.get(id=int(_id))
#         orm.name = name
#         orm.department = department
#         orm.comment = comment
#
#     try:
#         orm.save()
#         return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
#     except Exception,e:
#         logger.error(e,comment)
#         return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
#
# def staff_del(request):
#     _id = request.POST.get('id')
#     orm = user.objects.get(id=_id)
#
#     try:
#         orm.delete()
#         return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
#     except Exception,e:
#         return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
#

######################订餐#############################
@login_required
def order_form(request):
    path = request.path.split('/')[1]
    return render_to_response('order_form/order_form.html',{'user':'%s%s' % (request.user.last_name,request.user.first_name),
                                                       'path1':'order_manage',
                                                       'path2':path,
                                                       'page_name1':u'订餐管理',
                                                       'page_name2':u'订餐'})

@login_required
def order_form_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    type = request.POST.get('type')
    begin = request.POST.get('begin')
    end = request.POST.get('end')

    begin = begin.split('-')
    end = end.split('-')

    begin = datetime.datetime(int(begin[0]),int(begin[1]),int(begin[2]))
    try:
        end = datetime.datetime(int(end[0]),int(end[1]),int(end[2])+1)
    except ValueError:
        end = datetime.datetime(int(end[0]),int(end[1]),int(end[2]),23,59)

    aaData = []
    sort = ['name','type','None','add_time','order_name','comment','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = order.objects.filter(add_time__range=(begin,end)).filter(type=type) \
                                                .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = order.objects.filter(add_time__range=(begin,end)).filter(type=type).count()
        else:
            result_data = order.objects.filter(add_time__range=(begin,end)).filter(type=type).filter( \
                                               Q(name__contains=sSearch) | \
                                               Q(type__contains=sSearch) | \
                                               Q(order_name__contains=sSearch) | \
                                               Q(comment__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = order.objects.filter(add_time__range=(begin,end)).filter(type=type).filter( \
                                               Q(name__contains=sSearch) | \
                                               Q(type__contains=sSearch) | \
                                               Q(order_name__contains=sSearch) | \
                                               Q(comment__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = order.objects.filter(add_time__range=(begin,end)).filter(type=type).order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = order.objects.filter(add_time__range=(begin,end)).filter(type=type).count()
        else:
            result_data = order.objects.filter(add_time__range=(begin,end)).filter(type=type).filter( \
                                               Q(name__contains=sSearch) | \
                                               Q(type__contains=sSearch) | \
                                               Q(order_name__contains=sSearch) | \
                                               Q(comment__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = order.objects.filter(add_time__range=(begin,end)).filter(type=type).filter( \
                                               Q(name__contains=sSearch) | \
                                               Q(type__contains=sSearch) | \
                                               Q(order_name__contains=sSearch) | \
                                               Q(comment__contains=sSearch)).count()
    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.type,
                       '2':1,
                       '3':str(i.add_time).split('+')[0],
                       '4':i.order_name,
                       '5':i.comment,
                       '6':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def order_form_dropdown(request):
    _id = request.POST.get('id')
    result = {}
    result['list'] = []
    result['edit'] = []
    if _id == None:
        orm = User.objects.all()
        for i in orm:
            if not i.first_name:continue
            result['list'].append({'text':i.first_name,'id':i.id})
    else:
        pass
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def order_form_save(request):
    _id = request.POST.get('id')
    name = request.POST.get('name')
    type = request.POST.get('type')
    comment = request.POST.get('comment')
    time_now = datetime.datetime.now().time()
    begin = datetime.datetime.now().date()
    end = datetime.datetime.now() + datetime.timedelta(1)
    end = end.date()

    if not request.user.is_staff:
        if type == u'午餐' and time_now > datetime.time(11,00):
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'已经超过午餐订餐时间'}),content_type="application/json")
        elif type == u'晚餐' and time_now > datetime.time(16,30):
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'已经超过晚餐订餐时间'}),content_type="application/json")
    try:
        if _id =='':
            for i in name.split(','):
                check_orm = order.objects.filter(add_time__range=(begin,end)).filter(name=i).filter(type=type)
                if check_orm:
                    return HttpResponse(simplejson.dumps({'code':1,'msg':u'您已订过餐'}),content_type="application/json")
                orm = order(name=i,type=type,comment=comment,order_name=request.user.first_name)
                orm.save()
        # else:
        #     orm = user.objects.get(id=int(_id))
        #     orm.name = name
        #     orm.department = department
        #     orm.comment = comment
        #
        #
        # orm.save()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'订餐成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e,comment)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def order_form_del(request):
    _id = request.POST.get('id')
    time_now = datetime.datetime.now().time()
    begin = datetime.datetime.now().date()
    end = datetime.datetime.now() + datetime.timedelta(1)
    end = end.date()
    try:
        orm = order.objects.get(id=_id)
        if orm.type == u'午餐' and time_now > datetime.time(11,00):
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'已经超过午餐订餐时间，无法删除'}),content_type="application/json")
        elif orm.type == u'晚餐' and time_now > datetime.time(16,30):
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'已经超过晚餐订餐时间，无法删除'}),content_type="application/json")
        if orm.order_name != request.user.first_name and orm.name != request.user.first_name:
            return HttpResponse(simplejson.dumps({'code':1,'msg':u'您不能删除别人的订餐'}),content_type="application/json")
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")
