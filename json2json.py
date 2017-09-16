import json
import uuid
import sys
import re

from swedish_keys import Swedish_Keys
from labels import Label

Structure = ["id", "title", "url", "image_url", "description",
             "description_html", "rating_value", "price", "brand", "currency", "bulleted_text"]
Sub_Structure = ["technical_specification"]
Categories, Types = None, None


def load_SourceData(json_path):

    # load source data json
    data = []
    with open(json_path, encoding='utf-8') as f:
        for line in f:

            source_obj = json.loads(line)
            product_obj = parse_source_obj(source_obj)

            print(product_obj)
            # data.append(product_obj)
            break


def parse_source_obj(json_obj):
    dic_list = []
    for key, value in json_obj.items():
        key = key.lower()

        eng_key = swe2eng.translate_SweToEng(key)

        dic = parse_tag(eng_key, value)

    return dic_list


def parse_tag(key, value):
    if key is 'id':
        dics = create_tag("identifier", "id_netonnet", value)
    elif key is "title":
        dics = create_tag("meta", "title", value)
    elif key is "url":
        dics = create_tag("meta", "url", value)

    elif key is "image_url":
        if isinstance(value, list):
            dics = []
            for val in value:
                dics.extend(create_tag("meta", "image", val))
    elif key is "description":
        dics = create_tag("meta", "description", value)
    elif key is "description_html":
        dics = create_tag("meta", "description_html", value)

    elif key is "rating_value":
        dics = create_tag("meta", "rating_value", value)
    elif key is "bulleted_text":
        dics = create_tag("meta", "description", value)

    elif key is "price":
        dics = create_tag("price", "original", value)
    elif key is "currency":
        dics = create_tag("unit", "currency", value)
    elif key is "brand":
        dics = create_tag("identifier", "brand", value)

    elif key is "technical_specification":
        for key, value in spec_obj.items():
            dics = tech_specs(key, value)

    return dics


def tech_specs(key, value):

    if key is "storage":
        dics = _storage(key, value)
    elif key is "memory":
        dics = _memory(key, value)
    elif key is "connenctions":
        dics = _connections(key, value)
    elif key is "chassis":
        dics = _connections(key, value)


def _storage(key, value):
    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_dics = create_tag("identifier", "kind", "storage")
            dics.extend(sub_dics)

            if sub_key is "primary hard drive size".lower():
                [quantity, unit] = sub_value.split(" ")
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "storage", unit))
                dics.extend(sub_dics)

            elif sub_key is "primary hard drive type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

        subpart_dic = create_tag("subpart", "commponent", dics)
        usp_dic = create_tag("usp", "id", None, subpart_dic["id"])
        return [subpart_dic, usp_dic]


def _memory(key, value):
    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():

            sub_dics = create_tag("identifier", "kind", "working_memory")
            dics.extend(sub_dics)

            if sub_key is "memory Include".lower():

                [quantity, unit] = sub_value.split(" ")
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "storage", unit))
                dics.extend(sub_dics)

            elif sub_key is "memory type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

            elif sub_key is "memory speed".lower():
                [quantity, unit] = sub_value.split(" ")
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "frequency", unit))
                dics.extend(sub_dics)

        subpart_dic = create_tag("subpart", "commponent", dics)
        usp_dic = create_tag("usp", "id", None, subpart_dic["id"])
        return [subpart_dic, usp_dic]


def _connections(key, value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():

            # sub_dics = create_tag("identifier", "kind", "working_memory")
            # dics.extend(sub_dics)

            if sub_key is "HDMI".lower():
                sub_dics = create_tag("connection", "type", "hdmi", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

            elif sub_key is "RJ45".lower():
                sub_dics = create_tag("connection", "type", "rj45", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

            elif sub_key is "usb 30 port".lower():
                sub_dics = create_tag("connection", "type", "usb30", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

            elif sub_key is "thunderbolt".lower():
                sub_dics = create_tag("connection", "type", "thunderbolt", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

        return dics


def _chassis(key, value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():

            if sub_key is "Height".lower():
                [quantity, unit] = sub_value.split(" ")
                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "height", quantity, create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            elif sub_key is "RJ45".lower():
                [quantity, unit] = sub_value.split(" ")
                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "width", quantity, create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

        return dics


def _support_warranty(key, value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():

            if sub_key is "Support Number".lower():
                sub_dics = create_tag("meta", "number", sub_value)
                dics.extend(sub_dics)

            elif sub_key is "Warranty Hardware".lower():
                [quantity, unit] = sub_value.split(" ")
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "time", unit))
                dics.extend(sub_dics)

        feature_dic = create_tag("feature", "warranty", "hardware", dics)
        return feature_dic


def _communication(key, value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_val in value.items():

            if sub_key is "Wireless Network".lower():
                sub_dics = create(create_tag("technology", "technology", sub_val))
                super_dic = create(create_tag("communication", "type", "wifi", sub_dics))
                dics.extend(super_dic)

            if sub_key is "Fixed Network".lower():
                [qua_unit, _] = sub_val.split(" ")
                quantity = re.findall(qua_unit)[0]

                sub_dics = create(create_tag("size", "quantity", quantity, create_tag("unit", "speed", "Mbit/s")))
                super_dic = create(create_tag("communication", "type", "wifi", sub_dics))
                dics.extend(super_dic)

            return dics


def _processor(key, value):

    dics = []
    for sub_key, sub_value in value.items():

        sub_dics = create_tag("identifier", "kind", "cpu")
        dics.extend(sub_dics)

        if sub_key is "Manufacturer".lower():
            sub_dic = create_tag("identifier", "brand", sub_value)
            dics.extend(sub_dic)

        if sub_key is "Model".lower():
            sub_dic = create_tag("identifier", "model", sub_value)
            dics.extend(sub_dic)

        if sub_key is "Processor Series".lower():
            sub_dic = create_tag("identifier", "series", sub_value)
            dics.extend(sub_dic)

        if sub_key is "Bass Speed".lower():
            [quantity, unit] = sub_value.split(" ")
            tags = [create_tag("unit", "frequency", unit), create_tag("identifier", "version", "base")]
            sub_dics = create_tag("size", "quantity", quantity, tags)
            dics.extend(sub_dics)

        if sub_key is "Max Turbo".lower():
            [quantity, unit] = sub_value.split(" ")
            tags = [create_tag("unit", "frequency", unit), create_tag("identifier", "version", "boost")]
            sub_dics = create_tag("size", "quantity", quantity, tags)
            dics.extend(sub_dics)

        elif sub_key is "Number of Kernels".lower():
            [quantity, unit] = sub_value.split(" ")
            sub_dic = create_tag("hardward", "cores", quantity)
            dics.extend(sub_dic)

    subpart_dic = create_tag("subpart", "commponent", dics)
    usp_dic = create_tag("usp", "id", None, subpart_dic["id"])
    return [subpart_dic, usp_dic]


def create_tag(category, type, value=None, tags=None):
    tag = {
        "id": uuid.uuid4(),
        "category": category,
        "type": type,
    }
    if value is not None:
        tag["value"] = value
    if tags is not None:
        tag["tags"] = tags
    return [tag]

if __name__ == '__main__':

    """-------------------------Loading the Label data---------------------"""
    label = Label()

    """-------------------------Create the dictionary object---------------"""
    swe2eng = Swedish_Keys()

    """-------------------------Main Progress -----------------------------"""
    source_fname = "./data/sourcedata (1).json"
    load_SourceData(source_fname)

