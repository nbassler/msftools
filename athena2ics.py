import sys
import logging
import argparse
import datetime

import xml.sax

logger = logging.getLogger(__name__)


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
            self.cl.dt_start = datetime.datetime.strptime(content, self._dt_str)
            logger.debug(self.cl.dt_start.date(), self.cl.dt_start.time())
        elif self.CurrentData == "stop":
            self.cl.stop = content
            self.cl.dt_stop = datetime.datetime.strptime(content, self._dt_str)
        elif self.CurrentData == "room":
            self.cl.room = content
        elif self.CurrentData == "teacher":
            self.cl.teacher = content


def main(args=sys.argv[1:]):
    """
    Main function
    """
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("fn_input", help="input filename", type=str)
    parser.add_argument("-v", "--verbosity", action='count', help="increase output verbosity", default=0)

    parsed_args = parser.parse_args(args)

    if parsed_args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    elif parsed_args.verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    inp = parsed_args.fn_input

    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    handler = PlanHandler()
    parser.setContentHandler(handler)
    parser.parse(inp)

    # sort by date
    s = sorted(handler.lessons, key=lambda x: getattr(x, 'start'))

    # pretty print to stdout
    for l in s:
        # print(l.start)
        if l.dt_start:
            print("{}-{} {:50} {:20}".format(l.dt_start.strftime('%Y-%m-%d %a    %H:%S'),
                                             l.dt_stop.strftime('%H:%S'),
                                             l.name,
                                             l.teacher))


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
