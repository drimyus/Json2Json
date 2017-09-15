
def load_Labels_Table(txt_path):

    list = []
    with open(txt_path) as f:
        cnt = 0
        for line in f:
            cnt += 1
            print(cnt, line)

            [src_key, src_value, category, type, value, tags] = line[:-1].split(':')
            category.lower().replace('"', '')
            type.lower().replace('"', '')
            value.lower().replace('"', '')
            tags.lower().replace('"', '')

            dic = {
                'key': src_key,
                'category': category,
                'type': type,
                'value': value,
                'tags': tags
            }

            list.append(dic)

    return list

if __name__ == '__main__':
    label_txt_path = "./keys/labels.txt"
    load_Labels_Table(label_txt_path)
