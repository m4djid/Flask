from flask import Flask, Response
from voxml import Voxml
from flask_pymongo import PyMongo
from flask_restplus import Api, Resource
from copy import deepcopy
import os

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'vospace'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/vospace'
mongo = PyMongo(app)
api = Api(app)


def getnode(target, parent, ancestor):
    try:
        if ancestor == ['']:
            _ancestor = []
        else:
            _ancestor = ancestor
        node = mongo.db.VOSpaceFiles.find({'node': target, 'parent': parent, 'ancestor': _ancestor})
        temp = {}

        for document in node:
            for keys, values in document.items():
                temp[keys] = values
        representation = {
            'children': [],
            'properties': {},
            'accepts': {},
            'provides': {},
            'busy': '',
        }
        cursor = mongo.db.VOSpaceFiles.find({"parent": target}, {"path": 1, "busy": 1, "properties": 1, "_id": 0})
        if cursor:
            for items in cursor:
                representation['children'].append(items)
        representation['busy'] = temp['busy']
        representation['path'] = deepcopy(temp['path'])
        representation['properties'] = deepcopy(temp['properties'])
        representation['accepts'] = deepcopy(temp['accepts'])
        representation['provides'] = deepcopy(temp['provides'])

        return Voxml().xml_generator('get', representation)
    except Exception as e:
        return "Error : %s" % e


def args(path):
    return ['myresult1', 'nodes', []]


@api.route('/nodes/<string:path>')
@api.doc(params={'path': 'A path'})
class MyResource(Resource):
    def get(self, path):
        _ = args(path)
        node = getnode(_[0], _[1], _[2])
        return Response(node, mimetype='text/xml')



if __name__ == '__main__':
    app.run(debug=True)
