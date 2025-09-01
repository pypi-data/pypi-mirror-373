import argparse

def b_zip():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir_path")
    args = parser.parse_args()

    from .Barchive import b_archive_zip
    b_archive_zip(args.dir_path)