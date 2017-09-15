import json
import uuid
import sys

import labels
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

        if isinstance(value, dict):
            value = parse_source_obj(value)

        dic_list.append(create_tag_object(eng_key, value))

    return dic_list


def create_tag_object(src_key, src_value):

    id = uuid.uuid4()

    tag = label.get_key2label(src_key=src_key)
    if tag is None:
        return
    if tag["tar_value"] == "string":
        dic = {
            "id": id,
            "category": tag["tar_category"],
            "type": tag["tar_type"],
            "value": src_value
        }
        return dic
    else:
        pass



if __name__ == '__main__':

    """-------------------------Loading the Label data---------------------"""
    label = Label()

    """-------------------------Create the dictionary object---------------"""
    swe2eng = Swedish_Keys()

    """-------------------------Main Progress -----------------------------"""
    source_fname = "./data/sourcedata (1).json"
    load_SourceData(source_fname)

