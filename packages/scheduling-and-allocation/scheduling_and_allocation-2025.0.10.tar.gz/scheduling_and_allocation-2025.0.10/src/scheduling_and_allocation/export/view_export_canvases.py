"""
Provides canvases for drawing views, other than the Tk canvas
"""
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime

from ..Utilities import Colour
from ..model import ResourceType

import pathlib
CODE_PATH = pathlib.Path(__file__).parent.resolve()
CWD = pathlib.Path().resolve()

# ====================================================================================================================
# Latex
# ====================================================================================================================
class LatexCanvas:
    """Doesn't 'draw' a canvas so much as uses a template and inserts latex stuff"""

    def __init__(self, title="Title", schedule_name="sub_title", filename=None, directory=None):
        """
        creates the latex file to work with
        :param title: title to be displayed
        :param schedule_name: the filename of the schedule
        :param filename: the file to save the tex file to (defaults to title, in current working directory)
        """
        if directory is None:
            directory = CWD
        if filename is None:
            filename = title.lower()
            filename = filename.replace(" ","_")
            filename = f"{directory}/{filename}.tex"

        self.filename = filename
        template_file = open(f"{CODE_PATH}/view_template.tex","r")
        self.tex = template_file.read()
        template_file.close()
        title = title.replace("_",r"\_")
        schedule_name = schedule_name.replace("_",r"\_")

        self.tex = self.tex.replace("%%USER_NAME%%", str(title))
        self.tex = self.tex.replace("%%EMAIL%%","")
        self.tex = self.tex.replace("%%PHONE_NUMBER%%","")
        self.tex = self.tex.replace("%%FILENAME%%", schedule_name)
        self.tex = self.tex.replace("%%PRINTED_DATE%%",datetime.today().strftime('%Y-%m-%d'))

        self.blocks = []


    def draw_block(self, resource_type: ResourceType, day: int, start_time: float,
                   duration: float, text:str, gui_tag, movable):
        """
        doesn't actually draw a block, but it keeps the tex info required in a list
        :param resource_type:
        :param day:
        :param start_time:
        :param duration:
        :param text:
        :param gui_tag:
        :param movable:
        """
        day_name = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        text = text.replace("\n",r" \\ ")
        self.blocks.append(
            r"\node[course={"+f"{duration}"+"}{1}] at "+fr"(\{day_name[int(day)]},{start_time}) "+"{"+text+" };"
        )

    def save(self):
        """writes the tex file"""
        self.tex = self.tex.replace("%%CLASS_TIMES%%", "\n".join(self.blocks))
        fh = open(self.filename, "w")
        fh.write(self.tex)
        fh.close()


# ====================================================================================================================
# PDF
# ====================================================================================================================
class PDFCanvas:
    """Provides a canvas for drawing a pdf"""

    def __init__(self, title="Title", schedule_name="sub_title", filename=None, directory=None):
        """
        creates a pdf canvas to draw on
        :param title: title to be displayed
        :param schedule_name: the filename of the schedule
        :param filename: the file to save the pdf file to (defaults to title, in current working directory)
        """

        if directory is None:
            directory = CWD
            
        if filename is None:
            filename = title.lower()
            filename = filename.replace(" ","_")
            filename = f"{directory}/{filename}.pdf"

        self.cn = Canvas(filename, bottomup=0, pagesize=LETTER)
        self.cn.setFont("Helvetica", 14)
        self.cn.drawCentredString(LETTER[0]/2,50, str(title))
        self.cn.setFont("Helvetica", 10)
        self.cn.drawCentredString(LETTER[0]/2,70, str(schedule_name))
        self.cn.setFont("Helvetica", 6)
        self.cn.drawCentredString(LETTER[0]/2,80, f"Printed: {datetime.today().strftime('%Y-%m-%d')}")

        self.cn.setFont("Helvetica", 8)
        self.cn.setLineWidth(0.5)
        self.cn.translate(30,100)

    def config(self,*args, **kwargs):
        pass

    def create_line(self, x1:float, y1:float, x2:float, y2:float, fill:str="grey", dash="", tags: str|tuple=""):
        """draws a line"""
        if dash == "-":
            self.cn.setDash([6,3])
        elif dash == ".":
            self.cn.setDash([1,2])
        r,g,b = Colour.rgb(fill)
        self.cn.setFillColorRGB(r,g,b)
        self.cn.line(x1,y1,x2,y2)

    def addtag_withtag(self,*args,**kwargs):
        """not needed for this canvas"""
        pass

    def create_text(self, x:float, y:float, text:str="", fill:str='black', tags:str|tuple="")->int:
        """
        draws the text, centered on x/y
        :param x:
        :param y:
        :param text:
        :param fill:
        :param tags: not used
        """
        r,g,b = Colour.rgb("black")
        self.cn.setFillColorRGB(r,g,b)
        lines = text.split("\n")
        baseline = 10
        y = y - (len(lines)-1)*baseline/2
        for t in text.split("\n"):
            self.cn.drawCentredString(x,y,t)
            y = y+10
        return 1

    def create_rectangle(self, coords:tuple[float,float,float,float], fill:str='grey', outline:str='grey',
                                        tags:str|tuple="")->int:
        """
        creates a rectangle with bounding coordinates
        :param coords:
        :param fill:
        :param outline:
        :param tags: (not used)
        """

        r,g,b = Colour.rgb(outline)
        self.cn.setStrokeColorRGB(r,g,b)
        r,g,b = Colour.rgb(fill)
        self.cn.setFillColorRGB(r,g,b)
        x1,y1,x2,y2 = coords
        self.cn.rect(min(x1,x2),min(y1,y2),abs(x2-x1), abs(y2-y1), fill=1)

        return 1

    def save(self):
        """save the pdf"""
        self.cn.save()

