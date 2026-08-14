from db import save_log, get_logs

save_log("BC6EF306", "Cuong", "OPEN")
save_log("73D63207", "Guest", "DENY")

for log in get_logs():
    print(log)