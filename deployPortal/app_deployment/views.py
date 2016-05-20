from django.http import HttpResponse, JsonResponse

from django.conf import settings
from django.shortcuts import render
import os
import time
import json
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from murano_connect import utils as m_utils


class IndexView(TemplateView):
    template_name = 'app_deployment.html'

    def get(self, request, *args, **kwargs):   
        
        #packages = m_utils.get_murano_packages()    
        #packages = "{'io.murano.apps.docker.DockerPostgreSQL': {'hash': '4d0200b151c6d50800d433283080888c'}}"
        #packages = json.loads(packages)
       
        context = {
            'some_dynamic_value': 'This text comes from django view!',
            #'packages' : json.dumps(packages),
        }        
        return self.render_to_response(context)
        
        


 
def getindexnew(request):
    
    #packages = m_utils.get_murano_packages()
    
    packages = "{'io.murano.apps.docker.DockerPostgreSQL': {'hash': '4d0200b151c6d50800d433283080888c'}}"
    context = {
        'some_dynamic_value': 'This text comes from django view!',
        'packages' : packages, 
    }    
    
    return render(request, 'app_deployment.html', context)

def installSoftwares(request): 
    
    try:      
        selected_pkgs = request.GET.get('ids')
        selected_pkgs = selected_pkgs.rstrip(',');    
        packagelist = selected_pkgs.split(',')    
        
        #Create environment
        response_env = m_utils.create_environment()
        if response_env['id']:        
            env_id = response_env['id']     
        else:        
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating environment'})
        
        #Create session
        response_sess = m_utils.create_session(env_id)
        if response_sess['id']:
            session_id = response_sess['id']
        else:
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating session'})  
        
        '''
        print "env_id \n "
        print env_id
        print "session_id \n"  
        print session_id
        '''
        msg = ""
        err_msg = ""
        print packagelist
        
        
        
        for package in packagelist:     
            
            #package_name = settings.MURANO_PACKAGE_NAMES[package]     
            package_name = package     
            repo_url = settings.MURANO_PACKAGE_REPO_URL  
            
            #import package
            app_info = m_utils.import_application_package(repo_url, package_name)  
            #print "app_info \n"
            #print app_info
            
            if(app_info['response']['id']):             
                #Add application to environment
                respose_app = m_utils.add_application(env_id, session_id, app_info)
                #print "add application result \n"
                #print respose_app            
            else:            
                err_msg += 'Error occurred while importing package '+package+'\n'
        
        
        #app_info = []
        #respose_app = m_utils.add_application(env_id, session_id, app_info)   
        #Deploy session
        response_deploy = m_utils.deploy_session(env_id, session_id)
            
           
        if response_deploy['status_code'] == 200:
            msg +='Package deployment initiated \n'            
        elif response_deploy['status_code'] == 404:
            err_msg += ' Specified session does not exist \n'             
        elif response_deploy['status_code'] == 401:
            err_msg += ' User is not authorized to access this session \n'             
        elif response_deploy['status_code'] == 403:
            err_msg += ' Session is already deployed or deployment is in progress \n'              
        else:
            err_msg += 'Error occurred while deploying  \n'  
                
        if msg == "":     
            return JsonResponse({'status': 'failed', 'msg': 'Submission completed with below messages \n'+err_msg})     
        else:
            return JsonResponse({'status': 'success', 'msg': 'Submission completed with below messages \n'+msg+err_msg,'envid':env_id,'sessid':session_id})
        
    except Exception as e:
        return JsonResponse({'status': 'failed', 'msg': 'Exception occurred while deploying packages'})     
    
    
def getDeployInfo(request):    
    
    '''
    env_id = request.GET.get('envid')
    session_id = request.GET.get('sessid')     
    resp =m_utils.get_session_deatils(env_id, session_id) 
    if resp !=False:
        return JsonResponse({'status': 'success', 'state': resp['state']})   
    else:
        return JsonResponse({'status': 'failed', 'msg': 'Error occurred,while fetching deployment details'}) 
    '''
    env_id = request.GET.get('envid')
    
    resp = m_utils.get_deployment_status(env_id)
    
    #print resp
    
    if resp !=False:
        return JsonResponse({'status': 'success', 'state': str(resp['status'])})   
    else:
        return JsonResponse({'status': 'failed', 'msg': 'Error occurred,while fetching deployment details'}) 
    
'''def test_pkg(request):
    
    m_utils.prepare_mpl_package()        
    
    return HttpResponse("Done")'''

def getPackages(request):
    
    resp = m_utils.get_murano_packages()        
    
    return HttpResponse(resp)
    
@csrf_exempt
def uploadFiles(request):    
    
    #print request.FILES['file']
    f = request.FILES['file']
    
    path = handle_uploaded_file(f)    
    
    return JsonResponse({'status': 'ok','filepath':path})   

def handle_uploaded_file(f):
    print f.name
    extension = f.name.split('.')[-1]
    #filename = f.name +"oho"+ '.' + extension
    #path = properties.filestoreparth + f.name
    path = settings.UPLOAD_FILE_PATH +os.sep+ f.name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
    print path
    return path

def createCustomPackage(request):
    
    '''selected_files = request.GET.get('files')
    selected_files = selected_files.rstrip(',')    
    filelist = selected_files.split(',')   
    #print filelist
    pkg_zip = m_utils.prepare_hot_package(selected_files)
    
    #print filelist
    
    return HttpResponse("Done")'''


    try:      
        selected_files = request.GET.get('files')
        selected_files = selected_files.rstrip(',')    
        filelist = selected_files.split(',')   
        #Create environment
        response_env = m_utils.create_environment()
        if response_env['id']:        
            env_id = response_env['id']     
        else:        
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating environment'})
        
        #Create session
        response_sess = m_utils.create_session(env_id)
        if response_sess['id']:
            session_id = response_sess['id']
        else:
            return JsonResponse({'status': 'failed', 'msg': 'Error occurred while creating session'})  
        
        '''
        print "env_id \n "
        print env_id
        print "session_id \n"  
        print session_id
        '''
        msg = ""
        err_msg = ""
        print filelist        
        
        for package in filelist:     
            
            print package
            package_name = m_utils.prepare_hot_package(package)
            #package_name = settings.MURANO_PACKAGE_NAMES[package]     
            #package_name = pkg_zip     
            repo_url = "" 
            print package_name
            #import package
            app_info = m_utils.import_application_package(repo_url, package_name)  
            print "app_info \n"
            print app_info
            
            if(app_info['response']['id']):             
                #Add application to environment
                respose_app = m_utils.add_application(env_id, session_id, app_info)
                #print "add application result \n"
                #print respose_app            
            else:            
                err_msg += 'Error occurred while importing package '+package+'\n'
        
        
        #app_info = []
        #respose_app = m_utils.add_application(env_id, session_id, app_info)   
        #Deploy session
        response_deploy = m_utils.deploy_session(env_id, session_id)
            
           
        if response_deploy['status_code'] == 200:
            msg +='Package deployment initiated \n'            
        elif response_deploy['status_code'] == 404:
            err_msg += ' Specified session does not exist \n'             
        elif response_deploy['status_code'] == 401:
            err_msg += ' User is not authorized to access this session \n'             
        elif response_deploy['status_code'] == 403:
            err_msg += ' Session is already deployed or deployment is in progress \n'              
        else:
            err_msg += 'Error occurred while deploying  \n'  
                
        if msg == "":     
            return JsonResponse({'status': 'failed', 'msg': 'Submission completed with below messages \n'+err_msg})     
        else:
            return JsonResponse({'status': 'success', 'msg': 'Submission completed with below messages \n'+msg+err_msg,'envid':env_id,'sessid':session_id})
        
    except Exception as e:
        return JsonResponse({'status': 'failed', 'msg': 'Exception occurred while deploying packages'})   
    
    
 
    


    