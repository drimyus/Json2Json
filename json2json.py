import json
import uuid
import sys

import labels
from swedish_keys import Swedish_Keys


Structure = ["id", "title", "url", "image_url", "description",
             "description_html", "rating_value", "price", "brand", "currency",
             "category", "bulleted_text", "technical_specifications"]
Categories, Types = None, None


def load_SourceData(json_path):

    # load source data json
    data = []
    with open(json_path, encoding='utf-8') as f:
        for line in f:

            source_obj = json.loads(line)
            product_obj = parse_source_obj(source_obj)

            data.append(product_obj)
            break


def parse_source_obj(json_obj):

    for key, value in json_obj.items():
        key = key.lower()

        eng_key = swe2eng.translate_SweToEng(key)

        # sys.stdout.write("swe: {}, eng: {}\n".format(key, eng_key))

        if isinstance(value, dict):
            subdict = parse_source_obj(value)

        else:
            pass


def create_tag_object(category, type, value, tags=None):
    id = uuid.uuid4()
    if tags is not None:
        return {"id": id,
                "category": category,
                "type": type,
                "value": value,
                "tags": tags}
    else:
        return {"id": id,
                "category": category,
                "type": type,
                "value": value}


if __name__ == '__main__':

    labels_path = "./keys/labels.txt"
    categories, types = labels.load_Labels_Table(labels_path)

    # global Categories, Types
    Categories = categories
    Types = types

    swe2eng = Swedish_Keys()

    source_fname = "./data/sourcedata (1).json"
    load_SourceData(source_fname)

