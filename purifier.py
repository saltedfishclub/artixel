import io
import os
import sys

from PIL import Image, UnidentifiedImageError


def verify(file: str):
    with io.FileIO(file) as fd:
        a = fd.read()
        acTL = a.find(b"\x61\x63\x54\x4C")
        if acTL > 0:  # find returns -1 if it cant find anything
            iDAT = a.find(b"\x49\x44\x41\x54")
            if acTL < iDAT:
                print("Found a APNG file: " + file)
                return True
    try:
        img = Image.open(file)
        if img.is_animated:
            print("Found a ANIMATED file: " + file)
            return True
        img.verify()
    except (IOError, SyntaxError, UnidentifiedImageError) as e:
        print(f"Found a BROKEN image: " + file)
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("A folder to scan is needed.")
        exit(0)
    folder = sys.argv[1]
    for file in os.listdir(folder):
        if file.endswith(".png"):
            remove = False
            path = folder + "/" + file
            if verify(path):
                remove = True
                transKey = path.removesuffix(".png") + ".txt"
                if os.path.exists(transKey):
                    os.remove(transKey)
            if remove:
                os.remove(path)
