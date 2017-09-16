import sys


class Label:
    def __init__(self, label_txt="./keys/labels.txt"):
        self.label_txt = label_txt

        self.labels = []

        self.labels = self.load_Labels_Table()

    def load_Labels_Table(self):

        list = []
        with open(self.label_txt, encoding='utf-8') as f:
            cnt = 0
            for line in f:
                cnt += 1
                # print(cnt, line)

                [src_key, src_value, category, type, value, tags] = line[:-1].split(':')
                src_key.lower().replace('"', '')
                src_value.lower().replace('"', '')

                category.lower().replace('"', '')
                type.lower().replace('"', '')
                value.lower().replace('"', '')
                tags.lower().replace('"', '')

                dic = {
                    "src_key": src_key,
                    "src_value": src_value,
                    "tar_category": category,
                    "tar_type": type,
                    "tar_value": value,
                    "tar_tags": tags
                }

                list.append(dic)
        return list

    def get_key2label(self, src_key):
        for dic in self.labels:
            if src_key == dic["src_key"]:
                return dic
        # sys.stdout.write("{} is not in Label table\n".format(src_key))

if __name__ == "__main__":

    label = Label()

    print(label.get_key2label("id"))


