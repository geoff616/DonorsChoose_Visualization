from flask import Flask, render_template, g, after_this_request, request
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from cStringIO import StringIO as IO
import gzip
import functools 

app = Flask(__name__)

#From: http://flask.pocoo.org/snippets/122/
def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Content-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                print 'no'
                return response
            print 'yes'
            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb', 
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()


            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'donorschoose'
COLLECTION_NAME = 'projects'
FIELDS = {'school_state': True, 'resource_type': True, 'poverty_level': True, 'date_posted': True, 'total_donations': True, '_id': False}



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/donorschoose/projects")
@gzipped
def donorschoose_projects():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    #projects = collection.find({}, FIELDS, limit=1000)
    projects = collection.find({}, FIELDS)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)