import os
from typing import Text, Dict


def gen_table_path(bucket: Text, path: Text, options: Dict, function: Text):
    options_string = ""
    file_path = f"s3://{os.path.join(bucket, path)}"
    table = f"{function}('{file_path}'"

    if options:
        options_string = ", " + ", ".join([f"{k}={v}" for k, v in options.items()])

    table += options_string + ")"

    return table
