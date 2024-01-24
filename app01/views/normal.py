from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from datetime import datetime

# from app01.models import UserInfo, OperationRecord
from app01.models import UserInfo, OperationRecord, UpdateRecords


# Create your views here.


def index(request):
    return render(request, 'index.html')


def login(request):
    # 如果已登录就跳转至控制台
    if request.session.get("info"):
        return redirect("/console/")
    
    if request.method != "POST":
        return render(request, 'login.html')
    
    # 获取表单数据
    loginData = request.POST

    # 数据库查询用户名
    row_obj = UserInfo.objects.filter(username=loginData['username']).first()

    # 成功则session登录并跳转控制台
    if row_obj and row_obj.password == loginData['password']:
        print(row_obj.id, row_obj.username, row_obj.password)
        # 写入用户id、用户名、状态
        request.session['info'] = {
            'id': row_obj.id, 'username': row_obj.username, 'state': row_obj.state}
        request.session.set_expiry(60*60*2)
        return redirect("/console/")

    # 未成功则返回错误信息
    loginError = '用户名或密码错误'
    print(loginError)
    return render(request, 'login.html', {
        'loginData': loginData,
        'loginError': loginError
    })


def docs(request):
    return render(request, 'docs.html')


def connect(request):
    return render(request, 'connect.html')


def console(request):
    # 获取登录信息
    userSession = request.session.get("info")
    
    userInfo = {}
    userOpn = {}
    # 获取用户数据
    if userSession:
        # 如果是管理员则跳转至管理页面
        if userSession['state'] == '管理员':
            return redirect('/manage-user/')
    
        # 用户信息，转字典以添加数据
        userInfo = UserInfo.objects.filter(id=userSession['id']).first().__dict__
        # 计算建站累计时间与距离下次月付的时间
        nowDate = datetime.now().date()
        userInfo['accumulated_days'] = (nowDate - userInfo['create_time']).days
        userInfo['time_until_next_monthly_payment'] = (userInfo['next_monthly_payment_date'] - nowDate).days
        print(userInfo)

        # 获取欠费天数：如果状态为已欠费，欠费日期至今时间就为欠费时间
        userInfo['due_days'] = 0
        if userInfo['state'] == '已欠费':
            if userInfo['due_date']:    # 确保due_date有值，保证其不出错
                userInfo['due_days'] = (nowDate - userInfo['due_date']).days
                userInfo['due_date'] = userInfo['due_date'].strftime("%m-%d")
            else:
                userInfo['due_date'] = 'error'
        else:
            userInfo['due_date'] = '无'
            
        # 获取用户操作记录
        userOpn = OperationRecord.objects.filter(userid=userSession['id']).order_by('-datatime')

    return render(request, 'console.html', {
        'userSession': userSession, 'userInfo': userInfo, 'userOpn': userOpn})


def logout(request):
    """登出"""
    request.session.clear()
    return redirect('/login/')


def demo_a(request):
    return render(request, 'demo-a.html')


def demo_b(request):
    return render(request, 'demo-b.html')


def demo_c(request):
    return render(request, 'demo-c.html')


def demo_d(request):
    return render(request, 'demo-d.html')

