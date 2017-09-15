
def load_Labels_Table(txt_path):

    categories = []
    types = []
    with open(txt_path) as f:
        for line in f:
            [category, type] = line[:-1].split(':')
            categories.append(category.lower().replace('"', ''))
            types.append(type.lower().replace('"', ''))

    return categories, types

if __name__ == '__main__':
    label_txt_path = "./key/labels.txt"
    load_Labels_Table(label_txt_path)
