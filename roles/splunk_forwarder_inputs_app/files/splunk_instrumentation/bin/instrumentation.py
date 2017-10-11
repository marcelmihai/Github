# scripted inputs entry point

import os
import sys
import argparse
import datetime
import splunk_instrumentation.datetime_util as datetime_util
from time import sleep

'''
This must happen before splunk_instrumentation.constants is imported.
'''
parser = argparse.ArgumentParser()
parser.add_argument('--scheme', action='store_true')
parser.add_argument('-v', '--validate-arguments', action='store_true')
parser.add_argument('--no-collect', action='store_true', help='will not collect and index data')
parser.add_argument('--no-send', action='store_true', help='will not query _telemetry and send data')
parser.add_argument('-m', '--mode', default="INPUT", help='is required if not running from splund modular inputs')
parser.add_argument('--test-schema')
parser.add_argument('--log-level')
parser.add_argument('--execution-id')
parser.add_argument('--quickdraw-url', help='used to override the quickdraw-url')
parser.add_argument('--default-quickdraw', help='used to override the quickdraw-url response')
parser.add_argument('--start-date', help='first date to query, in YYYY-MM-DD format (defaults to yesterday)')
parser.add_argument('--stop-date', help='last date to query, in YYY-MM-DD format (inclusive) (defaults to yesterday)')
args = parser.parse_args()


# configuation is done through environmental variables. Convert command line to environmental.

if args.mode:
    os.environ['INST_MODE'] = args.mode
if args.no_collect:
    os.environ['INST_NO_COLLECT'] = args.no_collect
if args.no_send:
    os.environ['INST_NO_SEND'] = args.no_send
if args.test_schema:
    os.environ['INST_TEST_SCHEMA'] = args.test_schema
if args.log_level:
    os.environ['INST_DEBUG_LEVEL'] = args.log_level
if args.execution_id:
    os.environ['INST_EXECUTION_ID'] = args.execution_id
if args.quickdraw_url:
    os.environ['QUICKDRAW_URL'] = args.quickdraw_url
if args.default_quickdraw:
    os.environ['DEFAULT_QUICKDRAW'] = args.default_quickdraw


# Routine to get the value of an input token
def get_key():
    # read everything from stdin
    config_str = sys.stdin.read()
    # stdin is just a token
    os.environ['INST_TOKEN'] = config_str.rstrip()

# the default mode is INPUT and is what scripted inputs uses and implies
# there is a token passed in to stdin.
if os.environ['INST_MODE'] == "INPUT":
    get_key()

# these imports inlude splunk_instrumentation.constants which need to be imported after environmental vars are set
try:
    from splunk_instrumentation.input import run_input
    from splunk_instrumentation.constants import INST_PRE_EXECUTE_SLEEP
except:
    raise(Exception("COULD NOT IMPORT MODULE"))


def normalize_date_range_params(args):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    args.start_date = datetime_util.str_to_date(args.start_date) if args.start_date else yesterday
    args.stop_date = datetime_util.str_to_date(args.stop_date) if args.stop_date else yesterday


def validate_date_range(args):
    if args.stop_date < args.start_date:
        raise Exception("Start date must be >= stop date")


# Routine to index data
def main():
    sleep(INST_PRE_EXECUTE_SLEEP)

    normalize_date_range_params(args)
    validate_date_range(args)

    run_input({'start': args.start_date, 'stop': args.stop_date})


# Script must implement these args: scheme, validate-arguments
main()

sys.exit(0)
