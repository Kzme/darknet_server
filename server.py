#!/usr/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import sys
import os


from flask import Flask, request, redirect, jsonify
from werkzeug import secure_filename



sys.path.append(os.path.join(os.getcwd(),'python/'))
import darknet as dn

class Yolo(object):
    def __init__(self, cfgfilepath, weightfilepath, datafilepath, thresh=0.25):
        print(cfgfilepath)
        print(weightfilepath)
        self.net = dn.load_net(cfgfilepath, weightfilepath, 0)
        self.meta = dn.load_meta(datafilepath)
        self.thresh = thresh

    def detect(self, filepath):
        results = dn.detect(self.net, self.meta, filepath, self.thresh)
        print("func is yolo server")
        print(results)
        return results


class MyServer(object):
    def __init__(self, name, host, port, upload_dir, extensions, yolo):
        self.app = Flask(name)
        self.host = host
        self.port = port
        self.app.config['UPLOAD_FOLDER'] = upload_dir
        self.extensions = extensions
        self.yolo = yolo

    def check_allowfile(self, filename):
        if len(filename.split(".")) > 1:
            return filename.split(".")[-1] in self.extensions
        else:
            return False

    def detect(self):
        print("call detect")
        if request.method == 'POST':
            file = request.files['file']
            if file and self.check_allowfile(file.filename):
                print("saving file")
                output_filename = secure_filename(file.filename)
                outputfilepath = os.path.join(self.app.config['UPLOAD_FOLDER'], output_filename)
                file.save(outputfilepath)
                yolo_results = self.yolo.detect(outputfilepath)

                res = dict()
                res['status'] = '200'
                res['result'] = list()
                for yolo_result in yolo_results:
                    result = dict()
                    result['name'] = yolo_result[0]
                    result['score'] = yolo_result[1]
                    res['result'].append(result)

                return jsonify(res)
            else:
                res = dict()
                res['status'] = '500'
                res['msg'] = 'The file format is only jpg or png'
            

    def run(self):
        self.provide_automatic_option = False
        self.app.add_url_rule('/detect', None, self.detect, methods = [ 'POST' ] )
        print("server run")
        self.app.run(host=self.host, port=self.port)



def main():
    cfgfilepath = "./cfg/yolo.cfg"
    datafilepath = "./cfg/coco.data"
    weightfilepath = "./yolo.weights"

    yolo = Yolo(cfgfilepath, weightfilepath, datafilepath)
    server = MyServer('yolo_server', 'localhost', '8080', './upload', [ 'jpg', 'png' ], yolo )
    server.run()


if __name__ == "__main__":
    main()
