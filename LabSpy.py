import sys
import time
import datetime
import logging
import logging.handlers
import sqlite3 as sql

from tentacle_pi.AM2315 import AM2315


LOG_FILENAME = "/tmp/junktest.log"
# The below could also be "DEBUG" or "WARNING"
LOG_LEVEL = logging.INFO 

#                                    #
# -- BEGIN STANDARD LOGGING BLURB -- #
#                                    #
# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler) 

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)
#                                    #
# -- END   STANDARD LOGGING BLURB -- #
#                                    #


def writeDB(pvals, fname, which="LabEnv"):
    """
    Write the values to the Lab environment SQLite3 database for playing.
    I guess it's tailored to the set of lab sensors and it's a bit 
    manual and fiddly because I'm not good with SQLite3 yet.

    Needs:
    pvals, a list of values to store that are described below
    fname, a filename of a database to store stuff
    which, a placeholder/framework for setting up different tables
    """
    try:
        con = sql.connect(fname)
        with con:
            cur = con.cursor()
            if which is "LabEnv":
                cur.execute("""
                            CREATE TABLE IF NOT EXISTS
                            LabEnvironment(RPITimestamp TEXT,
                                           Temperature REAL,
                                           Humidity REAL,
                                           CRCCheck TEXT
                                          )
                            """)
                cur.execute("""
                            INSERT INTO LabEnvironment
                            VALUES (?, ?, ?, ?)
                            """, [pvals[0], pvals[1], pvals[2], pvals[3]])
            else:
                # There are no other table/sensor groups...yet?
                pass
    except sql.Error, e:
        logger.error("Error %s:" % str(e))
    finally:
        if con:
            con.close()


def main():
    # ONLY DO THIS ONCE. 
    #  Calling it in a loop will lead to 
    #  a plague of open file handles that will
    #  crash the code silently
    try:
        # I don't know why the hell this doesn't show up in i2cdetect :-/
        am = AM2315(0x5c,"/dev/i2c-1")
    except:
        logger.error("Shit's broken!")
        sys.exit(-1)

    while True:
        now = datetime.datetime.utcnow()
        temp, humi, crc = am.sense()
        lstr = "%s %0.2f %0.2f %s" % (now, temp, humi, (crc == 1))
        # Putting this into the rotating log for now so it's easy to check on
        writeDB([now, temp, humi, (crc == 1)], 
                "CourtyardPalmdale.db", which="LabEnv")
        logger.info(lstr)
        time.sleep(5)


# The magic function that calls the main function when starting it
#  via 'python whatever.py' and without it the code won't actually start
#  and it'll return immediately to the prompt
if __name__ == "__main__":
    main()
