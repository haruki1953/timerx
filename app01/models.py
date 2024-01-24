from django.db import models

# Create your models here.


class UserInfo(models.Model):
    """用户表"""
    username = models.CharField(verbose_name="用户名", max_length=64)
    password = models.CharField(verbose_name="密码", max_length=64)
    phonenum = models.CharField(verbose_name="电话号码", max_length=64,default='无')
    level = models.CharField(verbose_name="用户级别", max_length=64,default='无')
    domain_name = models.CharField(verbose_name="域名", max_length=64,default='无')
    member_points = models.DecimalField(
        verbose_name="会员积分", max_digits=10, decimal_places=2, default=0)
    account = models.DecimalField(
        verbose_name="账户余额", max_digits=10, decimal_places=2, default=0)
    create_time = models.DateField(verbose_name="建站日期")
    last_monthly_payment_date = models.DateField(verbose_name="上次月付日期")
    next_monthly_payment_date = models.DateField(verbose_name="下次月付日期")
    monthly_payment_amount = models.DecimalField(
        verbose_name="月付金额", max_digits=10, decimal_places=2, default=0)
    domain_name_expiration_date = models.DateField(verbose_name="域名到期日期")
    domain_name_renewal_amount = models.DecimalField(
        verbose_name="域名续费金额", max_digits=10, decimal_places=2, default=0)
    notes = models.CharField(verbose_name="备注", max_length=1024,default='无')
    state = models.CharField(verbose_name="状态", max_length=64,default='无')
    # remaining_modifications = models.IntegerField(verbose_name="剩余修改次数", default=0)
    # monthly_modifications = models.IntegerField(verbose_name="每月修改次数", default=0)
    due_date = models.DateField(verbose_name="欠费日期", null=True, blank=True)

class OperationRecord(models.Model):
    """操作记录表"""
    userid = models.IntegerField(verbose_name="用户id",default=0)
    updateid = models.IntegerField(verbose_name="所属更新记录id",default=0)
    operation_type = models.CharField(verbose_name="操作类型", max_length=64)
    operation_content = models.CharField(verbose_name="操作内容", max_length=256)
    amount_changes = models.DecimalField(
        verbose_name="账户余额变动", max_digits=10, decimal_places=2, default=0)
    datatime = models.DateTimeField(verbose_name="操作时间")
    notes = models.CharField(verbose_name="备注", max_length=256,default='无')

class UpdateRecords(models.Model):
    """更新记录表"""
    update_type = models.CharField(verbose_name="更新类型", max_length=64)
    update_usernum = models.IntegerField(verbose_name="更新用户数量",default=0)
    add_operationnum = models.IntegerField(verbose_name="添加操作记录数量",default=0)
    update_content = models.CharField(verbose_name="更新内容", max_length=1024)
    updatetime = models.DateTimeField(verbose_name="更新时间")
    notes = models.CharField(verbose_name="备注", max_length=256,default='无')

