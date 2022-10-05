import io
import os
import re
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
        print(f"Found a BROKEN image: " + file + f" Err: {e}")
        return True


MATCH_NUMBER_REGEX = "^.\w+[^ ]?(\d+)$"
lowerCaseRegex = "[a-z]+[A-Z0-9][a-z0-9]+[A-Za-z0-9]*"


def process(data: str) -> str:
    _result = data.replace("-", " ").replace(".", " ")
    match = re.match(MATCH_NUMBER_REGEX, data)
    if match:
        num = match.group(1)
        _result = data.removesuffix(num)
        _result += " " + num
        # print(f"Fixed {data} -> {_result}")
    if re.match(lowerCaseRegex, _result):
        _result = get_lower_case_name(_result)  # .removeprefix("item ")
        # print(f"Fixed {data} -> {_result}")
        return _result
    return _result  # .removeprefix("item").removeprefix(" ")


def get_lower_case_name(text):
    lst = []
    for index, char in enumerate(text):
        if char.isupper() and index != 0:
            lst.append(" ")
        lst.append(char)

    return "".join(lst).lower()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("A folder to scan is needed.")
        exit(0)
    folder = sys.argv[1]
    for file in os.listdir(folder):
        path = folder + "/" + file
        if file.endswith(".png"):
            remove = False
            if verify(path):
                remove = True
                transKey = path.removesuffix(".png") + ".txt"
                if os.path.exists(transKey):
                    os.remove(transKey)
            if remove:
                os.remove(path)
        if file.endswith(".txt"):
            if not os.path.exists(path):
                continue
            with io.FileIO(path, "r") as fd:
                data: str = fd.read().decode("utf-8")
                result = process(data).replace(".", "").replace("-", "")
            with io.FileIO(path, "w") as fd:
                fd.write(bytes(result, "utf-8"))
                #print(f"Fixed {data} -> {result}")

    # invoke magick
    os.system(f"mogrify {folder}/*.png")
