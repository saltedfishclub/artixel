import hashlib
import io
import json
import os
import sys
import tempfile
import zipfile

# Generates files
OUTPUT_DIR = "out"
TMP_DIR = tempfile.tempdir
PATH_IN_ZIP = "assets/minecraft/textures/item/"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
if not os.path.exists("en_us.json"):
    print("Cannot find en_us.json for translation. Please download it from our repository or provide by yourself.")
    exit(0)


def extract_resource(zip: str):
    if not zipfile.is_zipfile(zip):
        print("Not a valid zip.")
        exit(0)
    prefix = hashlib.sha384(zip.encode("utf-8")).hexdigest()[:6]
    file = zipfile.ZipFile(zip)
    for name in file.namelist():
        if name.endswith("pack.png"):
            continue
        if name.startswith(PATH_IN_ZIP):
            _name = name.removeprefix(PATH_IN_ZIP)
            # print(_name)
            if "/" not in _name and _name.endswith(".png"):
                # extract.
                with io.FileIO(OUTPUT_DIR + "/" + prefix + "_" + _name, "w") as fd:
                    fd.write(file.read(name))

                key = _name.removesuffix(".png")
                fname = OUTPUT_DIR + "/" + prefix + "_" + key + ".txt"
                with open(fname, "w") as fd:
                    # translationName = ""
                    dictKey = "item.minecraft." + key
                    if dictKey not in MOJANG_LANG:
                        print(f"Cannot find translation for {key}")
                        translationName = key.replace("_", " ")
                    else:
                        translationName = MOJANG_LANG[dictKey]
                    fd.write(translationName)
    file.close()


if __name__ == "__main__":
    MOJANG_LANG = json.load(open("en_us.json"))
    for target_zip in sys.argv:
        if target_zip.endswith(".zip"):
            print(f"Processing {target_zip}")
            extract_resource(target_zip)
    print("All done!")
