import json
import uuid
import sys
import re

from swedish_keys import Swedish_Keys

Structure = ["id", "title", "url", "image_url", "description",
             "description_html", "rating_value", "price", "brand", "currency", "bulleted_text"]
Sub_Structure = ["technical_specification"]
Categories, Types = None, None

global_id = "e5a05170-7f44-45ed-bd49-1b2ced344e81"


def load_SourceData(json_path):

    # load source data json
    cnt = 0
    origin = "./data/result/product"
    with open(json_path, encoding='utf-8') as f:
        for line in f:
            cnt += 1
            fname = origin + "_" + str(cnt) + ".json"
            source_obj = json.loads(line)
            product_obj = parse_line(source_obj)
            with open(fname, 'w', encoding='utf-8') as pro_file:
                # pro_file.write(str(product_obj))
                json.dump(product_obj, pro_file, ensure_ascii=False, indent=2)
            break

            # print(product_obj)


def parse_line(json_obj):
    dic_list = []
    for key, value in json_obj.items():
        # key = key.lower()
        eng_key = swe2eng.translate_SweToEng(key.lower())

        high_level_dic = high_level(eng_key, value, json_obj)

        if high_level_dic is None:
            print(key, value)
            continue
        dic_list.extend(high_level_dic)

    return dic_list


def high_level(key, value, json_object):

    dics = None

    if key == 'id'.lower():
        dics = create_tag("identifier", "id_netonnet", value)
    elif key == "title".lower():
        dics = create_tag("meta", "title", value)
    elif key == "url".lower():
        dics = create_tag("meta", "url", value)

    elif key == "image_url".lower():
        if isinstance(value, list):
            dics = []
            for val in value:
                dics.extend(create_tag("meta", "image", val))
    elif key == "description".lower():
        dics = create_tag("meta", "description", value)
    elif key == "description_html".lower():
        new_value = erase_description_html(value)
        dics = create_tag("meta", "description_html", new_value)

    elif key == "Category".lower():
        if isinstance(value, dict):
            str = None
            for sub_key, sub_value in value.items():

                if sub_value.lower().find("desktop") != -1:
                    str = "desktop"
                    break
                elif sub_value.lower().find("laptop") != -1:
                    str = "laptop"
                    break
            if str is not None:
                dics = create_tag("category", "tag", str, create_tag("parent", "tag", global_id))

    elif key == "bulleted_text".lower():
        dics = create_tag("meta", "description", value)

    elif key == "price".lower():
        if "currency" in json_object.keys():
            sub_value = json_object["currency"]
            dics = create_tag("price", "original", value, create_tag("unit", "currency", sub_value))
        else:
            pass

    elif key == "brand".lower():
        dics = create_tag("identifier", "brand", value)

    elif key == "technical_specifications".lower():
        dics = []
        for spec_key, spec_obj in value.items():
            spec_key = swe2eng.translate_SweToEng(spec_key.lower())
            dics.extend(tech_specs(spec_key, spec_obj))
    return dics


def erase_description_html(string):
    # remove the stranger charactor
    string.replace('\"', '')
    string.replace('\t', '')
    string.replace('\n', '')
    string.replace('\r', '')

    pos = 0
    # remove ahref="https:/
    while True:
        start = string.find('a href="http', pos)
        end = string.find('"', start + 8)
        if start != -1 and end != -1:
            url = string[start+6:end]
            string = string.replace(url, "")
            pos = start
        else:
            break

    # remove the src="https:\..."
    pos = 0
    while True:
        start = string.find('src="http', pos)
        end = string.find('"', start + 6)
        if start != -1 and end != -1:
            url = string[start+5:end]
            string = string.replace(url, "")
            pos = start
        else:
            break
    return string


def tech_specs(key, value):
    dics = None

    if key == "Storage".lower():
        dics = _storage(value)
    elif key == "Memory".lower():
        dics = _memory(value)
    elif key == "Connenctions".lower():
        dics = _connections(value)
    elif key == "Chassis".lower():
        dics = _chassis(value)
    elif key == "Support and Warranty".lower():
        dics = _support_warranty(value)
    elif key == "Communication".lower():
        dics = _communication(value)
    elif key == "Processor".lower():
        dics = _processor(value)
    elif key == "Graphics and Audio".lower() or "Graphics and Sounds":
        dics = _graphs_audio(value)
    elif key == "General".lower():
        dics = _general(value)

    return dics


def _storage(value):
    if isinstance(value, dict):
        dics = []
        sub_dics = create_tag("identifier", "kind", "storage")
        dics.extend(sub_dics)

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "primary hard drive size".lower():
                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "storage", unit))
                dics.extend(sub_dics)

            elif sub_key == "primary hard drive type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

        subpart_dic = create_tag("subpart", "commponent", None, dics)
        usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
        return [subpart_dic, usp_dic]


def _memory(value):
    if isinstance(value, dict):
        dics = []
        sub_dics = create_tag("identifier", "kind", "working_memory")
        dics.extend(sub_dics)
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "memory Include".lower():

                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "storage", unit))
                dics.extend(sub_dics)

            elif sub_key == "memory type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

            elif sub_key == "memory speed".lower():
                qua_unit = sub_value.split(" ")
                quantity, unit = qua_unit[0], qua_unit[-1]
                if len(qua_unit) != 2:
                    break
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "frequency", unit))
                dics.extend(sub_dics)

        subpart_dic = create_tag("subpart", "commponent", None, dics)
        usp_dic = create_tag("usp", "id",  subpart_dic[0]["id"], None)
        subpart_dic.extend(usp_dic)
        return subpart_dic


def _connections(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "HDMI".lower():
                sub_dics = create_tag("connection", "type", "hdmi", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

            elif sub_key == "RJ45".lower():
                sub_dics = create_tag("connection", "type", "rj45", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

            elif sub_key == "usb 30 port".lower():
                sub_dics = create_tag("connection", "type", "usb30", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

            elif sub_key == "thunderbolt".lower():
                sub_dics = create_tag("connection", "type", "thunderbolt", create_tag("size", "quantity", sub_value))
                dics.extend(sub_dics)

        return dics


def _chassis(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "Height".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    break

                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "height", quantity, create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            elif sub_key == "RJ45".lower():
                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "width", quantity, create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

        return dics


def _support_warranty(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "Support Number".lower():
                sub_dics = create_tag("meta", "number", sub_value)
                dics.extend(sub_dics)

            elif sub_key == "Warranty Hardware".lower():
                qua_unit = sub_value.split(" ")

                if len(qua_unit) != 2:
                    break
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "time", unit))
                dics.extend(sub_dics)

        feature_dic = create_tag("feature", "warranty", "hardware", dics)
        return feature_dic


def _communication(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_val in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "Wireless Network".lower():
                sub_dics = create_tag("technology", "technology", sub_val)
                super_dic = create_tag("communication", "type", "wifi", sub_dics)
                dics.extend(super_dic)

            if sub_key == "Fixed Network".lower():
                qua_unit = sub_val.split(" ")
                quantity = qua_unit[0][:qua_unit[0].find('bit/s')-1]

                sub_dics = create_tag("size", "quantity", quantity, create_tag("unit", "speed", "Mbit/s"))
                super_dic = create_tag("communication", "type", "wifi", sub_dics)
                dics.extend(super_dic)
        return dics


def _processor(value):

    dics = []
    sub_dics = create_tag("identifier", "kind", "cpu")
    dics.extend(sub_dics)
    for sub_key, sub_value in value.items():
        sub_key = swe2eng.translate_SweToEng(sub_key.lower())

        if sub_key == "Manufacturer".lower():
            sub_dic = create_tag("identifier", "brand", sub_value)
            dics.extend(sub_dic)

        if sub_key == "Model".lower():
            sub_dic = create_tag("identifier", "model", sub_value)
            dics.extend(sub_dic)

        if sub_key == "Processor Series".lower():
            sub_dic = create_tag("identifier", "series", sub_value)
            dics.extend(sub_dic)

        if sub_key == "Bass Speed".lower():
            [quantity, unit] = sub_value.split(" ")
            unit = swe2eng.translate_SweToEng(unit)
            tags = [create_tag("unit", "frequency", unit), create_tag("identifier", "version", "base")]
            sub_dics = create_tag("size", "quantity", quantity, tags)
            dics.extend(sub_dics)

        if sub_key == "Max Turbo".lower():
            qua_unit = sub_value.split(" ")

            if len(qua_unit) != 2:
                break
            quantity, unit = qua_unit[0], qua_unit[-1]
            unit = swe2eng.translate_SweToEng(unit)

            tags = [create_tag("unit", "frequency", unit), create_tag("identifier", "version", "boost")]
            sub_dics = create_tag("size", "quantity", quantity, tags)
            dics.extend(sub_dics)

        elif sub_key == "Number of Kernels".lower():
            [quantity, unit] = sub_value.split(" ")
            sub_dic = create_tag("hardward", "cores", quantity)
            dics.extend(sub_dic)

    subpart_dic = create_tag("subpart", "commponent", None, dics)
    usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
    subpart_dic.extend(usp_dic)
    return subpart_dic


def _graphs_audio(value):

    dics = []
    sub_dics = create_tag("identifier", "kind", "working_memory")
    dics.extend(sub_dics)

    for sub_key, sub_value in value.items():
        sub_key = swe2eng.translate_SweToEng(sub_key.lower())

        if sub_key == "Dedicated graphics memory".lower():
            qua_unit = sub_value.split(" ")
            if len(qua_unit) != 2:
                break
            quantity, unit = qua_unit[0], qua_unit[-1]
            unit = swe2eng.translate_SweToEng(unit)

            sub_dic = create_tag("size", "quantity", quantity, create_tag("unit", "storage", unit))
            dics.extend(sub_dic)

        if sub_key == "Graphics Card".lower():
            sub_dic = create_tag("identifier", "name", sub_value)
            dics.extend(sub_dic)
            if sub_value.find("AMD") != -1:
                sub_dic = create_tag("identifier", "brand", "AMD")
                dics.extend(sub_dic)

    subpart_dic = create_tag("subpart", "commponent", None, dics)
    usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
    subpart_dic.extend(usp_dic)
    return subpart_dic


def _general(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_val in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key == "Add Ard No.".lower():
                sub_dics = create_tag("identifier", "id_creator", sub_val)
                dics.extend(sub_dics)

            if sub_key == "Operating System".lower():
                sub_dics = create_tag("software", "os", sub_val)
                dics.extend(sub_dics)

        return dics


def create_tag(category, type, value=None, tags=None):
    tag = {
        "id": str(uuid.uuid4()),
        "category": category,
        "type": type,
    }
    if value is not None:
        tag["value"] = value
    if tags is not None:
        tag["tags"] = tags
    return [tag]

if __name__ == '__main__':

    """-------------------------Create the dictionary object---------------"""
    swe2eng = Swedish_Keys()

    """-------------------------Main Progress -----------------------------"""
    source_fname = "./data/sourcedata (1).json"

    global_id = "e5a05170-7f44-45ed-bd49-1b2ced344e81"
    load_SourceData(source_fname)

