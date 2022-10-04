import hashlib
import io
import os
import re
import sys
import tempfile
import zipfile

import json5

# Generates files
OUTPUT_DIR = "out"
TMP_DIR = tempfile.tempdir
PATH_IN_ZIP_REGEX = ".*assets\/([a-zA-Z0-9_+]+)\/textures\/item[s]?\/(.+)"
LANG_PATH_IN_ZIP_REGEX = ".*?assets\/([a-zA-Z0-9_+]+)\/lang\/(.+)"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
if not os.path.exists("en_us.json"):
    print("Cannot find en_us.json for translation. Please download it from our repository or provide by yourself.")
    exit(0)


def read_json5_inzip(name: str, file: zipfile) -> dict[str, str]:
    with file.open(name, "r") as fd:
        return json5.load(fd)


def write_json5_fromzip(name: str, dest: str, file: zipfile):
    with io.FileIO(dest, "w") as fd:
        fd.write(file.read(name))


MOJANG_LANG: dict[str, str] = json5.load(open("en_us.json"))
locales = dict[str, dict[str, str]]()


def read_lang_inzip(name, file) -> dict[str, str]:
    with file.open(name, "r") as fd:
        content = fd.read().decode("utf-8")
        nd = dict[str, str]()
        for line in content.splitlines():
            sp = line.split("=")
            if len(sp) != 2:
                # print(f"Cannot parse {line} from {name}")
                continue
            else:
                nd[sp[0].lower()] = sp[1]
        return nd


def extract_resource(zip: str):
    found = 0
    notfound = 0
    if not zipfile.is_zipfile(zip):
        print(f"Not a valid zip. ${zip}")
        return
    _def_prefix = hashlib.sha384(zip.encode("utf-8")).hexdigest()[:6]
    file = zipfile.ZipFile(zip)
    print(f"Processing {zip}")
    # find locale files.
    for name in file.namelist():
        if name.endswith("en_us.json"):
            sp = name.split("/")
            if sp[0] != "assets":  # not this
                continue
            # ..else
            locales[sp[1]] = read_json5_inzip(name, file)
        #  print(f"Found namespace {sp[1]}")
        # earlier versions
        elif name.endswith("en_US.lang"):
            try:
                match = re.match(LANG_PATH_IN_ZIP_REGEX, name)
                dct = read_lang_inzip(name, file)
                if match:
                    ns = match.group(1)
                    if dct:
                        locales[ns.lower()] = dct
                else:
                    MOJANG_LANG.update(dct)
            except UnicodeDecodeError as err:
                print(f"Can't decode {name}, {err}")

                # then read.
    for name in file.namelist():
        if name.endswith("pack.png"):
            continue
        matchPath = re.match(PATH_IN_ZIP_REGEX, name)
        # print(name)
        if matchPath:
            # print(f"Found {name}")
            _name = matchPath.group(2)
            namespace = matchPath.group(1)
            if namespace == "minecraft":
                prefix = _def_prefix
            else:
                prefix = namespace
            # print(_name)
            if "/" not in _name and _name.endswith(".png"):
                # extract.
                write_json5_fromzip(name, OUTPUT_DIR + "/" + prefix + "_" + _name, file)  # copy png

                # deal with translation
                key = _name.removesuffix(".png")
                fname = OUTPUT_DIR + "/" + prefix + "_" + key + ".txt"
                if "_" in key:  # item_xx_03
                    sp = key.split("_")
                    if sp[len(sp) - 1].isnumeric():
                        sp.pop()
                        key = "_".join(sp)
                if namespace in locales:
                    # print(f"Found namespace {namespace}")
                    LANG = locales[namespace]
                else:
                    LANG = dict()
                with open(fname, "w") as fd:
                    # translationName = ""
                    dictKey = f"item.{namespace}.{key}"
                    if dictKey not in LANG:
                        if dictKey + ".name" not in LANG:
                            if dictKey not in MOJANG_LANG:
                                if f"item.{key}.name" not in MOJANG_LANG:
                                    if f"item.{key}.name" not in LANG:
                                        translationName = key.replace("_", " ")
                                        #          print("Can't found translation for " + key)
                                        notfound = notfound + 1
                                    else:
                                        translationName = LANG[f"item.{key}.name"]
                                        found = found + 1
                                else:
                                    translationName = MOJANG_LANG[f"item.{key}.name"]
                                    found = found + 1
                            else:
                                translationName = MOJANG_LANG[dictKey]
                                found = found + 1
                        else:
                            #   print("Found translation for key " + key)
                            translationName = LANG[dictKey + ".name"]
                            found = found + 1
                    else:
                        # print("Found translation for key " + key)
                        translationName = LANG[dictKey]
                        found = found + 1
                    fd.write(translationName)
    print(f"Found: {found} NotFound: {notfound}")
    file.close()


if __name__ == "__main__":
    locales["minecraft"] = MOJANG_LANG
    for target_zip in sys.argv:
        if target_zip.endswith(".zip") or target_zip.endswith(".jar"):
            #  print(f"Processing {target_zip}")
            extract_resource(target_zip)
        elif os.path.isdir(target_zip):
            for entry in os.listdir(target_zip):
                #     print(f"Processing {entry}")
                extract_resource(target_zip + "/" + entry)

    print("All done!")
