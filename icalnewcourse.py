import sys
import logging
import argparse
import pytz  # timezones

from icalendar import Calendar
from datetime import datetime
from datetime import timedelta


logger = logging.getLogger(__name__)

# local_tz = pytz.timezone('CET')
local_tz = pytz.timezone('Europe/Stockholm')  # beware of daylight saving


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)  # .normalize might be unnecessary


def main(args=sys.argv[1:]):
    """
    Takes an old iCal calendar file, and sets a new starting date.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="iCal .ics file from which new schedule will be produced.", type=str)
    parser.add_argument("startdate", help="New course starting date in DD.MM.YYYY format.", type=str)
    parser.add_argument("outputfile", help="Filename of output iCal .ics file.", type=str, nargs='?', default=None)
    parser.add_argument("-v", "--verbosity", action='count',
                        help="increase output verbosity",
                        default=0)
    parsed_args = parser.parse_args(args)

    if parsed_args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    elif parsed_args.verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    fn_in = parsed_args.inputfile
    if parsed_args.outputfile:
        fn_out = parsed_args.outputfile
    else:
        fn_out = "new.ics"

    if parsed_args.startdate:
        new_start_date = datetime.strptime(parsed_args.startdate, '%d.%m.%Y')
        new_start_date = new_start_date.replace(tzinfo=local_tz)
        print(new_start_date)
    else:
        new_start_date = datetime(2018, 11, 19, 9, 0, 0, tzinfo=local_tz)

    old_start_date = new_start_date

    with open(fn_in, 'rb') as g:
        gcal = Calendar.from_ical(g.read())

    # first scan for the oldest date in the calendar
    for component in gcal.walk():
        if component.name == "VEVENT":
            # print(component['summary'].dt)
            _d = component['dtstart'].dt
            if _d < old_start_date:
                old_start_date = _d

    delta = new_start_date - old_start_date
    delta = timedelta(days=delta.days + 1)
    logger.info("Last years course started {}".format(utc_to_local(old_start_date)))
    logger.info("New course will be {} days later.".format(delta.days))

    new = old_start_date + delta
    logger.info("Course start: {}".format(utc_to_local(new)))

    for component in gcal.walk():
        if component.name == "VEVENT":
            logger.info("")
            logger.info("{}".format(component['summary']))
            logger.info("Old date: {}".format(component['dtstart'].dt))
            component['dtstart'].dt += delta
            logger.info("New date: {}".format(component['dtstart'].dt))
            if "dtend" in component:
                component['dtend'].dt += delta
            component['dtstamp'].dt = datetime.now()

    with open(fn_out, 'wb') as f:
        f.write(gcal.to_ical())
    logger.info("Wrote {}".format(fn_out))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
