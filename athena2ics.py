import sys
import logging
import argparse

import xml.sax

logger = logging.getLogger(__name__)


class Lesson():
    def __init__(self):
        self.name = ""
        self.description = ""
        self.start = ""
        self.stop = ""
        self.room = ""
        self.teacher = ""


class PlanHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.skip = False
        self.lessons = []
        self.cl = Lesson()  # current lesson

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "lesson":
            self.cl = Lesson()
            print("***** Lesson *****")
        if tag == "custom":
            print(attributes.items())
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
        # if self.CurrentData == "name":
        #     print("Name:", self.name)
        # elif self.CurrentData == "description":
        #     print("Description:", self.description)
        # elif self.CurrentData == "start":
        #     print("Start:", self.start)
        # elif self.CurrentData == "stop":
        #     print("Stop:", self.stop)
        # elif self.CurrentData == "room":
        #     print("Room:", self.room)
        # elif self.CurrentData == "teacher":
        #     print("Teacher:", self.teacher)
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
        elif self.CurrentData == "stop":
            self.cl.stop = content
        elif self.CurrentData == "room":
            self.cl.room = content
        elif self.CurrentData == "teacher":
            self.cl.teacher = content


def main(args=sys.argv[1:]):
    """ Main function
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

    print("\n\n\n")
    for l in handler.lessons:
        print(l.name)


if __name__ == '__main__':
    logging.basicConfig()
    sys.exit(main(sys.argv[1:]))
