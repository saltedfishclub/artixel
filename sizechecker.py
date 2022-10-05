import os

from PIL import Image

def traverseFiles(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            if f.endswith('.png'):
                path = os.path.join(root, f)
                yield path

def main():
    cnt = 0

    folder = './train/'
    for fileName in traverseFiles(folder):
        image = Image.open(fileName)

        if image.width != 32 or image.height != 32:
            print(fileName)
            cnt += 1

    print(cnt)

if __name__ == '__main__':
    main()