import hashlib
import io
import json
import os
import re
import sys
import tempfile
import zipfile

# Generates files
OUTPUT_DIR = "out"
TMP_DIR = tempfile.tempdir
PATH_IN_ZIP_REGEX = "assets/([a-zA-Z0-9_+]+)/textures/item/(.+)"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
if not os.path.exists("en_us.json"):
    print("Cannot find en_us.json for translation. Please download it from our repository or provide by yourself.")
    exit(0)


def read_json_inzip(name: str, file: zipfile) -> dict[str, str]:
    with file.open(name, "r") as fd:
        return json.load(fd)


def write_json_fromzip(name: str, dest: str, file: zipfile):
    with io.FileIO(dest, "w") as fd:
        fd.write(file.read(name))


locales = dict[str, str]()


def extract_resource(zip: str):
    if not zipfile.is_zipfile(zip):
        print("Not a valid zip.")
        exit(0)
    prefix = hashlib.sha384(zip.encode("utf-8")).hexdigest()[:6]
    file = zipfile.ZipFile(zip)
    # find locale files.
    for name in file.namelist():
        if name.endswith("en_us.json"):
            sp = name.split("/")
            if sp[0] != "assets":  # not this
                continue
            # ..else
            locales[sp[1]] = read_json_inzip(name, file)

    # then read.
    for name in file.namelist():
        if name.endswith("pack.png"):
            continue
        matchPath = re.match(PATH_IN_ZIP_REGEX, name)
        if matchPath:
            _name = matchPath.group(2)
            namespace = matchPath.group(1)
            # print(_name)
            if "/" not in _name and _name.endswith(".png"):
                # extract.
                write_json_fromzip(name, OUTPUT_DIR + "/" + prefix + "_" + _name, file)  # copy png

                # deal with translation
                key = _name.removesuffix(".png")
                fname = OUTPUT_DIR + "/" + prefix + "_" + key + ".txt"
                if "_" in key:  # item_xx_03
                    sp = key.split("_")
                    if sp[len(sp) - 1].isnumeric():
                        sp.pop()
                        key = "_".join(sp)
                LANG = locales[namespace]
                with open(fname, "w") as fd:
                    # translationName = ""
                    dictKey = f"item.{namespace}.{key}"
                    if dictKey not in LANG:
                        if dictKey not in MOJANG_LANG:
                            print(f"Cannot find translation for {key}")
                            translationName = key.replace("_", " ")
                        else:
                            translationName = MOJANG_LANG[dictKey]
                    else:
                        translationName = LANG[dictKey]
                    fd.write(translationName)
    file.close()


if __name__ == "__main__":
    MOJANG_LANG = json.load(open("en_us.json"))
    locales["minecraft"] = MOJANG_LANG
    for target_zip in sys.argv:
        if target_zip.endswith(".zip") or target_zip.endswith(".jar"):
            print(f"Processing {target_zip}")
            extract_resource(target_zip)
    print("All done!")
