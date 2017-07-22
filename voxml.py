# Classe traitant les fichiers et XML et les reponses du service

import os
import xml.dom.minidom as DOM
import xml.etree.ElementTree as ET
# from VoPackage.database import Handler as bdd
# from VoPackage.vospace import Vospace as vo


class Voxml(object):


    attribut_direction = ""
    url_fichier = ""
    vu = ""
    distant = {}
    RACINE = "./VOTest"


    def varAssign(self, node, string, idx):
        global url_fichier, attribut_direction, vu
        index = idx - 1
        if string == "target":
            self.url_fichier = node[index].text
        elif string == "direction":
            self.attribut_direction = node[index].text
        elif string == "view":
            self.vu = node[index].attrib

    def xml_tag_reader(self, root):
        retour = {}
        global distant
        i = 1
        for index, childs in enumerate(root.iter()):
            self.varAssign(root, childs.tag[38:], index)
            for subchild in childs:
                if "endpoint" in subchild.tag:
                    self.distant[subchild.tag[38:] + str(i)] = {"destination": subchild.text}
                    i += 1
            if len(childs.attrib) != 0 and len(childs.tag) != 0:
                tag = childs.tag[38:]
                att = childs.attrib
                retour[tag] = att
        return retour

    def protocol_parser(self, dictionary):
        if "protocol" in dictionary:
            if "ivo://ivoa.net/vospace/core#httpget" in dictionary["protocol"].values():
                return "ivo://ivoa.net/vospace/core#httpget"
            elif "ivo://ivoa.net/vospace/core#httppost" in dictionary["protocol"].values():
                return "ivo://ivoa.net/vospace/core#httppost"
            elif "ivo://ivoa.net/vospace/core#httpput" in dictionary["protocol"].values():
                return "ivo://ivoa.net/vospace/core#httpput"
            elif "ivo://ivoa.net/vospace/core#httpdelete" in dictionary["protocol"].values():
                return "ivo://ivoa.net/vospace/core#httpdelete"



    # Format XML Response
    def xml_formateur(self, element):
        chaine_originale = ET.tostring(element)
        reparsed = DOM.parseString(chaine_originale)
        return reparsed.toprettyxml(indent="    ")

    # Generate XML Response
    def xml_generator(self, action, node):
        PREFIX = "vos:"
        SUFFIX = ":vos"
        VOSNODE = 'vos:node'
        VOSTRANSFER = 'vos:transfer'
        VOSTARGET = 'vos:target'
        VOSDIRECT = 'vos:direction'
        VOSPROT = 'vos:protocol'
        VOSENDPOINT = 'vos:endpoint'
        XMLNS = 'xmnls'
        XMLNSVOS = 'xmlns:vos'
        XMLNSW3C = 'xmlns:xs'
        W3C_URI = "http://www.w3.org/2001/XMLSchema-instance"
        VOSPACE_URI = "http://www.ivoa.net/xml/VOSpace/v2.1"
        CORE_uri = "ivo://ivoa.net/vospace/core#"
        URI_V = "uri"
        # Generate GetProtocols, GetViews or GetProperties XML
        if action in ["protocols", "views", "properties"]:
            temp = node
            top = ET.Element(PREFIX + action)
            top.set(XMLNSVOS, VOSPACE_URI)
            top.set(XMLNSW3C, W3C_URI)

            accept = ET.SubElement(top, PREFIX + "accepts")
            for keys, values in temp["accepts"].items():
                accept_ = ET.SubElement(accept, PREFIX+action[:1])
                accept_.set(URI_V, values)

            provide = ET.SubElement(top, PREFIX  + "provides")
            for keys, values in temp["provides"].items():
                provide_ = ET.SubElement(provide, PREFIX+action[:len(action)-1])
                provide_.set(URI_V, values)

            if action == 'properties':
                contain = ET.SubElement(top, PREFIX + "contains")
                for keys, values in temp["contains"].items():
                    contain_ = ET.SubElement(contain, PREFIX+"property")
                    contain_.set(URI_V, values)

            return self.xml_formateur(top)

        # Generate GetNode XML
        elif action is "get":
            if node:
                temp = node
                top = ET.Element(PREFIX + 'node')
                top.set(XMLNSVOS, VOSPACE_URI)
                top.set(XMLNSW3C, W3C_URI)
                top.set(URI_V, temp['path'])
                for k, v in temp['properties']['type'].items():
                    if k != "readonly":
                        top.set("xs:type", PREFIX + v)
                top.set("Busy", temp['busy'])
                properties = ET.SubElement(top, PREFIX + 'properties')
                if temp['properties']:
                    for keys, values in temp['properties'].items():
                        for k, v in values.items():
                            if keys not in ["ctime", "type"]:
                                if values[k] != '' and k != "readonly":
                                        prop = ET.SubElement(properties, PREFIX + 'property')
                                        prop.set(URI_V, CORE_uri+k)
                                        prop.set("readOnly", values['readonly'])
                                        prop.text = v
                else:
                    prop = ET.SubElement(properties, PREFIX + 'property')
                acceptViews = ET.SubElement(top, PREFIX + 'accept')
                if temp['accepts']:
                    for keys, values in temp['accepts'].items():
                        if values is not '':
                            accept_ = ET.SubElement(acceptViews, PREFIX + 'view')
                            accept_.set(URI_V, values)
                else:
                    accept_ = ET.SubElement(acceptViews, PREFIX + 'view')
                provideViews = ET.SubElement(top, PREFIX + 'provide')
                if temp['provides']:
                    for keys, values in temp['provides'].items():
                        if values is not '':
                            provide_ = ET.SubElement(provideViews, PREFIX + 'view')
                            provide_.set(URI_V, values)
                else:
                    provide_ = ET.SubElement(provideViews, PREFIX + 'view')
                capabilities = ET.SubElement(top, PREFIX + 'capabilities')

                children = ET.SubElement(top, PREFIX + 'nodes')
                for childrens in temp['children']:
                    child = ET.SubElement(children, PREFIX + 'node')
                    child.set(URI_V, childrens['path'])
                    child.set("xs:type", childrens['properties']['type']['type'])
                    child.set("Busy", childrens['busy'])

                    childrenProperties = ET.SubElement(child, PREFIX + 'properties')
                    if childrens['properties']:
                        for keys, values in childrens['properties'].items():
                            for k, v in values.items():
                                if keys not in ["ctime", "type"]:
                                    if values[k] != '' and k != "readonly":
                                            chilProp = ET.SubElement(childrenProperties, PREFIX + 'property')
                                            chilProp.set(URI_V, CORE_uri+k)
                                            chilProp.set("readOnly", values['readonly'])
                                            chilProp.text = v
                    else:
                        chilProp = ET.SubElement(properties, PREFIX + 'property')
                return self.xml_formateur(top)


# class main(object):

    # script, file = argv
    # tree = ET.parse(file)
    # root = tree.getroot()
    # go = Voxml()
    # print(go.xml_generator("protocols"))
    # print(vo().getNode('./VOTest/VOSpace/nodes/myresult1'))
    # print(go.xml_generator('get','myresult1'))
    # print(bdd().getMeta('./VOTest/VOSpace/nodes/myresult1'))