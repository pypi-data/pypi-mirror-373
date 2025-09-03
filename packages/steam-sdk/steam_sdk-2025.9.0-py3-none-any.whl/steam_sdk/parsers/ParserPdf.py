from reportlab.lib import pagesizes
from svglib.svglib import svg2rlg
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, SimpleDocTemplate, PageBreak, Paragraph, Table


class ParserPdf:
    '''
    ParserPdf class is used to generate PDFs with images and tables.

    :param pdf_name: name of the pdf to be generated
    '''
    def __init__(self, pdf_name):
        self.pdf_name = pdf_name
        self.elements = []


    def add_table(self, data, columns_width):
        '''
        Add a table to the PDF.

        Parameters
        ----------
        data : list
            2D list representing the rows and columns of the table
        columns_width : list
            list of widths of each column in inches
        '''
        t = Table(data, colWidths=columns_width)
        self.elements.append(t)


    def add_header(self, text, level):
        """
        Add a header to the current document with the given text and level.

        Args:
            text (str): The text of the header.
            level (int): The level of the header, from 1 (highest) to 6 (lowest).
        """
        styles = getSampleStyleSheet()
        heading_style = styles[f'Heading{level}']
        heading = Paragraph(text, heading_style)
        self.elements.append(heading)

    def add_image(self, image_path: str, width: float=100, height: float=None):
        '''
        Add a png image to the PDF.

        :param image_path: path of the image to be added
        :param width: width of the image in millimeters
        :param height: height of the image in millimeters
        '''

        # Acquire image
        if image_path.endswith('.png'):
            img = Image(image_path)
        else:
            raise Exception(f'Image {image_path} has a not supported format. Supported formats: .png')

        # Change image sizes
        if width and height:
            img.drawWidth = width * mm
            img.drawHeight = height * mm
        elif width:
            img.drawHeight = img.imageHeight / img.imageWidth * (width*mm)  # keep aspect ratio
            img.drawWidth = width * mm
        elif height:
            img.drawWidth = img.imageWidth / img.imageHeight * (height*mm)  # keep aspect ratio
            img.drawHeight = height * mm

        # Add image
        self.elements.append(img)


    def add_svg_image(self, image_path: str):
        '''
            Add a svg vector graphic to the PDF.
            NOTE: with more than 300 graphics python crashes

            :param image_path: path of the image to be added
        '''
        drawing = svg2rlg(image_path)

        def scale(drawing, scaling_factor):
            """
            Scale a reportlab.graphics.shapes.Drawing()
            object while maintaining the aspect ratio
            """
            scaling_x = scaling_factor
            scaling_y = scaling_factor

            drawing.width = drawing.minWidth() * scaling_x
            drawing.height = drawing.height * scaling_y
            drawing.scale(scaling_x, scaling_y)
            return drawing

        # scale it down so that it fits on a PDF page (width of 210mm, estimated margin of 10mm per side)
        scaling_factor = 190 * mm / drawing.width - 0.05  # 5% safety margin
        drawing = scale(drawing, scaling_factor=scaling_factor)

        # Add image
        self.elements.append(drawing)



    def add_page_break(self):
        '''
        Add a page break to the document.
        '''
        if self.elements[-1] != PageBreak():  # this is to remove consecutive page breaks
            self.elements.append(PageBreak())


    # def add_pages_with_figures(self, pages_list: List[List[str]], width: float = None, height: float = None):
    #     '''
    #     Add multiple pages to the PDF with images.
    #
    #     :param pages_list: list of lists with image paths
    #     '''
    #     for page in pages_list:
    #         for img_path in page:
    #             self.add_image(img_path, width=width, height=height)
    #         if self.elements[-1] != PageBreak():
    #             self.add_page_break()


    def generate_pdf(self, text=None):
        '''
        Generate pdf with the elements added and adds text to it

        :param text: text to be added to the pdf
        '''
        pdf = SimpleDocTemplate(self.pdf_name, pagesize=pagesizes.A4)
        styles = getSampleStyleSheet()
        if text:
            self.elements.append(Paragraph(text, styles["Normal"]))
        pdf.build(self.elements)
