import logging
import sys
from blackduck.HubRestApi import HubInstance

# FIXME: set up logging for this module only
logging.basicConfig(format='[blackduck_results]%(asctime)s:%(levelname)s:%(message)s', stream=sys.stderr, level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
