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

    def print(self):
        print("Name: {}".format(self.name))
        print("Desc: {}".format(self.description))
        print("Start: {}".format(self.dt_start))
        print("Stop: {}".format(self.dt_stop))
        print("Room: {}".format(self.room))
        print("Teacher:".format(self.teacher))


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
            if l.dt_start:
                iw = l.dt_start.isoweekday()
            else:
                iw = 1
            # add a newline if new week:
            if iw < iw_saved:
                print("")
            iw_saved = iw

            if l.dt_start and l.dt_stop:  # TODO: print also if only one of these are set
                print("{}-{} {:55} {:30} {:20}".format(l.dt_start.strftime('%Y-%m-%d %a    %H:%M'),
                                                       l.dt_stop.strftime('%H:%M'),
                                                       l.name,
                                                       l.teacher,
                                                       l.room))
            else:
                print("{}-{} {:55} {:30} {:20}".format("",
                                                       "",
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

        col_week = col
        col_date = col + 1
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
            if l.dt_start:
                iw = l.dt_start.isoweekday()
            else:
                iw = 1
            if iw < iw_saved:
                row += 1
            iw_saved = iw
            if l.dt_start:
                self.ws.write(row, col_date, l.dt_start.strftime('%Y-%m-%d'),  self.date_format)
                self.ws.write(row, col_week, l.dt_start.strftime('%a'))
                self.ws.write(row, col_start, l.dt_start.strftime('%H:%M'))
            if l.dt_stop:
                self.ws.write(row, col_stop, l.dt_stop.strftime('%H:%M'))
            self.ws.write(row, col_name, l.name)
            self.ws.write(row, col_teacher, l.teacher)
            self.ws.write(row, col_room, l.room)
            row += 1

    def save(self):
        """
        """
        self.wb.close()


class IulianaWriter():
    """
    Class for making excel file in Iuliana's format and in Swedish too.
    """
    wdict = {'Mon': 'Mån',
             'Tue': 'Tis',
             'Wed': 'Ons',
             'Thu': 'Tors',
             'Fri': 'Fre',
             'Sat': 'Lör',
             'Sun': 'Sön'
             }

    def __init__(self, filename, lessons, course_name="", course_code=""):
        """
        """
        import xlsxwriter

        font_size = 12
        font_name = 'Times New Roman'

        self.wb = xlsxwriter.Workbook(filename)
        self.wb.formats[0].set_font_size(font_size)
        self.wb.formats[0].set_font_name(font_name)

        # bold text
        self.bold = self.wb.add_format({'bold': True})
        self.bold.set_font_size(font_size)
        self.bold.set_font_name(font_name)

        # fat overline
        self.oline = self.wb.add_format()
        self.oline.set_font_size(font_size)
        self.oline.set_font_name(font_name)
        self.oline.set_top(5)

        # fat overline bold
        self.obline = self.wb.add_format({'bold': True})
        self.obline.set_font_size(font_size)
        self.obline.set_font_name(font_name)
        self.obline.set_top(5)

        # normal format
        self.norm = self.wb.add_format()
        self.norm.set_font_size(font_size)
        self.norm.set_font_name(font_name)

        # header bar
        self.header = self.wb.add_format({'bold': True})
        self.header.set_bg_color('black')
        self.header.set_font_color('white')
        self.header.set_font_size(font_size)
        self.header.set_font_name(font_name)

        # self.date_format = self.wb.add_format({'num_format': 'mmmm d yyyy'})
        self.ws = self.wb.add_worksheet()
        self.cname = course_name
        self.ccode = course_code
        self.write_lessons(lessons)
        self.save()

    def write_lessons(self, lessons):
        """
        Write lessons to open worksheet.
        """

        row = 0
        col = 0

        col_dag = col
        col_datum = col + 1
        col_tid = col + 2
        col_kurs = col + 3
        col_kurskod = col + 4
        col_aktivitet = col + 5
        col_foerel = col + 6
        col_lokal = col + 7

        iw_saved = 1

        self.ws.write(row, col_dag, "Dag", self.header)
        self.ws.write(row, col_datum, "Datum", self.header)
        self.ws.write(row, col_tid, "Tid", self.header)
        self.ws.write(row, col_kurs, "Kurs", self.header)
        self.ws.write(row, col_kurskod, "Kurskod", self.header)
        self.ws.write(row, col_aktivitet, "Aktivitet", self.header)
        self.ws.write(row, col_foerel, "Föreläsere", self.header)
        self.ws.write(row, col_lokal, "Lokal", self.header)

        self.ws.set_column(col_dag, col_dag, 5)
        self.ws.set_column(col_datum, col_datum, 5)
        self.ws.set_column(col_tid, col_tid, 11)
        self.ws.set_column(col_kurs, col_kurs, 25)
        self.ws.set_column(col_kurskod, col_kurskod, 8)
        self.ws.set_column(col_aktivitet, col_aktivitet, 15)

        row += 1

        _new_day = True
        _last_day = None
        _format = self.norm
        _bformat = self.bold

        for l in lessons:
            # check if we reached a new week
            if l.dt_start:
                iw = l.dt_start.isocalendar()[1]
            else:
                iw = 1
            if iw != iw_saved:
                # we have a new week, do something
                # row += 1
                _format = self.oline
                _bformat = self.obline
            else:
                _format = self.norm
                _bformat = self.bold
            iw_saved = iw

            # check for new day:
            if _last_day:
                if l.dt_start.date() == _last_day.date():
                    _new_day = False
                else:
                    _new_day = True

            _last_day = l.dt_start

            if l.dt_start:
                # only write date, if we have a new day
                if _new_day:
                    self.ws.write(row, col_dag, IulianaWriter.wdict[l.dt_start.strftime('%a')], _format)
                    # self.ws.write(row, col_datum, l.dt_start.strftime('%d.%m'),  self.date_format)
                    self.ws.write(row, col_datum, l.dt_start.strftime('%d.%m'), _format)
                _start = l.dt_start.strftime('%H:%M')
            if l.dt_stop:
                _date = _start + "-" + l.dt_stop.strftime('%H:%M')
                self.ws.write(row, col_tid, _date, _format)

            self.ws.write(row, col_kurs, self.cname, _format)
            self.ws.write(row, col_kurskod, self.ccode, _format)

            # check if any exam is happening, and translate accordingly
            if l.name.lower() == "exam":
                self.ws.write(row, col_aktivitet, "TENTAMEN", _bformat)
                self.ws.write(row, col_foerel, "", _format)
                self.ws.write(row, col_foerel, "", _format)
            else:
                self.ws.write(row, col_aktivitet, "Föreläsning", _format)
                self.ws.write(row, col_foerel, l.teacher, _format)
                self.ws.write(row, col_foerel, "SU", _format)

            self.ws.write(row, col_lokal, "", _format)
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
    parser.add_argument("-c", "--course-code", help="Course code, e.g. FK5031", type=str)
    parser.add_argument("-n", "--course-name", help="Course name, e.g. Radiation Dosimetry", type=str)
    parser.add_argument("-i", "--iuliana-format", action='store_true',
                        help="Iuliana style formatted xlsx file")

    parsed_args = parser.parse_args(args)

    if parsed_args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    elif parsed_args.verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    cname = parsed_args.course_name
    ccode = parsed_args.course_code
    iform = parsed_args.iuliana_format

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
        if iform:
            IulianaWriter(oup, s, course_name=cname, course_code=ccode)
        else:
            ExcelWriter(oup, s)

    StdoutWriter(s)


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
