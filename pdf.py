from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from payment import stripe_payment
from gsheet import get_gsheet_data

pdfmetrics.registerFont(TTFont('Roboto', 'sales_invoice/media/Roboto-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Roboto-Bold', 'sales_invoice/media/Roboto-Bold.ttf'))

def draw_invoice_template(c, invoice_data):
    c.translate(inch, inch)

    logo_width = 1*inch
    logo_height = 1*inch
    logo_x = -0.05*inch
    logo_y = 8.5*inch

    c.drawImage('sales_invoice/media/my_logo.png', logo_x, logo_y,
                width=logo_width, height=logo_height, mask='auto')

    info_x = logo_x + logo_width + 0.3*inch
    
    c.setFillColorRGB(0,0,0)

    c.setFont("Roboto-Bold", 16)
    c.drawString(info_x, logo_y + 0.8*inch, "How App & Web")

    c.setFont("Roboto", 14)
    c.drawString(info_x, logo_y + 0.55*inch, "1234, ABCD Road")
    c.drawString(info_x, logo_y + 0.3*inch, "Mycity, ZIP : 12345")

    c.setFillColorRGB(0,0,1)
    c.drawString(5.6*inch, 8.7*inch, 'Bill No :# 1234')

    if invoice_data and len(invoice_data[0]) > 0:
        raw_date = str(invoice_data[0][0])

        clean_date = raw_date.split(" ")[0]

        c.setFillColorRGB(0,0,1)
        c.drawString(5.6*inch, 8.5*inch, clean_date)

    row_height = 0.25 * inch
    rows_down = 5
    move_down = rows_down * row_height

    invoice_y = 8.3*inch - move_down
    line_y = 8.1*inch - move_down

    c.setFillColorRGB(1,0,0)
    c.setFont("Roboto-Bold", 40)
    c.drawString(4.3*inch, invoice_y, 'INVOICE')
    c.setFillColorRGB(0,0,0)
    c.line(0, line_y, 6.8*inch, line_y)

    shift_up = 2 * row_height  

    c.setFont("Roboto", 22)

    column_headers_y = (7.3*inch - move_down) + shift_up

    c.drawString(0.5*inch, column_headers_y, 'Products')
    c.drawString(4*inch, column_headers_y, 'Price')
    c.drawString(5*inch, column_headers_y, 'Quantity')
    c.drawString(6.1*inch, column_headers_y, 'Total')
    c.setStrokeColorCMYK(0,0,0,1)

    original_bottom = (1.9*inch - move_down)
    rows_to_shorten = 3
    new_bottom = original_bottom + (rows_to_shorten * row_height) + shift_up

    c.line(3.9*inch, column_headers_y, 3.9*inch, new_bottom)
    c.line(4.9*inch, column_headers_y, 4.9*inch, new_bottom)
    c.line(6.1*inch, column_headers_y, 6.1*inch, new_bottom)

    horizontal_line_y = new_bottom - 0.2*inch
    c.line(0.01*inch, horizontal_line_y, 7*inch, horizontal_line_y)
    total_y = horizontal_line_y - 0.25*inch

    c.setFont("Roboto-Bold", 22)
    signature_y = total_y - (3 * 0.3*inch)

    c.setFont("Roboto", 22)
    c.drawString(5.6*inch, signature_y, 'Signature')

    positions = {
        "data_start_y": column_headers_y - 0.4*inch,
        "data_row_height": 0.3*inch,
        "new_bottom": new_bottom
    }

    return c, positions



def fill_customer_info(c, invoice_data, positions):
    data_start_y = positions['data_start_y']
   
    c.setFillColorRGB(0,0,0)

    if invoice_data and len(invoice_data) > 0:
        row = invoice_data[0]

        name_str = row[1] if len(row) > 1 else ""
        address_str = row[2] if len(row) > 2 else ""
        email_str = row[3] if len(row) > 3 else ""

        y_position = data_start_y + 2*inch  

        c.setFont("Roboto-Bold", 12)
        c.drawString(0.1*inch, y_position, name_str)
        c.setFont("Roboto", 12)
        c.drawString(0.1*inch, y_position - 0.2*inch, address_str)
        c.drawString(0.1*inch, y_position - 0.4*inch, email_str)

    return c



def fill_invoice_data(c, invoice_data, positions):
    data_start_y = positions['data_start_y']
    data_row_height = positions['data_row_height']
    new_bottom = positions['new_bottom']

    c.setFont("Roboto", 12)
    c.setFillColorRGB(0,0,0)

    grand_total = 0

    for i, row in enumerate(invoice_data):
        if any(str(cell).strip() for cell in row if cell):

            y_position = data_start_y - (i * data_row_height)
            product = row[4] if len(row) > 3 else ""
            price_str = row[5] if len(row) > 4 else "0"
            quantity_str = row[6] if len(row) > 5 else "0"

            try:
                clean_price = str(price_str).replace('$', '').replace(',', '').strip()
                price = int(float(clean_price)) if clean_price else 0
            except ValueError:
                price = 0

            try:
                quantity = int(float(quantity_str)) if quantity_str else 0
            except ValueError:
                quantity = 0

            line_total = price * quantity
            grand_total += line_total

            price_display = f"${price:,.2f}" if price > 0 else ""
            quantity_display = str(quantity) if quantity > 0 else ""
            total_display = f"${line_total:,.2f}" if line_total > 0 else ""

            c.drawString(0.5*inch, y_position, str(product))
            c.drawString(4*inch, y_position, price_display)
            c.drawString(5*inch, y_position, quantity_display)
            c.drawString(6.1*inch, y_position, total_display)

    row_height = 0.25 * inch
    total_row_y = new_bottom - 0.2*inch - row_height 

    c.setFont("Roboto-Bold", 22)
    c.setFillColorRGB(0,0,0) 
    c.drawString(2*inch, total_row_y, "Total") 
    c.drawString(6.1*inch, total_row_y, f"${grand_total:,.2f}")  

    return c



my_path = 'sales_invoice/my_invoice.pdf'

c = canvas.Canvas(my_path, pagesize=letter)
invoice_data = get_gsheet_data()  
c, positions = draw_invoice_template(c, invoice_data) 
c = fill_customer_info(c, invoice_data, positions)
c = fill_invoice_data(c, invoice_data, positions)
c = stripe_payment(c)  
c.save()
