#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import sys
import time

from smtplib import SMTP, SMTP_SSL


comm = "cat /proc/uptime"
regex_patt = r"(.*) (.*)"

def get_uptime():
	l = os.popen(comm).read()
	uptime = float(re.findall(regex_patt,l)[0][0])
	return uptime

def get_uptimestamp():
	uptime = get_uptime()
	return str(int(uptime//3600)) + ":" + str("%02d"%(uptime%3600//60)) + ":" + str("%02d"%(uptime%3600%60))

if not os.path.exists("config.json"):
	print("Please, create config.json first.")
	sys.exit(0)

with open("config.json") as infile:
	config = json.load(infile)

for alert in config["alerts"]:
	if get_uptime() > alert["limit"]:
		if alert["type"] == "smtp":
			if config["smtp"]["SSL"]: smtp = SMTP_SSL(config["smtp"]["host"])
			else: smtp = SMTP(config["smtp"]["host"])
			smtp.ehlo_or_helo_if_needed()
			smtp.login(config["smtp"]["user"],config["smtp"]["pass"])
			base_params = {
				"server_name": config["general"]["server-name"],
				"uptime_seconds": int(get_uptime()),
				"uptime_stamp": get_uptimestamp(),
				"timestamp": time.strftime(config["general"]["timestamp"])
			}
			body_params = {
				"from": config["smtp"]["user"],
				"recipients": ", ".join(config["smtp"]["recipients"]),
				"subject": alert["subject"] % base_params,
				"body": alert["body"] % base_params
			}
			body = """From: %(from)s\r\nTo: %(recipients)s\r\nSubject: %(subject)s\r\n\r\n%(body)s"""%body_params
			smtp.sendmail(config["smtp"]["user"],config["smtp"]["recipients"],body)
			