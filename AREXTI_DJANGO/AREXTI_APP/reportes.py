from decimal import Decimal
# from lxml import etree, objectify

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

''' the XML document and return an lxml XML document
		"""
########################################################################
class PDFOrder(object):
	""""""

	# ----------------------------------------------------------------------
	def __init__(self, xml_file, pdf_file):
		"""Constructor"""
		self.xml_file = xml_file
		self.pdf_file = pdf_file

		self.xml_obj = self.getXMLObject()

	# ----------------------------------------------------------------------
	def coord(self, x, y, unit=1):
		"""
		# http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
		Helper class to help position flowables in Canvas objects
		"""
		x, y = x * unit, self.height - y * unit
		return x, y

	# ----------------------------------------------------------------------
	def createPDF(self):
		"""
		Create a PDF based on the XML data
		"""
		self.canvas = canvas.Canvas(self.pdf_file, pagesize=letter)
		width, self.height = letter
		styles = getSampleStyleSheet()
		xml = self.xml_obj

		address = """ <font size="9">
        SHIP TO:<br/>
        <br/>
        %s<br/>
        %s<br/>
        %s<br/>
        %s<br/>
        </font>
        """ % (xml.address1, xml.address2, xml.address3, xml.address4)
		p = Paragraph(address, styles["Normal"])
		p.wrapOn(self.canvas, width, self.height)
		p.drawOn(self.canvas, *self.coord(18, 40, mm))

		order_number = '<font size="14"><b>Order #%s </b></font>' % xml.order_number
		p = Paragraph(order_number, styles["Normal"])
		p.wrapOn(self.canvas, width, self.height)
		p.drawOn(self.canvas, *self.coord(18, 50, mm))

		data = []
		data.append(["Item ID", "Name", "Price", "Quantity", "Total"])
		grand_total = 0
		for item in xml.order_items.iterchildren():
			row = []
			row.append(item.id)
			row.append(item.name)
			row.append(item.price)
			row.append(item.quantity)
			total = Decimal(str(item.price)) * Decimal(str(item.quantity))
			row.append(str(total))
			grand_total += total
			data.append(row)
		data.append(["", "", "", "Grand Total:", grand_total])
		t = Table(data, 1.5 * inch)
		t.setStyle(TableStyle([
			('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
			('BOX', (0, 0), (-1, -1), 0.25, colors.black)
		]))
		t.wrapOn(self.canvas, width, self.height)
		t.drawOn(self.canvas, *self.coord(18, 85, mm))

		txt = "Thank you for your business!"
		p = Paragraph(txt, styles["Normal"])
		p.wrapOn(self.canvas, width, self.height)
		p.drawOn(self.canvas, *self.coord(18, 95, mm))

	# ----------------------------------------------------------------------
	def getXMLObject(self):
		"""
		Open
		with open(self.xml_file) as f:
			xml = f.read()
		return objectify.fromstring(xml)

	# ----------------------------------------------------------------------
	def savePDF(self):
		"""
		Save the PDF to disk
		"""

		self.canvas.save()


# ----------------------------------------------------------------------
if __name__ == "__main__":
	src_path = "C:/Users/javier/Desktop/Python/Reportes/"
	xml = "venv/templates/export_template.xml"
	pdf = src_path + "letter.pdf"
	doc = PDFOrder(xml, pdf)
	doc.createPDF()
	doc.savePDF()
'''


src_path = "C:/Users/javier/Desktop/Python/Reportes/"
src_path = "C:/Users/Mariano-Dell/Desktop/Tesis/"

pdf = src_path + "reporte_histograma.pdf"
archivo_imagen = 'C:/Users/Mariano-Dell/Desktop/Tesis/Logo2.png'


header_data = [{'cant_imagenes': '1000'},
        {'palabra_buscada':'droga'},
        {'cant_ocurrencia':'7'}]

canvas = canvas.Canvas(pdf, pagesize=letter)
width, height = letter
rightMargin = 72
leftMargin = 72
topMargin = 72
bottomMargin = 72

#header
styles = getSampleStyleSheet()
header = Paragraph('Reporte ocurrencia de palabra'*5, styles['Normal'])
w, h = header.wrap(width, topMargin)
header.drawOn(canvas, leftMargin, 400, rightMargin)

# Footer
footer = Paragraph('This is a multi-line footer.  It goes on every page.   ' * 5, styles['Normal'])
w, h = footer.wrap(width, bottomMargin)
footer.drawOn(canvas, leftMargin, h)

#se agrega el logo (x: posicion horizontal, y: posicion vertical ambas comenzando desde abajo a la izquierda de la hoja del reporte)
canvas.drawImage(archivo_imagen, 20, 700, 120, 90, preserveAspectRatio=True)


canvas.save()