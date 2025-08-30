#!/usr/bin/python

import os
import sys
import typing

#import jk_typing
#import jk_utils
import jk_sysinfo
import jk_argparsing
import jk_argparsing.textmodel





def getAllProcessNames(bVerbose:bool = False) -> typing.List[str]:
	if bVerbose:
		print(f"NOTICE: Scanning for processes ...")

	allProcesses = {}
	for p in jk_sysinfo.get_ps():
		allProcesses[p["pid"]] = p

	currentPID = os.getpid()
	processNames:typing.List[str] = []

	while True:
		procInfo = allProcesses.get(currentPID)
		if procInfo is None:
			if bVerbose:
				print(f"NOTICE:     Process with PID {currentPID} not found => stopping search")
			break
		cmd = procInfo["cmd"]
		if cmd:
			if cmd.endswith(":"):
				cmd = cmd[:-1]
			if cmd:
				if bVerbose:
					print(f"NOTICE:     Process found: {cmd}")
				processNames.append(cmd)

		currentPID = allProcesses[currentPID].get("ppid")
		if not currentPID:
			if bVerbose:
				print(f"NOTICE:     No parent process for PID {currentPID} => stopping search")
			break

	return processNames
#





def main():
	ap = jk_argparsing.ArgsParser(os.path.basename(__file__), "Checks if a specified program is a parent of the current process.")

	ap.optionDataDefaults.set("help", False)
	ap.optionDataDefaults.set("list", False)
	ap.optionDataDefaults.set("cmd_check", None)
	ap.optionDataDefaults.set("verbose", False)

	ap.createOption("h", "help", "Display this help text.").onOption = \
		lambda argOption, argOptionArguments, parsedArgs: \
			parsedArgs.optionData.set("help", True)
	ap.createOption("v", "verbose", "Verbose output (for testing --check).").onOption = \
		lambda argOption, argOptionArguments, parsedArgs: \
			parsedArgs.optionData.set("verbose", True)
	ap.createOption("l", "list", "List all parent process names.").onOption = \
		lambda argOption, argOptionArguments, parsedArgs: \
			parsedArgs.optionData.set("list", True)
	ap.createOption("c", "check", "Check if the specified process name is part of the parent process names. " \
		"Use --verbose for a test run.").expectString("cmd", minLength=1).onOption = \
		lambda argOption, argOptionArguments, parsedArgs: \
			parsedArgs.optionData.set("cmd_check", argOptionArguments[0])

	ap.createAuthor("Jürgen Knauth", "pubsrc@binary-overflow.de")

	ap.setLicense("Apache")

	ap.createReturnCode(0, "Everything is okay.")
	ap.createReturnCode(1, "Something went wrong.")
	ap.createReturnCode(2, "The help text has been displayed.")

	ap.addDescriptionChapter(None, [
		"This program can be used to check if the current process tree contains a specific type of process.",
		"Of course, there is only a very limited range of uses for this tool. Of application would be to use it within bash initialization to determine if a user logged in via ssh. "
		+ "Here is an example of how this could be done in principle:",
		"if jkcheckpproc.py -c bash; then echo \"bash is parent\"; else echo \"no, bash is not parent\"; fi",
	])

	parsedArgs = ap.parse()

	bVerbose = parsedArgs.optionData["verbose"]

	# ----

	if parsedArgs.optionData["list"]:
		for processName in getAllProcessNames():
			print(processName)
		sys.exit(0)

	# ----

	if parsedArgs.optionData["cmd_check"] is not None:
		bResult = False
		sCheck = parsedArgs.optionData["cmd_check"]
		if "/" not in sCheck:
			sCheck2 = "/" + sCheck
		else:
			sCheck2 = None
		processNames = getAllProcessNames(bVerbose = bVerbose)

		for processName in processNames:
			if processName == sCheck:
				bResult = True
				break
			if sCheck2 and processName.endswith(sCheck2):
				bResult = True
				break

		exitCode = 0
		if bResult:
			exitCode = 0
			if bVerbose:
				print(f"NOTICE: Parent process found matching {sCheck!r} => exiting with {exitCode}")
		else:
			exitCode = 1
			if bVerbose:
				print(f"NOTICE: No parent process found matching {sCheck!r} => exiting with {exitCode}")
		sys.exit(exitCode)

	# ----

	ap.showHelp()
	sys.exit(1)
#













