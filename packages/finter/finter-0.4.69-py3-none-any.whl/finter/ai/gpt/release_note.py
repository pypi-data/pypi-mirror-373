import os

from qore_client import QoreClient


def get_logs():
    diff_script_path = os.path.join(os.path.dirname(__file__), "tag_diff_logs.sh")
    with os.popen(f"bash {diff_script_path}") as p:
        output = p.read()
    return output


def get_tag(output):
    tag = None
    for line in output.split("\n"):
        if "Most recent tag" in line:
            tag = line.split(": ")[-1]
            break
    return tag


def read_log_file():
    log_output = get_logs()
    recent_tag = get_tag(log_output)
    return log_output, recent_tag


def generate_release_note(log_output):
    qc = QoreClient(
        access_key=os.getenv("QORE_ACCESS_KEY"),
        secret_key=os.getenv("QORE_SECRET_KEY"),
    )
    response = qc.execute_webhook("V29ya2Zsb3c6MTI0", log_output=log_output)
    print(response)


if __name__ == "__main__":
    log_output, recent_tag = read_log_file()

    if "rc" in recent_tag.split(".")[-1]:
        pass
    else:
        rel = generate_release_note(log_output)
        print(rel)
