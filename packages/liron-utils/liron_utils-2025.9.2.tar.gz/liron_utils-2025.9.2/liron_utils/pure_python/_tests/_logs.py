from liron_utils.pure_python import Logger

with Logger(
		min_level_file=Logger.NAME2LEVEL.INFO,
		min_level_console=Logger.NAME2LEVEL.DEBUG) as logger:
	logger.debug("This is a debug message. It will be printed to the console, but not to the log file.")
	logger.info("This is an info message.")
	logger.warning("This is a warning message.")
	logger.error("This is an error message.")
	logger.critical("This is a critical message.")

	x = 1 / 0  # This will raise a ZeroDivisionError and be automatically logged as an error
