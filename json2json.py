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

uncatched_keys = []


def load_uncatched_keys(txt_path):
    with open(txt_path, encoding='utf-8') as f:
        for line in f:
            key = line[:-1]
            uncatched_keys.append(key)
        # print(len(uncatched_keys))


def load_SourceData(json_path):

    # load source data json
    cnt = 0
    origin = "./data/result/product"
    with open(json_path, encoding='utf-8') as f:
        for line in f:
            cnt += 1

            if cnt != 157:
                continue

            # sys.stdout.write("=== line number : {}\n".format(cnt))

            fname = origin + "_" + str(cnt) + ".json"
            source_obj = json.loads(line)
            product_obj = parse_line(source_obj)
            with open(fname, 'w', encoding='utf-8') as pro_file:
                json.dump(product_obj, pro_file, ensure_ascii=False, indent=2)

            sys.stdout.flush()


def num(s):
    try:
        return int(s)
    except ValueError:
        if s.find(",") != -1:
            s = s.replace(",", ".")
            try:
                return float(s)
            except ValueError:
                pass  # print("---", s)

        elif s.find("0/") != -1:
            return s
        else:
            return s
            # pass  # print("---", s)


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
                # elif sub_value.lower().find("laptop") != -1:
                #     str = "laptop"
                #     break
            if str is not None:
                dics = create_tag("category", "tag", str, create_tag("parent", "tag", global_id))
                dics.extend(create_tag("identifier", "kind", str))
                # dics.extend(create_tag("identifier", "customer_id", global_customer_id))
                # dics.extend(create_tag("identifier", "name", global_product_name))

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
            key = swe2eng.translate_SweToEng(spec_key.lower())
            spec_value = spec_obj
            # print("=", key)

            dic = None
            top_dic = None

            if key.lower() == "Storage".lower():
                dic, top_dic = _storage(spec_value)

            elif key.lower() == "Memory".lower():
                dic = _memory(spec_value)

            elif key.lower() == "Connections".lower():
                dic = _connections(spec_value)

            elif key.lower() == "Chassis".lower():
                dic = _chassis(spec_value)

            elif key.lower() == "Support and Warranty".lower():
                dic = _support_warranty(spec_value)

            elif key.lower() == "Communication".lower():
                dic = _communication(spec_value)

            elif key.lower() == "Processor".lower():
                dic = _processor(spec_value)

            elif key.lower() == "Graphics and Audio".lower() or key.lower() == "Graphics and Sounds".lower():
                dic = _graphs_audio(spec_value)

            elif key.lower() == "Generally".lower():
                dic = _general(spec_value)

            elif key.lower() == "battery".lower():
                dic = _battery(spec_value)

            elif key.lower() == "Special Features".lower():
                dic = _spec_feature(spec_value)

            elif key.lower() == "screen".lower():
                dic = _screen(spec_value)
                if len(dic) != 0:
                    # for laptop tag
                    laptop_dic = create_tag("category", "tag", "laptop", create_tag("parent", "tag", global_id))
                    laptop_dic.extend(create_tag("identifier", "kind", "laptop"))
                    dic.extend(laptop_dic)

            if dic is not None:
                dics.extend(dic)

            if top_dic is not None:
                dics.extend(top_dic)
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


def _storage(value):
    if isinstance(value, dict):
        dics = []
        top_dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "primary hard drive size".lower():
                if len(sub_value.split(" ")) != 2:
                    continue
                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
                dics.extend(sub_dics)
            if sub_key.lower() == "primary hard drive type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

            if sub_key.lower() == "secondary hard drive size".lower():
                if len(sub_value.split(" ")) != 2:
                    continue
                [quantity, unit] = sub_value.split(" ")
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
                dics.extend(sub_dics)
            if sub_key.lower() == "secondary hard drive type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

            if sub_key.lower() == "memory card reader".lower():
                kinds = sub_value.split(",")
                for kind in kinds:
                    sub_dic = create_tag("technology", "memorycard", kind.replace(" ", ""))
                    top_dics.extend(sub_dic)

            if sub_key.lower().find("speed hdd #".lower()) != -1:  # speed hdd # 1/2/3
                if len(sub_value.split(" ")) != 2:
                    continue
                [quantity, unit] = sub_value.split(" ")[:2]
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "speed", unit))
                dics.extend(sub_dics)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "storage")
            dics.extend(sub_dics)
            subpart_dic = create_tag("subpart", "component", None, dics)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic, top_dics

        else:
            return dics, top_dics


def _memory(value):
    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            # if sub_key.lower() == "memory Included".lower():
            #
            #     [quantity, unit] = sub_value.split(" ")
            #     unit = swe2eng.translate_SweToEng(unit)
            #     sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
            #     dics.extend(sub_dics)

            # if sub_key.lower() == "maximum memory".lower():
            #
            #     qua_unit = sub_value.split(" ")
            #     if len(qua_unit) != 2:
            #         continue
            #     [quantity, unit] = qua_unit[:2]
            #     unit = swe2eng.translate_SweToEng(unit)
            #     sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
            #     dics.extend(sub_dics)

            if sub_key.lower() == "memory type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

            if sub_key.lower() == "memory speed".lower():
                qua_unit = sub_value.split(" ")
                quantity, unit = qua_unit[0], qua_unit[-1]
                if len(qua_unit) != 2:
                    continue
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "frequency", unit))
                dics.extend(sub_dics)

            elif sub_key.lower() == "memory".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = int(qua_unit[0]), qua_unit[-1]

                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("memory", "kind", "memory", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "free memory locations".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = int(qua_unit[0]), qua_unit[-1]

                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("memory", "kind", "memory", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower().find("slot".lower()) != -1:
                sub_dics = create_tag("feature", "has", "slots", create_tag("size", "quantity", int(sub_value)))
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

            elif sub_key.lower().find("thunderbolt".lower()) != -1:  # thunderbolt 1/2/3
                sub_dics = create_tag("connection", "type", sub_key.lower(), create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "other connections".lower():
                sub_dics = create_tag("connection", "type", sub_value)
                dics.extend(sub_dics)

            elif sub_key.lower() == "MagSafe".lower():
                sub_dics = create_tag("connection", "type", "MagSafe", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "vga".lower():
                sub_dics = create_tag("connection", "type", "vga", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "dvi".lower():
                sub_dics = create_tag("connection", "type", "dvi", create_tag("size", "quantity", quantity))
                dics.extend(sub_dics)

            elif sub_key.lower() == "digital audio output (optical)".lower():
                sub_dics = create_tag("connection", "type", "digital audio output (optical)",
                                      create_tag("size", "quantity", int(sub_value[0])))
                dics.extend(sub_dics)

            elif sub_key.lower() == "digital audio output (coaxial)".lower():
                sub_dics = create_tag("connection", "type", "digital audio output (coaxial)",
                                      create_tag("size", "quantity", int(sub_value[0])))
                dics.extend(sub_dics)
            elif sub_key.lower() == "headphone output".lower():
                sub_dics = create_tag("connection", "type", "headphone",
                                      create_tag("size", "quantity", int(sub_value[0])))
                dics.extend(sub_dics)
            elif sub_key.lower() == "headphone output".lower():
                sub_dics = create_tag("connection", "type", "microphone",
                                      create_tag("size", "quantity", int(sub_value[0])))
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
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "height", num(quantity), create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            if sub_key.lower() == "Width".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)
                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "width", num(quantity), create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            if sub_key.lower() == "Depth".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)
                if unit.lower() == "mm":
                    unit = "millimetre"
                if unit.lower() == "cm":
                    unit = "centimetre"
                sub_dics = create_tag("size", "depth", num(quantity), create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            if sub_key.lower() == "power supply".lower():
                qua_unit = sub_value.lower()
                if qua_unit.find('w') != -1:
                    qua = qua_unit[: qua_unit.find('w')]
                    sub_dics = create_tag("size", "powersource", int(qua), create_tag("unit", "metric", "watt"))
                    dics.extend(sub_dics)

            if sub_key.lower() == "weight".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)
                if unit.lower() == "kg":
                    unit = "kilogram"
                if unit.lower() == "g":
                    unit = "gram"
                sub_dics = create_tag("size", "weight", num(quantity), create_tag("unit", "metric", unit))
                dics.extend(sub_dics)

            if sub_key.lower() == "chassis".lower():
                sub_dics = create_tag("hardware", "chassi", sub_value)
                dics.extend(sub_dics)

            if sub_key.lower() == "color".lower():
                sub_dics = create_tag("quality", "color", sub_value)
                dics.extend(sub_dics)

            if sub_key.lower() == "material".lower():
                sub_dics = create_tag("quality", "material", sub_value)
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
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "time", unit))
                dics.extend(sub_dics)

            elif sub_key.lower() == "Warranty Battery".lower():
                qua_unit = sub_value.split(" ")

                if len(qua_unit) != 2:
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "time", unit))
                dics.extend(sub_dics)

        feature_dic = create_tag("feature", "warranty", "hardware", dics)
        return feature_dic


def _communication(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "Wireless Network".lower():
                sub_dics = create_tag("technology", "technology", sub_value)
                super_dic = create_tag("communication", "type", "wifi", sub_dics)
                dics.extend(super_dic)

            if sub_key.lower() == "Fixed Network".lower():
                qua_unit = sub_value
                quantity = qua_unit[:qua_unit.find('bit/s')-1]

                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "speed", "Mbit/s"))
                super_dic = create_tag("communication", "type", "ethernet", sub_dics)
                dics.extend(super_dic)

            if sub_key.lower() == "Bluetooth version".lower():
                sub_dics = create_tag("communication", "type", "bluetooth", create_tag("identifier", "version", sub_value))
                dics.extend(sub_dics)

            if sub_key.lower() == "resolution still image".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                sub_dics = create_tag("size", "resolution", num(qua_unit[0]),
                                      create_tag("unit", "resolution", qua_unit[1]))
                sub_dics.extend(create_tag("identifier", "version", "still"))

                super_dic = create_tag("communication", "type", "webcam", sub_dics)
                dics.extend(super_dic)

            if sub_key.lower() == "Resolution Video".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                sub_dics = create_tag("size", "resolution", num(qua_unit[0]),
                                      create_tag("unit", "resolution", qua_unit[1]))
                sub_dics.extend(create_tag("identifier", "version", "still"))
                super_dic = create_tag("communication", "type", "webcam", sub_dics)
                dics.extend(super_dic)

            if sub_key.lower() == "resolution still image".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                sub_dics = create_tag("size", "resolution", num(qua_unit[0]),
                                      create_tag("unit", "resolution", qua_unit[1]))
                sub_dics.extend(create_tag("identifier", "version", "video"))
                super_dic = create_tag("communication", "type", "webcam", sub_dics)
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
                    continue
                quantity, unit = num(qua_unit[0]), qua_unit[-1]
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
        working_memory_dics = []
        brand_dics = []
        sound_dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "shared graphics memory".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                unit = swe2eng.translate_SweToEng(unit)

                sub_dic = create_tag("size", "quantity", num(quantity), create_tag("unit", "storage", unit))
                working_memory_dics.extend(sub_dic)

            if sub_key.lower() == "speaker".lower():
                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                quantity, unit = qua_unit[0], qua_unit[-1]
                sub_dic = create_tag("identifier", "kind", "speaker", create_tag("size", "quantity", int(quantity)))
                sound_dics.extend(sub_dic)

            if sub_key.lower() == "sound card".lower():
                sub_dic = create_tag("communication", "type", "soundcard", create_tag("identifier", "model", num(sub_value)))
                sound_dics.extend(sub_dic)

            if sub_key.lower() == "Graphics Card".lower() or sub_key.lower() == "Video Card".lower():
                sub_dic = create_tag("identifier", "name", sub_value)
                brand_dics.extend(sub_dic)
                if sub_value.find("AMD") != -1:
                    sub_dic = create_tag("identifier", "brand", "AMD")
                    brand_dics.extend(sub_dic)

        res_dic = []
        if len(working_memory_dics) + len(brand_dics) != 0:
            if len(working_memory_dics) != 0:
                id_dic = create_tag("identifier", "kind", "working_memory")
                working_memory_dics.extend(id_dic)
            if len(brand_dics) != 0:
                working_memory_dics.extend(brand_dics)

            sub_subpart_dic = create_tag("subpart", "component", None, working_memory_dics)

            id_dic = create_tag("identifier", "kind", "gpu")
            id_dic.extend(sub_subpart_dic)

            subpart_dic = create_tag("subpart", "component", None, id_dic)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)

            res_dic.extend(usp_dic)
            res_dic.extend(subpart_dic)

        if len(sound_dics) != 0:
            id_dic = create_tag("identifier", "kind", "speaker")
            sound_dics.extend(id_dic)
            subpart_dic = create_tag("subpart", "component", None, sound_dics)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)

            res_dic.extend(usp_dic)
            res_dic.extend(subpart_dic)

        return res_dic


def _general(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())


            if sub_key.lower() == "also available in Art".lower():
                sub_dics = create_tag("identifier", "id_creator", sub_value)
                dics.extend(sub_dics)

            if sub_key.lower() == "Operating System".lower() or sub_key.lower() == "OS".lower():
                sub_dics = create_tag("software", "os", sub_value)
                dics.extend(sub_dics)

        return dics


def _screen(value):
    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "screen size".lower():
                [quantity, unit] = sub_value.split(" ")
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "imperial", "inch"))
                dics.extend(sub_dics)

            if sub_key.lower() == "aspect ratio".lower():

                sub_dics = create_tag("size", "ratio", sub_value)
                dics.extend(sub_dics)

            elif sub_key.lower() == "maximum resolution".lower():
                sub_dic = create_tag("size", "resolution", sub_value)
                dics.extend(sub_dic)

            elif sub_key.lower() == "display technology".lower():
                sub_dic = create_tag("technology", "panel", sub_value)
                dics.extend(sub_dic)

            elif sub_key.lower() == "screen technology".lower():
                sub_dic = create_tag("technology", "panel", sub_value)
                dics.extend(sub_dic)

            elif sub_key.lower() == "screen type".lower():
                sub_dic = create_tag("identifier", "type", sub_value)
                dics.extend(sub_dic)

            elif sub_key.lower() == "screen surface".lower():
                sub_dic = create_tag("identifier", "surface", sub_value)
                dics.extend(sub_dic)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "screen")
            dics.extend(sub_dics)
            subpart_dic = create_tag("subpart", "component", None, dics)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic
        else:
            return dics


def _spec_feature(value):
    if isinstance(value, dict):
        dics = []

        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())
            print(sub_key, sub_value)

            if sub_key.lower().find("Other Features".lower()) != -1:
                str = sub_value.lower()
                pos = str.find(("Ljusstyrka på").lower())
                if pos != -1:
                    pos += len(("Ljusstyrka på").lower())
                    sub = str[pos + 1:]
                    quan_unit = sub.split(" ")
                    if len(quan_unit) != 2:
                        continue
                    quan, unit = quan_unit[:2]
                    sub_dics = create_tag("feature", "has", "brightness",
                                          create_tag("size", "quantity", quan, create_tag("unit", "metric", "cd/m2")))
                    dics.extend(sub_dics)

        return dics


def _battery(value):

    if isinstance(value, dict):
        dics = []
        for sub_key, sub_value in value.items():
            sub_key = swe2eng.translate_SweToEng(sub_key.lower())

            if sub_key.lower() == "number of cells".lower():
                sub_dics = create_tag("powersource", "cells", num(sub_value))
                dics.extend(sub_dics)

            if sub_key.lower() == "operating time (up to)".lower():

                qua_unit = sub_value.split(" ")
                if len(qua_unit) != 2:
                    continue
                [quantity, unit] = qua_unit[:2]
                unit = swe2eng.translate_SweToEng(unit)
                sub_dics = create_tag("size", "quantity", num(quantity), create_tag("unit", "time", "hour"))
                dics.extend(sub_dics)

            elif sub_key.lower() == "battery type".lower():
                sub_dic = create_tag("technology", "technology", sub_value)
                dics.extend(sub_dic)

        if len(dics) != 0:
            sub_dics = create_tag("identifier", "kind", "battery")
            dics.extend(sub_dics)
            subpart_dic = create_tag("subpart", "component", None, dics)
            usp_dic = create_tag("usp", "id", subpart_dic[0]["id"], None)
            subpart_dic.extend(usp_dic)
            return subpart_dic
        else:
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

