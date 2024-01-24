from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from datetime import datetime , timedelta

# from app01.models import UserInfo, OperationRecord
from app01.models import UserInfo, OperationRecord, UpdateRecords

from decimal import Decimal


# 充值
def user_recharge(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = Decimal(request.POST.get('value'))

    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value'] or opnContent['value'] <= 0:
        dataNormal = False
        alertType = 'danger'
        alertContent = '充值失败，充值数额必须为正数'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '充值失败，未查询到id:'+str(opnContent['id'])

    
    # 数据正常，修改数据库用户信息
    if dataNormal:
        nowAccount = userData.account + opnContent['value']
        """ 充值操作 """
        UserInfo.objects.filter(id=userData.id).update(account=nowAccount)
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='充值',  # 操作类型充值
            operation_content='充值'+str(opnContent['value'])+'元，余额'+str(nowAccount)+'元',
            amount_changes=opnContent['value'],
            datatime=datetime.now()
        )
        """ 充值操作END """
        alertType = 'success'
        alertContent = '充值成功！'
        # 如果状态为已欠费，且现在余额大于或等于0，则恢复为正常运行
        if userData.state == '已欠费' and nowAccount >= 0:
            """ 欠费恢复 """
            UserInfo.objects.filter(id=userData.id).update(state='运行中')
            OperationRecord.objects.create(  # 添加操作记录
                userid=userData.id,
                updateid=0,
                operation_type='欠费恢复',
                operation_content='已从欠费状态中恢复，余额'+str(nowAccount)+'元',
                amount_changes=0,
                datatime=datetime.now()
            )
            """ 欠费恢复END """
            alertContent += '并从欠费状态恢复'

    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 扣费
def user_refund(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作内容
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = Decimal(request.POST.get('value'))
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value'] or opnContent['value'] <= 0:
        dataNormal = False
        alertType = 'danger'
        alertContent = '扣费失败，扣费数额必须为正数'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '扣费失败，未查询到id:'+str(opnContent['id'])
    elif opnContent['value'] > userData.account:
        dataNormal = False
        alertType = 'danger'
        alertContent = '扣费失败，扣费金额不能大于账户余额'

    # 数据正常，修改数据库用户信息
    if dataNormal:
        nowAccount = userData.account - opnContent['value']
        """ 扣费操作 """
        UserInfo.objects.filter(id=userData.id).update(account=nowAccount)
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='扣费',  # 操作类型扣费
            # 操作内容
            operation_content='扣费'+str(opnContent['value'])+'元，余额'+str(nowAccount)+'元',
            amount_changes=-opnContent['value'], # 余额变动
            datatime=datetime.now()
        )
        """ 扣费操作END """
        alertType = 'success'
        alertContent = '扣费成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 发送消息
def user_message(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = request.POST.get('value')
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '消息发送失败，消息不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '消息发送失败，未查询到id:'+str(opnContent['id'])
    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='发送消息',  # 操作类型发送消息
            operation_content=opnContent['value'], # 消息内容
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '消息发送成功！'

 
    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 备注修改
def user_changeNotes(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = request.POST.get('value')
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()


    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '备注修改失败，备注不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '备注修改失败，未查询到id:'+str(opnContent['id'])
    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(notes=opnContent['value'])
        # 修改备注无需发送消息
        alertType = 'success'
        alertContent = '备注修改成功！'

 
    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 修改电话号码
def user_changePhonenum(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = request.POST.get('value')
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '电话号码修改失败，电话号码不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '电话号码修改失败，未查询到id:'+str(opnContent['id'])

    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(phonenum=opnContent['value'])
        # 修改电话号码无需发送消息
        alertType = 'success'
        alertContent = '电话号码修改成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 修改用户名
def user_changeUsername(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = request.POST.get('value')
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '用户名修改失败，用户名不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '用户名修改失败，未查询到id:'+str(opnContent['id'])

    # 用户名不能重复
    usernameExists = UserInfo.objects.filter(username=opnContent['value']).first()
    if usernameExists:  # 用户名已存在
        dataNormal = False
        alertType = 'danger'
        alertContent = '用户名修改失败，用户名不能重复，重复用户的id为{id}'.format(
            id=usernameExists.id,
        )
    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(username=opnContent['value'])
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='修改用户名',  # 操作类型
            operation_content='用户名已从{old}修改为{new}'.format(old=userData.username,new=opnContent['value']),
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '用户名修改成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 修改密码
def user_changePassword(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = request.POST.get('value')
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '密码修改失败，密码不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '密码修改失败，未查询到id:'+str(opnContent['id'])
    elif opnContent['value'] == userData.password:
        dataNormal = False
        alertType = 'warning'
        alertContent = '密码未修改，修改的密码和当前一样'
    
    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(password=opnContent['value'])
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='修改密码',  # 操作类型
            operation_content='密码修改成功',
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '密码修改成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 月付金额变动
def user_monthly_payment_amount_modification(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = Decimal(request.POST.get('value'))
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value'] or opnContent['value'] <= 0:
        dataNormal = False
        alertType = 'danger'
        alertContent = '月付金额变动失败，月付金额必须为正数'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '月付金额变动失败，未查询到id:'+str(opnContent['id'])
    elif opnContent['value'] == userData.monthly_payment_amount:
        dataNormal = False
        alertType = 'warning'
        alertContent = '月付金额未修改，修改的月付金额和当前一样'
    

    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(monthly_payment_amount=opnContent['value'])
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='月付金额变动',  # 操作类型
            operation_content='月付金额变动为{}元'.format(opnContent['value']),
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '月付金额变动成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 修改域名
def user_domain_name_modification(request):
    # 非post请求报错
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = request.POST.get('value')
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名修改失败，域名不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名修改失败，未查询到id:'+str(opnContent['id'])
    elif opnContent['value'] == userData.domain_name:
        dataNormal = False
        alertType = 'warning'
        alertContent = '域名未修改，修改的域名和当前一样'

    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(domain_name=opnContent['value'])
        alertType = 'success'
        alertContent = '域名修改成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 修改域名到期日期
def user_domain_name_expiration_date_modification(request):
    # 非post请求报错
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    try:
        opnContent['value'] = datetime.strptime(request.POST.get('value'),'%Y-%m-%d').date()
    except:
        opnContent['value'] = 0
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value']:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名到期日期修改失败，日期不能为空'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名到期日期修改失败，未查询到id:'+str(opnContent['id'])

    if opnContent['value'] == userData.domain_name_expiration_date:
        dataNormal = False
        alertType = 'warning'
        alertContent = '域名到期日期未修改，修改的日期和当前一样'

    
    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(domain_name_expiration_date=opnContent['value'])
        alertType = 'success'
        alertContent = '域名到期日期修改成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 域名续费金额变动
def user_domain_name_renewal_amount_modification(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    opnContent['value'] = Decimal(request.POST.get('value'))
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not opnContent['value'] or opnContent['value'] <= 0:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名续费金额变动失败，域名续费金额必须为正数'
    elif not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名续费金额变动失败，未查询到id:'+str(opnContent['id'])
    elif opnContent['value'] == userData.domain_name_renewal_amount:
        dataNormal = False
        alertType = 'warning'
        alertContent = '域名续费金额未修改，修改的域名续费金额和当前一样'
    

    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(domain_name_renewal_amount=opnContent['value'])
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='域名续费金额变动',  # 操作类型
            operation_content='域名续费金额变动为{}元'.format(opnContent['value']),
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '域名续费金额变动成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 域名续费
def user_domain_name_renewal(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名续费失败，未查询到id:'+str(opnContent['id'])
    elif userData.account < userData.domain_name_renewal_amount:
        dataNormal = False
        alertType = 'danger'
        alertContent = '域名续费失败，余额不足'
    

    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        # 余额减少，域名到期日期加一年，
        nowAccount = userData.account - userData.domain_name_renewal_amount
        nowExpirationDate = userData.domain_name_expiration_date + timedelta(days=365)
        UserInfo.objects.filter(id=opnContent['id']).update(
            account=nowAccount,
            domain_name_expiration_date=nowExpirationDate
        )
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='域名续费',  # 操作类型
            operation_content='您的域名域名已续费',
            amount_changes=-userData.domain_name_renewal_amount,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '域名续费成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 从停止运行状态恢复
def user_stop_operation(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '手动停止运行失败，未查询到id:'+str(opnContent['id'])
    elif userData.state == '停止运行':
        dataNormal = False
        alertType = 'warning'
        alertContent = '手动停止运行失败，用户已为停止运行状态'
    

    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        UserInfo.objects.filter(id=opnContent['id']).update(
            state='停止运行'
        )
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='停止运行',  # 操作类型
            operation_content='网站已停止运行',
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '网站已停止运行'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


# 从停止运行状态恢复
def user_resume_operation(request):
    # 非post请求报错   
    if request.method != "POST":
        return HttpResponse('请以正确方式进入')
    
    # 获取操作数据
    opnContent = {}
    opnContent['id'] = int(request.POST.get('id'))
    
    # 从数据库获取用户数据
    userData = UserInfo.objects.filter(id=opnContent['id']).first()

    # 检查数据
    alertType = '' # 提示类型 success danger warning info 
    alertContent = '' # 提示内容
    dataNormal = True
    if not userData:
        dataNormal = False
        alertType = 'danger'
        alertContent = '运行状态恢复失败，未查询到id:'+str(opnContent['id'])
    elif userData.state != '停止运行':
        dataNormal = False
        alertType = 'warning'
        alertContent = '运行状态恢复失败，用户不为停止运行状态'
    

    # 数据正常，数据库操作记录表添加信息
    if dataNormal:
        # 余额归零，上次月付为当前日期，下次月付为30天后，状态为运行中
        nowDate = datetime.now().date()
        nowAccount = 0
        now_last_monthly_payment_date = nowDate
        now_next_monthly_payment_date = nowDate + timedelta(days=30)
        nowState = '运行中'
        UserInfo.objects.filter(id=opnContent['id']).update(
            account=nowAccount,
            last_monthly_payment_date=now_last_monthly_payment_date,
            next_monthly_payment_date=now_next_monthly_payment_date,
            state=nowState
        )
        OperationRecord.objects.create(
            userid=userData.id,     # 操作的用户id
            updateid=0,             # 0表示手动操作
            operation_type='恢复运行',  # 操作类型
            operation_content='网站已恢复运行',
            amount_changes=0,
            datatime=datetime.now()
        )
        alertType = 'success'
        alertContent = '运行状态恢复成功！'


    # 返回路径拼接用户id与提示信息
    returnPath = '/user/?id={id}&alert={alert}&content={content}'.format(
        id=str(opnContent['id']),
        alert=alertType,
        content=alertContent
    )
    return redirect(returnPath)


