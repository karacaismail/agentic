"""Extract word geometry using the already bundled PDF runtime."""

import sys
import xml.etree.ElementTree as ET

import pdfplumber


def main():
    root = ET.Element("html", xmlns="http://www.w3.org/1999/xhtml")
    with pdfplumber.open(sys.argv[1]) as pdf:
        for page in pdf.pages:
            output = ET.SubElement(root, "page", width=str(page.width), height=str(page.height))
            line = None
            last_top = None
            for word in page.extract_words():
                if last_top is None or abs(word["top"] - last_top) > 2:
                    line = ET.SubElement(output, "line")
                last_top = word["top"]
                element = ET.SubElement(line, "word", xMin=str(word["x0"]),
                                        yMin=str(word["top"]), xMax=str(word["x1"]),
                                        yMax=str(word["bottom"]))
                element.text = word["text"]
    ET.ElementTree(root).write(sys.argv[2], encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
