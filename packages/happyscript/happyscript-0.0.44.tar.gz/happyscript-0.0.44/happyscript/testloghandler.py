
import traceback, logging


class TestLogHandler(logging.FileHandler):

    def __init__(self, filename):
        super().__init__(filename)
    
    def emit(self, record):
        
        if record.msg is None:
            return
        record.msg = record.msg.strip()
        if len(record.msg.rstrip())==0:
            return
        
        if record.exc_info and str(record.exc_info[1])!="'Stopping parent script...'":
            tb = traceback.format_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2])
            for line in tb[:-1 or None]:
                if line.startswith("Traceback "):
                    continue
                if "in execute_threadfunc" in line:
                    continue

                record.msg = record.msg + "\r\n" + line
                
            record.exc_info = None

        super().emit(record)

