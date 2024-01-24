import os, sys, time
from datetime import datetime, timedelta
import threading
import django
from django.utils import timezone

base_apth = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(base_apth)
# 将项目路径加入到系统path中，这样在导入模型等模块时就不会报模块找不到了
sys.path.append(base_apth)
os.environ['DJANGO_SETTINGS_MODULE'] ='timerx.settings' # 注意：timerx 是我的模块名，你在使用时需要跟换为你的模块
django.setup()
# from app01.models import UserInfo, OperationRecord
from app01.models import UserInfo, OperationRecord, UpdateRecords


minCount = 0    # 分钟计数，用来控制每个任务的间隔执行


def interval_min(min):
    '''
    判断是否间隔min的分钟数
    '''
    global minCount  # 声明全局变量
    # 增加鲁棒性
    if min == 0:
        return True
    if minCount % min == 0:
        return True
    return False


def interval_h(hour):
    '''
    判断是否间隔hour的小时数
    '''
    return interval_min(hour*60)


def user_check():
    '''
    用户信息检查更新
    '''
    print('【用户信息检查更新】')
    nowDate = datetime.now().date()  # 获取现在的日期
    # 更新记录
    updateUserNum = 0       # 统计更新的用户数
    addOpnNum = 0           # 统计添加的操作记录数量
    updateContent = ''      # 更新内容，内容为“(id,用户),(id,操作类型)...;...”
    """
    通过临时记录以获取确定的id（处理用户信息添加操作记录时要保存其id）
    先搜索是否有临时记录，没有再创建
    """
    """ 临时记录 """
    tempUpdateRecord = UpdateRecords.objects.filter(update_type='temp').first()
    if not tempUpdateRecord:
        tempUpdateRecord = UpdateRecords.objects.create(
            update_type='temp',
            update_usernum=0,
            add_operationnum=0,
            update_content='temp',
            updatetime=datetime.now(),
        )

    """ 临时记录 END """
    userList = UserInfo.objects.all()   # 数据库获取用户信息
    if not userList:    # 无数据返回
        print('没有用户数据')
        return 
    for user in userList:               # 遍历检查
        # print(user)
        # 统计更新数据准备
        isUserUpdate = False            # 用户是否更新
        addOpnNumOfUser = 0             # 属于用户的操作数
        updateContentOfUser = '({id},{name})'.format(
            id=user.id, name=user.username)    # 用户的更新信息

        """
        以状态区分处理用户信息
        """
        if user.state == '管理员':  # 管理员不做检查
            pass
        # 停止运行状态
        elif user.state == '停止运行':    # 停止运行则不做检查
            pass
        # 已欠费状态
        elif user.state == '已欠费':
            if user.account >= 0:       # 余额为正则变回运行中。其实充值后就会立刻修改，此为增强鲁棒性
                """ 欠费恢复用户信息修改操作 """
                UserInfo.objects.filter(id=user.id).update(
                    state='运行中')  # 修改用户信息
                opn = OperationRecord.objects.create(  # 添加操作记录
                    userid=user.id,
                    updateid=tempUpdateRecord.id,
                    operation_type='欠费恢复',
                    operation_content='已从欠费状态中恢复，余额'+str(user.account)+'元',
                    amount_changes=0,
                    datatime=datetime.now()
                )
                isUserUpdate = True
                addOpnNumOfUser += 1
                updateContentOfUser += ',({id},{name})'.format(
                    id=opn.id, name=opn.operation_type)
                """ 欠费恢复用户信息修改操作 END """
            elif (nowDate - user.last_monthly_payment_date).days > 20:    # 欠费超20天网站将停止运行
                """ 停止运行用户信息修改操作 """
                UserInfo.objects.filter(id=user.id).update(
                    state='停止运行')    # 修改用户信息
                opn = OperationRecord.objects.create(  # 添加操作记录
                    userid=user.id,
                    updateid=tempUpdateRecord.id,
                    operation_type='停止运行',
                    operation_content='欠费超20天，网站停止运行',
                    amount_changes=0,
                    datatime=datetime.now()
                )
                isUserUpdate = True
                addOpnNumOfUser += 1
                updateContentOfUser += ',({id},{name})'.format(
                    id=opn.id, name=opn.operation_type)
                """ 停止运行用户信息修改操作 END """

        # 正常状态
        else:
            if user.account < 0:    # 用户余额小于0修改状态为已欠费。其实扣费后就会立刻判断并修改，此为增强鲁棒性
                """ 已欠费用户信息修改操作 """
                UserInfo.objects.filter(id=user.id).update( # 修改用户信息
                    state='已欠费', 
                    due_date=nowDate    # 欠费开始日期设置为当前
                    )
                opn = OperationRecord.objects.create(  # 添加操作记录
                    userid=user.id,
                    updateid=tempUpdateRecord.id,
                    operation_type='已欠费',
                    operation_content='您已欠费，余额：' + \
                    str(user.account)+'元。欠费超20天网站将停止运行',
                    amount_changes=0,
                    datatime=datetime.now()
                )
                isUserUpdate = True
                addOpnNumOfUser += 1
                updateContentOfUser += ',({id},{name})'.format(
                    id=opn.id, name=opn.operation_type)
                """ 已欠费用户信息修改操作 END """
            # 检查付款
            if user.next_monthly_payment_date <= nowDate:   # 到期月付
                lastDate = user.next_monthly_payment_date   # 修改上次月付时间
                nextDate = lastDate + timedelta(days=30)    # 修改下次月付加30天
                accountAfterPay = user.account - user.monthly_payment_amount    # 用户余额扣费
                """ 月付扣费用户信息修改操作 """
                UserInfo.objects.filter(id=user.id).update(  # 修改用户信息
                    last_monthly_payment_date=lastDate,
                    next_monthly_payment_date=nextDate,
                    account=accountAfterPay
                )
                opn = OperationRecord.objects.create(  # 添加操作记录
                    userid=user.id,
                    updateid=tempUpdateRecord.id,
                    operation_type='月付扣费',
                    operation_content='月付扣费' + \
                    str(user.monthly_payment_amount) + \
                    '元，余额：'+str(accountAfterPay)+'元',
                    amount_changes=-user.monthly_payment_amount,
                    datatime=datetime.now()
                )
                isUserUpdate = True
                addOpnNumOfUser += 1
                updateContentOfUser += ',({id},{name})'.format(
                    id=opn.id, name=opn.operation_type)
                """ 月付扣费用户信息修改操作 END """
                # 付款后用户余额小于0修改状态为已欠费
                if accountAfterPay < 0:
                    """ 已欠费用户信息修改操作 """
                    # 注意此处用户余额扣费，应为accountAfterPay，而不是user.account
                    UserInfo.objects.filter(id=user.id).update( # 修改用户信息
                        state='已欠费', 
                        due_date=nowDate    # 欠费开始日期设置为当前
                        )
                    opn = OperationRecord.objects.create(  # 添加操作记录
                        userid=user.id,
                        updateid=tempUpdateRecord.id,
                        operation_type='已欠费',
                        operation_content='您已欠费，余额：' + \
                        str(accountAfterPay)+'元。欠费超20天网站将停止运行',
                        amount_changes=0,
                        datatime=datetime.now()
                    )
                    isUserUpdate = True
                    addOpnNumOfUser += 1
                    updateContentOfUser += ',({id},{name})'.format(
                        id=opn.id, name=opn.operation_type)
                    """ 已欠费用户信息修改操作 END """

        """ 
        以状态区分处理用户信息 END 
        """
        # 统计更新数据
        if isUserUpdate:
            updateUserNum += 1
            addOpnNum += addOpnNumOfUser
            updateContent += updateContentOfUser + ';'

    # 更新记录保存，因前面创建了临时占位的更新记录，所以需根据其id修改其数据
    if updateUserNum:   # 存在更新，保存数据
        UpdateRecords.objects.filter(id=tempUpdateRecord.id).update(
            update_type='用户信息更新',
            update_usernum=updateUserNum,
            add_operationnum=addOpnNum,
            update_content=updateContent[:1000],
            updatetime=datetime.now(),
        )
        print('做出以下更新：')
        print('更新用户', updateUserNum, '个')
        print('做出操作', addOpnNum, '条')
        print('更新内容：')
        print(updateContent)
    else:
        """
        无更新内容仍每天写一条记录：
        查询上一条用户信息更新的时间，
        判断此次和最近的一条记录不是同一天，
        或表内无数据后保存例行检查记录。
        注意： 因指定update_type='用户信息更新'，所以临时占位的更新记录不会被查到，不用担心其时间
        """
        print('无更新内容')
        
        # 查询上一条用户信息更新的时间
        lastUpdateTime = False
        lastUpdate = UpdateRecords.objects.filter(
            update_type='用户信息更新').order_by('-updatetime').first()
        if lastUpdate:  # 确保在有数据时再访问其updatetime属性
            lastUpdateTime = lastUpdate.updatetime

        if not lastUpdateTime or datetime.now().date() != lastUpdateTime.date():
            dataInfo = UpdateRecords.objects.filter(id=tempUpdateRecord.id).update(
                update_type='用户信息更新',
                update_usernum=0,
                add_operationnum=0,
                update_content='例行检查，无更新内容',
                updatetime=datetime.now(),
            )
            print('今日第一次检查')
        # else:   # 无更新内容且今日已有更新
           



def main():
    '''
    主函数，用于定时任务
    '''
    global minCount
    try:
        # 循环执行任务
        while True:
            if interval_h(2):
                print(str(datetime.now()) + "【执行用户检查】")
                user_check()
                
            if interval_min(1):
                print('循环检查'+str(minCount))

            time.sleep(60)  # 睡眠1分钟
            minCount += 1
            if minCount == 32760:
                minCount = 0
    except Exception as e:
        print('发生异常：%s' % str(e))

def test():
    print('已进入测试函数')
    # now1 = datetime.now()
    # now2 = timezone.now()
    # print(now1)
    # print(now2)
    testdata = UpdateRecords.objects.filter(update_type='temp').first()
    print(testdata.__dict__)

if __name__ == '__main__':
    funDict = { # 通过函数字典直接映射传入的参数
        'main': main,
        'usercheck': user_check,
        'test': test
        }
    if len(sys.argv) < 2:
        print('请提供参数')
    elif sys.argv[1] not in funDict:
        print('参数错误，参数如下')
        print(funDict)
    else:   #映射传入的参数执行对应函数
        print(datetime.now())
        funDict[sys.argv[1]]()



"""
myTest.objects.create(notes='任务2',datatime=datetime.now())
userList = UserInfo.objects.all()
num = userList[0].account
print('余额'+str(num))
print(type(num))

"""
