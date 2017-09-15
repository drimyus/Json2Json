import sys
import json
import os


class Swedish_Keys:
    def __init__(self, raw_json="", swe_txt="./keys/swedish_keys.txt", eng_txt="./keys/english_keys.txt"):

        self.raw_json = raw_json
        self.swe_txt = swe_txt
        self.eng_txt = eng_txt

        self.swe_keys, self.eng_keys = [], []

        if os.path.isfile(eng_txt) and os.path.isfile(swe_txt):
            self.load_Swedish2English_Key_Dict(swe_txt, eng_txt)
        else:
            sys.stderr.write("incorrect dictionary txt file {}.\n".format(eng_txt))

    def explore_Swedish_Keys(self, json_path):
        txt_path = self.swe_txt
        # load source data json
        with open(json_path, encoding='utf-8') as f:
            cnt = 0
            for line in f:
                cnt += 1
                obj = json.loads(line)
                self.get_keys(obj)
            sys.stdout.write("lines: {}\n".format(cnt))
        # write the detected keys to a file
        with open(txt_path, 'w', encoding='utf-8') as file:
            self.swe_keys.sort()
            for key in self.swe_keys:
                file.write("{}\n".format(key))
            sys.stdout.write("Number of keys: {}\n".format(len(self.swe_keys)))

    def get_keys(self, json_obj):
        for key, value in json_obj.items():
            if type(value) is dict:
                self.get_keys(value)
            if key.lower() not in self.swe_keys:
                self.swe_keys.append(key.lower())

    def load_Swedish2English_Key_Dict(self, swe_path, eng_path):
        with open(swe_path) as f:
            for line in f:
                swe = line[:-1]
                self.swe_keys.append(swe.lower())
        with open(eng_path) as f:
            for line in f:
                eng = line[:-1]
                self.eng_keys.append(eng.lower())
        sys.stdout.write("swedish_keys: {}, english_keys: {}".format(len(self.swe_keys), len(self.eng_keys)))

    def translate_SweToEng(self, swe_key):
        if len(self.swe_keys) == 0 or len(self.eng_keys) == 0:
            sys.stderr.write("plesae init the dictionary.\n")
            sys.exit(1)
        else:
            try:
                idx = self.swe_keys.index(swe_key)
                return self.eng_keys[idx]
            except Exception as ex:
                print(ex)


if __name__ == '__main__':

    raw_json_path = "./data/sourcedata (1).json"

    swe_to_eng = Swedish_Keys()
    swe_to_eng.explore_Swedish_Keys(raw_json_path)
    # print(swe_to_eng.translate_SweToEng("brand"))


