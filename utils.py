from json import load, dump


def get_submission_data(file_name):
    with open("db.json", "wb") as json:
        db = load(json)
        caption, url = db.pop(file_name)
        dump(db, json)
        return caption, url
