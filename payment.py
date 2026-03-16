from reportlab.lib.units import inch
from reportlab.lib.colors import red

def stripe_payment(c):

    stripe_url = "https://buy.stripe.com/test_28EeVdecq3ME7n92OvgMw05"

    x = 2.8 * inch
    y = 0.5 * inch
    width = 2 * inch
    height = 0.5 * inch
    
    rect = (x, y, x + width, y + height)
    c.setFillColor(red)
    
    c.setFont("Roboto-Bold", 14)

    offset_x = -69   
    offset_y = -76    

    text_x = x + width/2 + offset_x
    text_y = y + height/2 + offset_y
    text = "Pay Now"
    c.drawCentredString(text_x, text_y, text)

    c.linkURL(
        stripe_url,
        rect,
        relative=0,
        thickness=2,
        color=red
    )

    return c
