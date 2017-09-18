import sys
import json
import os


class Swedish_Keys:
    def __init__(self, raw_json="", swe_txt="./keys/swedish_keys.txt", swe2eng_txt="./keys/swedish2english_keys.txt"):

        self.raw_json = raw_json
        self.swe_txt = swe_txt
        self.swe2eng_txt = swe2eng_txt

        self.swe_keys, self.eng_keys, self.eng_keys_BIG = [], [], []

        if os.path.isfile(swe2eng_txt):
            self.load_Swedish2English_Key_Dict(swe2eng_txt)
        else:
            sys.stderr.write("incorrect dictionary txt file {}.\n".format(swe2eng_txt))

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

    def load_Swedish2English_Key_Dict(self, swe2eng_path):
        with open(swe2eng_path, encoding='utf-8') as f:
            for line in f:
                [swe, eng] = line[:-1].split(":")
                self.swe_keys.append(swe.lower())
                self.eng_keys.append(eng.lower())
                self.eng_keys_BIG.append(eng)

        # sys.stdout.write("swedish_keys: {}, english_keys: {}".format(len(self.swe_keys), len(self.eng_keys)))

    def translate_SweToEng(self, swe_key):
        if len(self.swe_keys) == 0 or len(self.eng_keys) == 0:
            sys.stderr.write("plesae init the dictionary.\n")
            sys.exit(1)
        else:
            if swe_key.lower() in self.swe_keys:
                idx = self.swe_keys.index(swe_key.lower())
                return self.eng_keys_BIG[idx]
            else:
                print(swe_key)
                return swe_key


if __name__ == '__main__':

    raw_json_path = "./data/sourcedata (1).json"

    swe_to_eng = Swedish_Keys()
    swe_to_eng.explore_Swedish_Keys(raw_json_path)
    # print(swe_to_eng.translate_SweToEng("brand"))


