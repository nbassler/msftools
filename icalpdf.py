import sys
import logging
import argparse
import numpy as np
import datetime

from icalendar import Calendar

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape


logger = logging.getLogger(__name__)

def main(args=sys.argv[1:]):
    """
    Foobar
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="iCal file from which PDF schedule will be produced.", type=str)
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
    fn_out = fn_in.replace("ics", "pdf")

    with open(fn_in, 'rb') as g:
        gcal = Calendar.from_ical(g.read())

    c = canvas.Canvas(fn_out, pagesize=landscape(A4))

    margin = 50.0  # marin in points
    xmax, ymax = np.array(landscape(A4)) - margin
    xmin, ymin = np.zeros(2) + margin

    dates = []
    events = []

    for i, _c in enumerate(gcal.walk()):

        if _c.name == "VCALENDAR":
            calname = _c["X-WR-CALNAME"]
            caldesc = _c["X-WR-CALDESC"]

        if _c.name == "VEVENT":
            logger.info("")
            logger.info("{}".format(_c['summary']))
            dates.append(_c.decoded('dtstart'))
            events.append(_c)

    idxarr = np.argsort(dates)

    c.setFont('Helvetica', 20)
    c.drawString(xmin, ymax - 10, calname)

    c.setFont('Helvetica', 6)

    c.drawString(xmin + 700, ymax, "Autogenerated")
    c.drawString(xmin + 700, ymax - 8, datetime.datetime.now().strftime("%m.%d.%Y-%H:%M"))

    c.setFont('Helvetica', 12)

    # positions
    xoff_date = 0
    xoff_start_time = 75
    xoff_stop_time = 110
    xoff_location = 150
    xoff_name = 250
    xoff_desc = 550

    maxchar = 60  # maximum characters per line
    maxchar_desc = 40  # maximum characters per line

    ypos = 0
    j = 0
    for i, idx in enumerate(idxarr):
        _c = events[idx]
        _name = _c['SUMMARY']
        _start_date = _c['DTSTART'].dt.strftime("%a, %d %b")
        _start_time = _c['DTSTART'].dt.strftime("%H:%M")

        if "LOCATION" in _c:
            _location = _c['LOCATION']
        if "DTEND" in _c:
            _stop_time = _c['DTEND'].dt.strftime("%H:%M")
        else:
            _stop_time = None

        if "DESCRIPTION" in _c:
            _description = _c['DESCRIPTION']
        else:
            _description = None

        if i == 0:
            _start_date_old = _start_date

        if _start_date != _start_date_old:
            c.line(xmin, ypos-2, xmax, ypos-2)

        _start_date_old = _start_date

        ypos = ymax - 40 - (j * 14)

        if ypos < ymin:  # new page and reset counter
            c.showPage()
            j = 0
            ypos = ymax - 40 - (j * 14)

        c.drawString(xmin + xoff_date , ypos, _start_date)
        c.drawString(xmin + xoff_start_time, ypos, _start_time)
        if _stop_time:
            c.drawString(xmin + xoff_stop_time, ypos, _stop_time)
        if _location:
            c.drawString(xmin + xoff_location, ypos, _location[:3])

        if len(_name) > maxchar:
            import textwrap
            lines = textwrap.wrap(_name, maxchar)
            j -= 1
            for line in lines:
                j += 1
                ypos = ymax - 40 - (j * 14)
                c.drawString(xmin + xoff_name, ypos, line)
        else:
            c.drawString(xmin + xoff_name, ypos, _name)


        if _description:
            if len(_description) > maxchar_desc:
                import textwrap
                lines = textwrap.wrap(_description, maxchar_desc)
                j -= 1
                for line in lines:
                    j += 1
                    ypos = ymax - 40 - (j * 14)
                    c.drawString(xmin + xoff_desc, ypos, line)
        else:
            c.drawString(xmin + xoff_name, ypos, _description)

        j += 1

    j += 2  # more newlines

    for line in caldesc.split("\n"):
        ypos = ymax - 40 - (j * 14)
        c.drawString(xmin, ypos, line)

        if ypos < ymin:  # new page and reset counter
            c.showPage()
            j = 0
            ypos = ymax - 40 - (j * 14)

        j += 1
    c.save()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))