import time


def write_to_log(log_file, msg, print_to_console):
	if print_to_console:
		print msg
	with open(log_file, "a") as f:
		f.write(msg)
		f.close()


def write_to_requester_log(msg, print_to_console=True):
    write_to_log("requester.log", "[" + str(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())) + "]: " + str(msg), print_to_console)


def write_to_downloader_log(msg, print_to_console=True):
    write_to_log("downloader.log", "[" + str(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())) + "]: " + str(msg), print_to_console)