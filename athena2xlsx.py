import os
import sys
import logging
import argparse
import datetime
import pytz

import xml.sax

logger = logging.getLogger(__name__)

local_tz = pytz.timezone('Europe/Stockholm')  # beware of daylight saving


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)  # .normalize might be unnecessary


class Lesson():
    """
    Class which describes a single lesson.
    """

    def __init__(self):
        self.name = ""
        self.description = ""
        self.start = ""
        self.stop = ""
        self.dt_start = None  # for datetime objects
        self.dt_stop = None
        self.room = ""
        self.teacher = ""


class StdoutWriter():
    """
    Writes lessons to standard out.

    You can pretty print with a2ps:
    athena2ics.py input.xml  | a2ps -1 -r -l144 -o output.ps
    """

    def __init__(self, lessons):
        """
        Writes lessons to standard out.
        """

        # pretty print to stdout
        iw_saved = 1
        for l in lessons:
            # print(l.start)
            iw = l.dt_start.isoweekday()
            # add a newline if new week:
            if iw < iw_saved:
                print("")
            iw_saved = iw

            if l.dt_start:
                print("{}-{} {:55} {:30} {:20}".format(l.dt_start.strftime('%Y-%m-%d %a    %H:%M'),
                                                       l.dt_stop.strftime('%H:%M'),
                                                       l.name,
                                                       l.teacher,
                                                       l.room))


class ExcelWriter():
    """
    Class for making excel files
    """

    def __init__(self, filename, lessons):
        """
        """
        import xlsxwriter

        self.wb = xlsxwriter.Workbook(filename)
        self.bold = self.wb.add_format({'bold': True})
        self.date_format = self.wb.add_format({'num_format': 'mmmm d yyyy'})
        self.ws = self.wb.add_worksheet()
        self.write_lessons(lessons)
        self.save()

    def write_lessons(self, lessons):
        """
        Write lessons to open worksheet.
        """

        row = 0
        col = 0

        col_date = col
        col_week = col + 1
        col_start = col + 2
        col_stop = col + 3
        col_name = col + 4
        col_teacher = col + 5
        col_room = col + 6

        iw_saved = 1

        self.ws.write(row, col_date, "Date", self.bold)
        self.ws.write(row, col_week, "Weekday", self.bold)
        self.ws.write(row, col_start, "Start", self.bold)
        self.ws.write(row, col_stop, "Stop", self.bold)
        self.ws.write(row, col_name, "Title", self.bold)
        self.ws.write(row, col_teacher, "Teacher", self.bold)
        self.ws.write(row, col_room, "Location", self.bold)

        row += 1

        for l in lessons:
            iw = l.dt_start.isoweekday()
            if iw < iw_saved:
                row += 1
            iw_saved = iw
            self.ws.write(row, col_date, l.dt_start.strftime('%Y-%m-%d'),  self.date_format)
            self.ws.write(row, col_week, l.dt_start.strftime('%a'))
            self.ws.write(row, col_start, l.dt_start.strftime('%H:%M'))
            self.ws.write(row, col_stop, l.dt_stop.strftime('%H:%M'))
            self.ws.write(row, col_name, l.name)
            self.ws.write(row, col_teacher, l.teacher)
            self.ws.write(row, col_room, l.room)
            row += 1

    def save(self):
        """
        """
        self.wb.close()


class PlanHandler(xml.sax.ContentHandler):
    """
    How to parse the XML file exported from Athena.
    """

    def __init__(self):
        self.CurrentData = ""
        self.skip = False
        self.lessons = []
        self.cl = None  # current lesson
        self._dt_str = '%Y-%m-%dT%H:%M:%S'  # date time string format in XML file

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "lesson":
            self.cl = Lesson()
            logger.debug("Found a new lesson")
        if tag == "custom":
            logger.debug(attributes.items())
            if "colName" in attributes:
                self.CurrentData = attributes["colName"].lower()
        if tag == "objectives":
            self.skip = True

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "objectives":
            self.skip = False
        if self.skip:
            return
        if tag == "lesson":  # end current lesson
            self.lessons.append(self.cl)
        self.CurrentData = ""

    # Call when a character is read
    def characters(self, content):
        # cl = self.lessons[-1]  # current lesson being parsed
        if self.CurrentData == "name":
            self.cl.name = content
        elif self.CurrentData == "description":
            self.cl.description = content
        elif self.CurrentData == "start":
            self.cl.start = content
            self.cl.dt_start = utc_to_local(datetime.datetime.strptime(content, self._dt_str))
            logger.debug(self.cl.dt_start.date(), self.cl.dt_start.time())
        elif self.CurrentData == "stop":
            self.cl.stop = content
            self.cl.dt_stop = utc_to_local(datetime.datetime.strptime(content, self._dt_str))
        elif self.CurrentData == "room" or self.CurrentData == "location":  # are made lower case before
            self.cl.room = content
        elif self.CurrentData == "teacher":
            self.cl.teacher = content


def main(args=sys.argv[1:]):
    """
    Main function
    """
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="input XML filename, exported from itslearning.com -> plan -> import/export",
                        type=str)
    parser.add_argument("-v", "--verbosity", action='count', help="increase output verbosity", default=0)
    parser.add_argument('-o', '--outfile', nargs='?', type=str,
                        help='output filename, if suffix is .xlsx then output as spreadsheet')

    parsed_args = parser.parse_args(args)

    if parsed_args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    elif parsed_args.verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    inp = parsed_args.infile
    oup = parsed_args.outfile
    if oup:
        oup_ext = os.path.splitext(oup)[-1].lower()
    else:
        oup_ext = ""

    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    handler = PlanHandler()
    parser.setContentHandler(handler)
    parser.parse(inp)

    # sort by date
    s = sorted(handler.lessons, key=lambda x: getattr(x, 'start'))

    if oup_ext == ".xlsx":
        ExcelWriter(oup, s)

    StdoutWriter(s)


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
