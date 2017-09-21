import json
import uuid
import sys
import re
import html
from swedish_keys import Swedish_Keys

Structure = ["id", "title", "url", "image_url", "description",
             "description_html", "rating_value", "price", "brand", "currency", "bulleted_text"]
Sub_Structure = ["technical_specification"]
Categories, Types = None, None


def load_SourceData(json_path):

    # load source data json
    cnt = 0
    origin = "./data/result/product"
    with open(json_path, encoding='utf-8') as f:
        for line in f:
            cnt += 1
            sys.stdout.write("=================line number : {}\n".format(cnt))
            if cnt != 3:
                continue

            fname = origin + "_" + str(cnt) + ".json"
            source_obj = json.loads(line)
            product_obj = parse_line(source_obj)
            with open(fname, 'w', encoding='utf-8') as pro_file:
                # pro_file.write(str(product_obj))
                json.dump(product_obj, pro_file, ensure_ascii=False, indent=2)

            sys.stdout.flush()
    print(len(swe2eng.unused_swe_keys), len(swe2eng.unused_eng_keys))
    for i in range(len(swe2eng.unused_swe_keys)):
        print(swe2eng.unused_swe_keys[i], "\t", swe2eng.unused_eng_keys[i])


def num(s):
    try:
        return int(s)
    except ValueError:
        if s.find(",") != -1:
            s = s.replace(",", ".")
            try:
                return float(s)
            except ValueError:
                print("=============", s)
        else:
            print("=============", s)


def parse_line(json_obj):
    dic_list = []
    for key, value in json_obj.items():
        # key = key.lower()
        eng_key = swe2eng.translate_SweToEng(key.lower())

        high_level_dic = high_level(eng_key, value, json_obj)

        if high_level_dic is None:
            # print(key, value)
            continue

        dic_list.extend(high_level_dic)

    return dic_list


def high_level(key, value, json_object):

    dics = None

    if key.lower() == 'id'.lower():
        dics = create_tag("identifier", "id_netonnet", value)
    elif key.lower() == "title".lower():
        dics = create_tag("meta", "title", value)
    elif key.lower() == "url".lower():
        dics = create_tag("meta", "url", value)

    elif key.lower() == "image_url".lower():
        if isinstance(value, list):
            dics = []
            for val in value:
                dics.extend(create_tag("meta", "image", val))

    elif key.lower() == "description_html".lower():
        new_value = erase_description_html(value)
        dics = create_tag("meta", "description", new_value)

    elif key.lower() == "Category".lower():
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
                dics.extend(create_tag("identifier", "kind", str))
                # dics.extend(create_tag("identifier", "customer_id", global_customer_id))
                # dics.extend(create_tag("identifier", "name", global_product_name))

    # elif key.lower() == "bulleted_text".lower():
    #     dics = create_tag("meta", "description", value)

    elif key.lower() == "price".lower():
        if "currency" in json_object.keys():
            sub_value = json_object["currency"]
            dics = create_tag("price", "original", value, create_tag("unit", "currency", sub_value))
        else:
            pass

    elif key.lower() == "brand".lower():
        dics = create_tag("identifier", "brand", value)

    elif key.lower() == "technical_specifications".lower():
        dics = []
        for spec_key, spec_obj in value.items():
            spec_key = swe2eng.translate_SweToEng(spec_key.lower())

            print(spec_key)

            dic = tech_specs(spec_key, spec_obj)
            if dic is not None:
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
            string = string.replace('"' + url + '"', "''")
            pos = start
        else:
            break

    string = string.replace('\"', '\'')
    string = string.replace('\"', '')
    string = string.replace('\t', '')
    string = string.replace('\n', '')
    string = string.replace('\r', '')
    return string


def tech_specs(key, value):
    dics = None

    if key.lower() == "Storage".lower():
        dics = _storage(value)
    elif key.lower() == "Memory".lower():
        dics = _memory(value)
    elif key.lower() == "Connections".lower():
        dics = _connections(value)
    elif key.lower() == "Chassis".lower():
        dics = _chassis(value)
    elif key.lower() == "Support and Warranty".lower():
        dics = _support_warranty(value)
    elif key.lower() == "Communication".lower():
        dics = _communication(value)
    elif key.lower() == "Processor".lower():
        dics = _processor(value)
    elif key.lower() == "Graphics and Audio".lower() or key.lower() == "Graphics and Sounds".lower():
        dics = _graphs_audio(value)
    elif key.lower() == "Generally".lower():
        dics = _general(value)

    return dics


def _storage(value):
    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "primary hard drive size".lower():
                if len(sub_value.split(" ")) != 2:
                    break
                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
                dics.extend(sub_dics)

            elif sub_key.lower() == "primary hard drive type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "storage")
            dics.extend(sub_dics)
            subpart_dic = create_tag("subpart", "component", None, dics)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic

        else:
            return dics


def _memory(value):
    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "memory Included".lower():

                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
                dics.extend(sub_dics)

            elif sub_key.lower() == "memory type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

            elif sub_key.lower() == "memory speed".lower():
                qua_unit = sub_value.split(" ")
                quantity, unit = qua_unit[0], qua_unit[-1]
                if len(qua_unit) != 2:
                    break
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "frequency", unit))
                dics.extend(sub_dics)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "working_memory")
            dics.extend(sub_dics)
            subpart_dic = create_tag("subpart", "component", None, dics)
            usp_dic = create_tag("usp", "id",  subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic
        else:
            return dics


def _connections(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            qua_unit = sub_value.split(" ")
            if len(qua_unit) != 2:
                continue
            quantity = num(qua_unit[0])

            if sub_key.lower() == "HDMI".lower():
                sub_dics = create_tag("connection", "type", "hdmi", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "RJ45".lower():
                sub_dics = create_tag("connection", "type", "rj45", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "usb 30 ports".lower():
                sub_dics = create_tag("connection", "type", "usb30", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "usb 20 ports".lower():
                sub_dics = create_tag("connection", "type", "usb20", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "thunderbolt".lower():
                sub_dics = create_tag("connection", "type", "thunderbolt", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

        return dics


def _chassis(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "Height".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    break
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "height", num(quantity), create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            elif sub_key.lower() == "Width".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    break
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)
                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "width", num(quantity), create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

        return dics


def _support_warranty(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "Support Number".lower():
                sub_dics = create_tag("meta", "number", sub_value)
                dics.extend(sub_dics)

            elif sub_key.lower() == "Warranty Hardware".lower():
                qua_unit = sub_value.split(" ")

                if len(qua_unit) != 2:
                    break
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "time", unit))
                dics.extend(sub_dics)

        feature_dic = create_tag("feature", "warranty", "hardware", dics)
        return feature_dic


def _communication(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_val in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "Wireless Network".lower():
                sub_dics = create_tag("technology", "technology", sub_val)
                super_dic = create_tag("communication", "type", "wifi", sub_dics)
                dics.extend(super_dic)

            if sub_key.lower() == "Fixed Network".lower():
                qua_unit = sub_val.split(" ")
                quantity = qua_unit[0][:qua_unit[0].find('bit/s')-1]

                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "speed", "Mbit/s"))
                super_dic = create_tag("communication", "type", "ethernet", sub_dics)
                dics.extend(super_dic)
        return dics


def _processor(value):
    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "Manufacturer".lower():
                sub_dic = create_tag("identifier", "brand", sub_value)
                dics.extend(sub_dic)

            if sub_key.lower() == "Model".lower():
                sub_dic = create_tag("identifier", "model", sub_value)
                dics.extend(sub_dic)

            if sub_key.lower() == "Processor Series".lower():
                sub_dic = create_tag("identifier", "series", sub_value)
                dics.extend(sub_dic)

            if sub_key.lower() == "Base Speed".lower() or sub_key.lower() == "Bass Speed".lower():
                if len(sub_value.split(" ")) == 2:
                    [quantity, unit] = sub_value.split(" ")
                    unit = swe2eng.translate_SweToEng(unit)
                    tags = []
                    tags.extend(create_tag("unit", "frequency", unit))
                    tags.extend(create_tag("identifier", "version", "base"))
                    sub_dics = create_tag("size", "quantity", num(quantity), tags)
                    dics.extend(sub_dics)

            if sub_key.lower() == "Max Turbo".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    break
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)
                tags = []
                tags.extend(create_tag("unit", "frequency", unit))
                tags.extend(create_tag("identifier", "version", "boost"))
                sub_dics = create_tag("size", "quantity", num(quantity), tags)
                dics.extend(sub_dics)

            elif sub_key.lower() == "Number of Kernels".lower() or sub_key.lower() == "Number of Cores".lower():
                if len(sub_value.split(" ")) == 2:
                    [quantity, unit] = sub_value.split(" ")
                    sub_dic = create_tag("hardware", "cores", num(quantity))
                    dics.extend(sub_dic)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "cpu")
            dics.extend(sub_dics)
            subpart_dic = create_tag("subpart", "component", None, dics)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic
        else:
            return dics


def _graphs_audio(value):

    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "Dedicated graphics memory".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    break
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                sub_dic = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
                dics.extend(sub_dic)

            if sub_key.lower() == "Graphics Card".lower() or sub_key.lower() == "Video Card".lower():
                sub_dic = create_tag("identifier", "name", sub_value)
                dics.extend(sub_dic)
                if sub_value.find("AMD") != -1:
                    sub_dic = create_tag("identifier", "brand", "AMD")
                    dics.extend(sub_dic)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "working_memory")
            dics.extend(sub_dics)

            sub_subpart_dic_1 = create_tag("identifier", "kind", "gpu")
            sub_subpart_dic_2 = create_tag("subpart", "component", None, dics)
            sub_subpart_dic_1.extend(sub_subpart_dic_2)

            subpart_dic = create_tag("subpart", "component", None, sub_subpart_dic_1)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic
        else:
            return dics


def _general(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_val in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "also available in Art".lower():
                sub_dics = create_tag("identifier", "id_creator", sub_val)
                dics.extend(sub_dics)

            if sub_key.lower() == "Operating System".lower() or sub_key.lower() == "OS".lower():
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
    global_customer_id = 8
    global_product_name = "Mac Pro"
    load_SourceData(source_fname)

