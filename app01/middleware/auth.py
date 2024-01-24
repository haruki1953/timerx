from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 无需登录的路径
        noLoginPath = [
            "/",
            "/index/",
            "/login/",
            "/docs/",
            "/connect/",
            "/demo-a/",
            "/demo-b/",
            "/demo-c/",
            "/demo-d/"
            ]
        # 普通用户可以访问的路径
        normalUserPath = [
            "/console/",
            "/logout/"
        ]

        # 0.当用户访问的路径无需登录时放行
            # request.path_info 获取当前用户请求的URL
        if request.path_info in noLoginPath:
            print('访问的路径无需登录，放行')
            return
        
        
        # 1.获取用户登录信息session
        #   如果没登录，则回到登录页面
        info_dict = request.session.get("info")
        # print(info_dict)
        if not info_dict:
            print('未登录，拦截')
            return redirect('/login/')
        
        # 2.接下来的用户就都是已登录的
        #   如果访问的路径是普通用户可以访问的，则通过
        if request.path_info in normalUserPath:
            return
        
        # 3.接下来的路径就都不是是普通用户可以访问的
        #   判断状态不是管理员则返回至index界面
        if info_dict['state'] != '管理员':
            return redirect('/index/')
        
        # 4.到这里还没返回的就是管理员，通过
        
        return 
