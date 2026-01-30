import sys
from datetime import datetime

class Tee:
    def __init__(self, filename, stream=sys.stdout, add_timestamp=True):
        self.file = open(filename, "a", encoding="utf-8")
        self.stream = stream
        self.add_timestamp = add_timestamp

    def write(self, message):
        if not message:
            return

        if self.add_timestamp and message.strip():
            lines = message.splitlines(True)
            for line in lines:
                if line.strip():
                    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
                    out = f"{timestamp}{line}"
                else:
                    out = line
                self.stream.write(out)
                self.file.write(out)
        else:
            # stderr 或空行：原样输出，不加时间
            self.stream.write(message)
            self.file.write(message)

    def flush(self):
        self.stream.flush()
        self.file.flush()
        
def start_logging(filename="log/run.log"):
    # 保存原始 stdout / stderr
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    # stdout：带时间戳
    sys.stdout = Tee(filename, orig_stdout, add_timestamp=True)
    # stderr：不带时间戳
    sys.stderr = Tee(filename, orig_stderr, add_timestamp=False)

    # Python 3.7+ 可以再保证 stdout/stderr 的 UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")