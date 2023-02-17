#coding=utf-8
import jsonpickle
def getSessionInfo(request):
    suser = request.session.get('user','')

    if suser:
        user = jsonpickle.loads(suser)
        return {'user':user}
    return {'user':''}


