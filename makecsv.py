# sys.path.append('/Users/kyutatsu/Documents/machine_learning/python')して使って。

import numpy as np
import csv
import subprocess
import pathlib
import math
from PIL import Image



def makecsv(folder, csvfile, dimension=10000, color='L'):
    '''convert Imagefile(jpg,png,etc) to csv file.

    (e.g.)makecsv('path/to/images/folder', 'path/to/new/csv/file.csv', 10000, 'L')
    1000 means 100 by 100 matrix will be expected.
    'L' means Greyscale.
    '''
    original_images = subprocess.run(
            ('ls', folder),
            stdout=subprocess.PIPE,
            universal_newlines=True
    )
    original_images = original_images.stdout.split('\n')
    # The last element is ''. To avoid opening(''), I have gotten rid of
    # it.
    original_images.remove('')

    folder_path = pathlib.PurePath(folder)
    with open(csvfile, 'w', newline='') as f:
        writer = csv.writer(f)
        for path in original_images:
            path_to_image = folder_path / path
            img = Image.open(str(path_to_image))
            longer_side = max(img.size)
            shorter_side = min(img.size)
            diffby2 = (longer_side - shorter_side) / 2
            if img.size[1] == longer_side:  # 縦長画像
                box = (0, diffby2, shorter_side, shorter_side+diffby2)
            else:
                box = (diffby2, 0, shorter_side+diffby2, shorter_side)
            img_colored = img.convert(mode=color)
            img_croped = img_colored.crop(box=box)
            size = round(math.sqrt(dimension))
            img_resized = img_croped.resize((size,size))
            row_vec_list = list(img_resized.getdata())
            writer.writerow(row_vec_list)


def get_array_from_imgfile(fileobj, dimension=10000, color='L'):
    """convert image_file_obj to np.array.

    fileobj should be file line object.
    """
    img = Image.open(fileobj)
    longer_side = max(img.size)
    shorter_side = min(img.size)
    diffby2 = (longer_side - shorter_side) / 2
    if img.size[1] == longer_side:  # 縦長画像
        box = (0, diffby2, shorter_side, shorter_side+diffby2)
    else:
        box = (diffby2, 0, shorter_side+diffby2, shorter_side)
    img_colored = img.convert(mode=color)
    img_croped = img_colored.crop(box=box)
    size = round(math.sqrt(dimension))
    img_resized = img_croped.resize((size,size))
    # img_resized.getdata()=> object. list化=>  0-255の数値のリスト
    row_vec_list = list(img_resized.getdata())
    # 軽くしたいので0-255のuint8.
    return np.array(row_vec_list, dtype=np.uint8)
