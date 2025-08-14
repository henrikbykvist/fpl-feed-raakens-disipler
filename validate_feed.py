
import json, os, sys
def main(path="data/latest.json"):
    if not os.path.exists(path):
        print("Missing:", path); return 1
    with open(path,"r",encoding="utf-8") as f:
        data = json.load(f)
    for key in ["fpl","_fetched_at_utc"]:
        if key not in data:
            print("Missing top-level key:", key); return 1
    for key in ["bootstrap_static","fixtures","entry","leagues"]:
        if key not in data["fpl"]:
            print("Missing fpl key:", key); return 1
    print("Feed looks OK.")
    return 0
if __name__=="__main__":
    sys.exit(main())
