#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
from threading import Thread
import json

SERVER_IP = "10.0.2.15"
SERVER_PORT = 8080
DEFAULT_PATH = "/template/manage.html"

class ParseUrls:
    '''
    descrption: 解析url
    example: /post/add?host=843&uid=20345#addPost
    __dict__ : {
        path: /post/add?host=843&uid=20345#addPost,
        pathInfo: /post/add,
        pathAry: [post, add],
        filename: "", // static file use, likes png html css...
        queryString: host=843&uid=20345,
        queryMap: {host: 843, uid: 20345},
        hashString: addPost,
    }
    '''

    def __init__(self, path):
        self.path = path;
        
        # parse pathInfo, queryString, hashString
        i1 = path.find("?")
        i2 = path.find("#")
        if i1 < 0 and i2 < 0:
            self.pathInfo = path
            self.queryString = ""
            self.hashString = ""
        elif i1 >= 0 and (i2 > i1 or i2 < 0):
            self.pathInfo = path[0:i1]
            if i2 >= 0:
                self.queryString = path[(i1 + 1): i2]
                self.hashString = path[i2:]
            else:
                self.queryString = path[(i1 + 1):]
                self.hashString = ""
        elif i2 >= 0 and (i1 > i2 or i1 < 0):
            self.pathInfo = path[0:i2]
            if i1 >= 0:
                self.hashString = path[(i2 + 1): i1]
                self.queryString = path[i1:]
            else:
                self.hashString = path[(i2 + 1):]
                self.queryString = ""
        else:
            print "Error Search Path",path,i1,i2

        # parse pathAry
        tmpStr = self.pathInfo.strip("/")
        self.pathAry = tmpStr.split("/")

        # parse filename
        tmpStr = self.pathAry[-1]
        i3 = tmpStr.find(".")
        self.filename = tmpStr[(i3 + 1):]

        # parse queryMap
        tmpStr = self.queryString.strip("&")
        self.queryMap = {}
        if (len(tmpStr)):
            tmpAry = tmpStr.split("&")
            for each in tmpAry:
                i4 = each.find("=")
                k = each[0:i4]
                v = each[(i4 + 1):]
                self.queryMap[k] = v
        return

class Autoload():
    '''
    descrption: 动态加载模块，字符串方法调用
    example:
        loader = Autonload('util.common',['*'])
        obj = loader.getobject()
        loader.execfunc(obj, 'test')
        ins = loader.getClassInstance(obj, 'CatClass')
        loader.execMethod(ins, 'test')
    '''
    def __init__(self, package, imp_list):
        
        self.package = package
        self.imp = imp_list
        
    def getobject(self):
        try:
            return __import__(self.package, globals(), locals(), self.imp, -1)
        except ImportError:
            print "ImportError: No module named {m}".format(
                    m = self.package)
            return -1

    def execfunc(self, obj, method, *args):
        try:
            return getattr(obj, method)(*args)
        except AttributeError:
            print "AttributeError: {obj} has no func {m}".format(
                    obj = obj.__module__, m = method)
            return -2
 
    def getClassInstance(self, obj, classstr, *args):
        try: 
            return getattr(obj, classstr)(*args)
        except AttributeError:
            print "AttributeError: {obj} has no class {m}".format(
                    obj = obj, m = classstr) 
            return -3
    
   
    def execMethod(self, instance, method, *args):
        try:
            return getattr(instance, method)(*args)
        except AttributeError:
            print "AttributeError: {instance} has no method {m}".format(
                    instance = instance, m = method)
            return -4


class Handler(BaseHTTPRequestHandler):
    '''
    descrption: 处理请求分发
    '''
    def do_GET(self):
        if self.path == "/":
            self.path = DEFAULT_PATH

        try:
            urlInfo = ParseUrls(self.path)
            
            file2Type = {
                "html"  : "text/html",
                "jpg"   : "image/jpg",
                "png"   : "image/png",
                "gif"   : "image/gif",
                "ico"   : "image/x-icon",
                "js"    : "application/javascript",
                "css"   : "text/css",
                "woff"  : "application/x-font-woff",
                "woff2" : "application/x-font-woff",
            }

            mimetype=file2Type.get(urlInfo.filename, "text/html");

            f = open(curdir + sep + urlInfo.pathInfo)
            self.send_response(200)
            self.send_header('Content-type',mimetype)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):
        
        # get requst info 
        urlInfo = ParseUrls(self.path)
        postData = self.rfile.read(int(self.headers['content-length']))

        # log request 
        self.log_message("\n----header----\n%s\n----postData----\n%s\n", self.headers, postData);
 
        ret = {};
        if (len(urlInfo.pathAry) >= 2):
            
            tmpStr = urlInfo.pathAry[0]
            controller = "{c}Controller".format(c = tmpStr.capitalize());
            imp = "modules.{c}_controller".format(c = tmpStr.lower());

            tmpStr = urlInfo.pathAry[1]
            action = "action{a}".format(a = tmpStr.capitalize()); 
            
            loader = Autoload(imp, ["*"]);
            obj = loader.getobject()
            if obj == -1:
                ret = {"ret": -1, "msg": "not found controller"}
            else:
                ins = loader.getClassInstance(obj, controller, urlInfo, postData);
                if ins == -3:
                    ret = {"ret": -3, "msg": "not found class"}
                else:
                    ret = loader.execMethod(ins, action)
                    if ret == -4:
                        ret = {"ret": -4, "msg": "not found action"}

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(ret))
        return


class ThreadedHTTPServer(HTTPServer):
    '''
    Description: 多线程服务器
    '''
    def process_request(self, request, client_address):
            thread = Thread(target=self.__new_request, args=(self.RequestHandlerClass, request, client_address, self))
            thread.start()

    def __new_request(self, handlerClass, request, address, server):
            handlerClass(request, address, server)
            self.shutdown_request(request)

def main():
    try:
        #Create a web server and define the handler to manage the
        #incoming request
        #server = HTTPServer((SERVER_IP, SERVER_PORT), myHandler)
        server = ThreadedHTTPServer((SERVER_IP, SERVER_PORT), Handler)
        print 'Started httpserver on port ' , SERVER_PORT

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()

if __name__ == '__main__':
      main()
