# Generated by Django 3.0.6 on 2023-10-12 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OperationRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField(default=0, verbose_name='用户id')),
                ('updateid', models.IntegerField(default=0, verbose_name='所属更新记录id')),
                ('operation_type', models.CharField(max_length=64, verbose_name='操作类型')),
                ('operation_content', models.CharField(max_length=64, verbose_name='操作内容')),
                ('amount_changes', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='账户余额变动')),
                ('datatime', models.DateTimeField(verbose_name='操作时间')),
                ('notes', models.CharField(default='无', max_length=256, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='UpdateRecords',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_type', models.CharField(max_length=64, verbose_name='更新类型')),
                ('update_usernum', models.IntegerField(default=0, verbose_name='更新用户数量')),
                ('add_operationnum', models.IntegerField(default=0, verbose_name='添加操作记录数量')),
                ('update_content', models.CharField(max_length=1024, verbose_name='更新内容')),
                ('updatetime', models.DateTimeField(verbose_name='更新时间')),
                ('notes', models.CharField(default='无', max_length=256, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('phonenum', models.CharField(default='无', max_length=64, verbose_name='电话号码')),
                ('level', models.CharField(default='无', max_length=64, verbose_name='用户级别')),
                ('domain_name', models.CharField(default='无', max_length=64, verbose_name='域名')),
                ('member_points', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='会员积分')),
                ('account', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='账户余额')),
                ('create_time', models.DateField(verbose_name='建站日期')),
                ('last_monthly_payment_date', models.DateField(verbose_name='上次月付日期')),
                ('next_monthly_payment_date', models.DateField(verbose_name='下次月付日期')),
                ('monthly_payment_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='月付金额')),
                ('domain_name_expiration_date', models.DateField(verbose_name='域名到期日期')),
                ('domain_name_renewal_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='域名续费金额')),
                ('notes', models.CharField(default='无', max_length=256, verbose_name='备注')),
                ('state', models.CharField(default='无', max_length=64, verbose_name='状态')),
                ('remaining_modifications', models.IntegerField(default=0, verbose_name='剩余修改次数')),
                ('monthly_modifications', models.IntegerField(default=0, verbose_name='每月修改次数')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='欠费日期')),
            ],
        ),
    ]
