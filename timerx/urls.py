"""
URL configuration for timerx project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from app01.views import normal
from app01.views import myAdmin
from app01.views import userOpn


urlpatterns = [
    path('', normal.index),
    path('index/', normal.index),
    path('login/', normal.login),
    path('docs/', normal.docs),
    path('connect/', normal.connect),
    path('console/', normal.console),
    path('logout/', normal.logout),
    path('demo-a/', normal.demo_a),
    path('demo-b/', normal.demo_b),
    path('demo-c/', normal.demo_c),
    path('demo-d/', normal.demo_d),

    path('manage-user/', myAdmin.manage_user),
    path('manage-view/', myAdmin.manage_view),
    path('adduser/', myAdmin.adduser),
    path('user/', myAdmin.user),
    path('manage-operation/', myAdmin.manage_operation),
    path('manage-update/', myAdmin.manage_update),

    path('user-recharge/', userOpn.user_recharge),
    path('user-refund/', userOpn.user_refund),
    path('user-message/', userOpn.user_message),
    path('user-changeNotes/', userOpn.user_changeNotes),
    path('user-changePhonenum/', userOpn.user_changePhonenum),
    path('user-changeUsername/', userOpn.user_changeUsername),
    path('user-changePassword/', userOpn.user_changePassword),
    path('user-monthly_payment_amount_modification/', userOpn.user_monthly_payment_amount_modification),
    path('user-domain_name_modification/', userOpn.user_domain_name_modification),
    path('user-domain_name_expiration_date_modification/', userOpn.user_domain_name_expiration_date_modification),
    path('user-domain_name_renewal_amount_modification/', userOpn.user_domain_name_renewal_amount_modification),
    path('user-domain_name_renewal/', userOpn.user_domain_name_renewal),
    path('user-stop_operation/', userOpn.user_stop_operation),
    path('user-resume_operation/', userOpn.user_resume_operation),

]
