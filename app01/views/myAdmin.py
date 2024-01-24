from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from datetime import datetime , timedelta

# from app01.models import UserInfo, OperationRecord
from app01.models import UserInfo, OperationRecord, UpdateRecords

from decimal import Decimal


def manage_user(request):

    """用户管理，查询用户"""
    # 获取登录信息
    userSession = request.session.get("info")

    # 获取视图信息（表项的显示与否）
    viewInfo = request.session.get("viewInfo", {})
    # 没有用户视图信息则赋值默认
    userViewDefault = '用户名 电话号码'
    # userViewAll = '用户id 用户名 密码 电话号码 用户级别 域名 会员积分 账户余额 建站日期 上次月付日期 下次月付日期 月付金额 域名到期日期 域名续费金额 备注 状态 剩余修改次数 每月修改次数'
    userViewInfo = viewInfo.get('user', userViewDefault)
    if not userViewInfo:
        userViewInfo = userViewDefault

    # 根据get请求选择查询
    filterType = request.GET.get('filter', default='all')
    filterValue = request.GET.get('value', default='0')
    filterName = request.GET.get('name', default='全部用户')
    userList = []
    # 查询所有用户（不包括管理员），以id倒序来排序，使后添加的排在前比较方便
    if filterType == 'all': 
        userList = UserInfo.objects.all().exclude(state='管理员').order_by('-id')
    # 按状态查询
    elif filterType == 'state':
        userList = UserInfo.objects.filter(state=filterValue).exclude(state='管理员').order_by('-id')
        # 根据状态改变排序方式
        if filterValue == '已欠费':
            userList = userList.order_by('due_date')
    # 按距离域名过期的天数查询
    elif filterType == 'domain_name_expiration_date': 
        tempDate = datetime.now().date() + timedelta(days=int(filterValue))
        userList = UserInfo.objects.filter(domain_name_expiration_date__lt=tempDate).exclude(state='管理员').order_by('domain_name_expiration_date')
    # 条件都不符合则查询全部用户
    else: 
        userList = UserInfo.objects.all().exclude(state='管理员').order_by('-id')

    # 再检查用户的数据做出需要的处理
    print(userList)
    myUserList = []
    nowDate = datetime.now().date()
    for user in userList:
        userData = user.__dict__

        # 获取欠费天数：如果状态为已欠费，欠费日期至今时间就为欠费时间
        userData['due_days'] = 0
        if userData['state'] == '已欠费':
            if userData['due_date']:    # 确保due_date有值，保证其不出错
                userData['due_days'] = (nowDate - userData['due_date']).days
                userData['due_date'] = userData['due_date'].strftime("%m-%d")
            else:
                userData['due_date'] = 'error'
        else:
            userData['due_date'] = '无'
        
        # 保存至列表
        myUserList.append(userData)

    return render(request, 'manage-user.html', {
        'userSession': userSession, 
        'userList': myUserList, 
        'userViewInfo': userViewInfo, 
        'filterName': filterName
        })


def manage_view(request):
    """
    视图，控制显示哪些表项
    接收post发送来的数据，保存至session
    """
    if request.method != "POST":
        return HttpResponse('请以正确的方式进入')
    
    viewInfoData = request.POST

    viewType = viewInfoData['viewType'] # 获取视图类型 user update operation
    if viewType not in ['user', 'update', 'operation']:
        return HttpResponse('请以正确的方式进入')

    tempViewInfo = request.session.get("viewInfo")
    # 如果session有viewInfo则添加，如果没有则重新赋值
    if tempViewInfo:
        tempViewInfo[viewType] = viewInfoData['viewStr']
        request.session['viewInfo'] = tempViewInfo
    else:
        request.session['viewInfo'] = {viewType: viewInfoData['viewStr']}
    return redirect("/manage-{}/".format(viewType))


def user(request):
    # 获取登录信息
    userSession = request.session.get("info")

    # 获取传入的参数，用户id
    userId = int(request.GET.get('id', default=0))
    if not userId:
        return redirect("/manage-user/")
    
    # 提示信息 从get参数获取
    alert = {}
    alert['type'] = request.GET.get('alert', default='')
    alert['content'] = request.GET.get('content', default='')
    
    # 从数据库获取用户数据
    try:
        userData = UserInfo.objects.filter(id=userId).first().__dict__
    except:
        return HttpResponse('未查询到用户id'+str(userId))


    # 获取用户操作记录
    userOpn = OperationRecord.objects.filter(userid=userId).order_by('-datatime')

    # 获取欠费天数：如果状态为已欠费，欠费日期至今时间就为欠费时间
    nowDate = datetime.now().date()
    userData['due_days'] = 0
    if userData['state'] == '已欠费':
        if userData['due_date']:    # 确保due_date有值，保证其不出错
            userData['due_days'] = (nowDate - userData['due_date']).days
            userData['due_date'] = userData['due_date'].strftime("%m-%d")
        else:
            userData['due_date'] = 'error'
    else:
        userData['due_date'] = '无'

    return render(request, 'user.html', {
        'userSession': userSession, 
        'userData': userData, 
        'userOpn': userOpn,
        'userAlert': alert
        })
    
    
def adduser(request):
    """
    添加用户
    用户名  密码    电话号码    用户级别    域名
    月付金额    域名续费金额    备注
    """
    # 获取登录信息
    userSession = request.session.get("info")

    if request.method != "POST":
        return render(request, 'adduser.html', {'userSession': userSession})

    # 获取表单数据
    userSubmit = {}
    userSubmit['username'] = request.POST.get('username')
    userSubmit['password'] = request.POST.get('password')
    userSubmit['phonenum'] = request.POST.get('phonenum')
    userSubmit['level'] = request.POST.get('level')
    userSubmit['domain_name'] = request.POST.get('domain_name')
    userSubmit['monthly_payment_amount'] = Decimal(request.POST.get('monthly_payment_amount'))
    userSubmit['domain_name_renewal_amount'] = Decimal(request.POST.get('domain_name_renewal_amount'))
    userSubmit['notes'] = request.POST.get('notes')
    print(userSubmit)

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
        # .1不能为空
    for key,value in userSubmit.items():
        if not value:
            dataNormal = False
            alertType = 'danger'
            alertContent = '{}不能为空'.format(key)
            break
    if dataNormal: # 数据不为空
        # .2用户名不能重复
        usernameExists = UserInfo.objects.filter(username=userSubmit['username']).first()
        if usernameExists:  # 用户名已存在
            dataNormal = False
            alertType = 'danger'
            alertContent = '用户名不能重复，重复用户的id为{id}'.format(id=usernameExists.id)
        # .3月付金额必须为正数
        if userSubmit['monthly_payment_amount'] <= 0:
            dataNormal = False
            alertType = 'danger'
            alertContent = '月付金额必须为正数'
        # .4域名续费金额必须为正数
        if userSubmit['domain_name_renewal_amount'] <= 0:
            dataNormal = False
            alertType = 'danger'
            alertContent = '域名续费金额必须为正数'

    # 数据正常添加用户，并返回用户操作界面
    if dataNormal:
        nowDate = datetime.now().date()
        userCreate = UserInfo.objects.create(
            username=userSubmit['username'], # 用户名
            password=userSubmit['password'], # 密码
            phonenum=userSubmit['phonenum'], # 电话号码
            level=userSubmit['level'], # 用户级别
            domain_name=userSubmit['domain_name'], # 域名
            member_points=0, # 会员积分
            account=0, # 账户余额
            create_time=nowDate, # 创建时间
            last_monthly_payment_date=nowDate,  # 上次月付日期
            next_monthly_payment_date=nowDate+timedelta(days=30), # 下次月付日期
            monthly_payment_amount=userSubmit['monthly_payment_amount'], # 月付金额
            domain_name_expiration_date=nowDate+timedelta(days=365), # 域名到期日期
            domain_name_renewal_amount=userSubmit['domain_name_renewal_amount'], # 域名续费金额
            notes=userSubmit['notes'], # 备注
            state='运行中', # 状态
        )
        OperationRecord.objects.create(
            userid=userCreate.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='建站',  # 操作类型
            operation_content='您的网站成功建立',
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '用户添加成功'
        returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(userCreate.id),
        alert=alertType,
        content=alertContent
        )
        return redirect(returnPath)
    

    return render(request, 'adduser.html', {
        'userSession': userSession,
        'userSubmit': userSubmit,
        'userAlert': {'type':alertType,'content':alertContent},
        })


def manage_operation(request):
    """操作记录查看"""
    # 获取登录信息
    userSession = request.session.get("info")
    
    # 获取视图信息（表项的显示与否）
    viewInfo = request.session.get("viewInfo",{})
    # 没有用户视图信息则赋值默认
    opnViewDefault = '用户名 操作内容 操作时间'
    opnViewInfo = viewInfo.get('operation',opnViewDefault)
    if not opnViewInfo:
        opnViewInfo = opnViewDefault

    # 根据get请求选择查询 更新查看中暂不使用
    # filterType = request.GET.get('filter', default='all')
    # filterValue = request.GET.get('value', default='0')
    # filterName = request.GET.get('name', default='全部更新')
    filterName = '操作记录'

    opnList = []
    # 查询所有操作记录，时间倒序
    opnList = OperationRecord.objects.all().order_by('-datatime')
    
    # 遍历处理数据
    allUser = UserInfo.objects.all() #获取所有用户
    idName = {} # 临时用户名id映射字典优化查询
    myOpnList = []
    for opn in opnList:
        opnData = opn.__dict__
        # 用户名查询,临时映射字典优化查询
        idKey = str(opn.userid)
        if idKey not in idName:
            user = allUser.filter(id=opn.userid).first()
            if user:
                idName[idKey] = user.username
            else:
                idName[idKey] = '无'
        
        opnData['username'] = idName[idKey]
        myOpnList.append(opnData)


    return render(request, 'manage-operation.html', {
        'userSession': userSession, 
        'opnList': myOpnList, 
        'opnViewInfo': opnViewInfo, 
        'filterName': filterName
        })


def manage_update(request):
    """更新信息查看"""
    # 获取登录信息
    userSession = request.session.get("info")
    
    # 获取视图信息（表项的显示与否）
    viewInfo = request.session.get("viewInfo",{})
    # 没有用户视图信息则赋值默认
    updateViewDefault = '更新内容 更新时间'
    updateViewInfo = viewInfo.get('update',updateViewDefault)
    if not updateViewInfo:
        updateViewInfo = updateViewDefault

    # 根据get请求选择查询 更新查看中暂不使用
    # filterType = request.GET.get('filter', default='all')
    # filterValue = request.GET.get('value', default='0')
    # filterName = request.GET.get('name', default='全部更新')
    filterName = '更新记录'

    updateList = []
    # 查询所有更新记录，排除temp，时间倒序
    updateList = UpdateRecords.objects.all().exclude(update_type='temp').order_by('-updatetime')
    

    return render(request, 'manage-update.html', {
        'userSession': userSession, 
        'updateList': updateList, 
        'updateViewInfo': updateViewInfo, 
        'filterName': filterName
        })



