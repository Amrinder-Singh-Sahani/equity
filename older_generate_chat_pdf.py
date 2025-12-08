
def generate_chat_pdf(messages):
    # Initialize PDF with fpdf2
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- FONT HANDLING ---
    font_path = 'NotoSans-Regular.ttf'
    font_name = 'Helvetica' # Default fallback
    
    if os.path.exists(font_path):
        try:
            # Register the font. 

            # pdf.add_font(fname=font_path)
            # font_name = 'NotoSans-Regular' # fpdf2 usually uses the filename stem as the font name
            pdf.add_font('NotoSans', fname=font_path)
            font_name = 'NotoSans' # Set the font name to the family name
        except Exception as e:
            print(f"Font loading error: {e}")
    else:
        print(f"⚠️ Font file {font_path} not found. Using Standard Helvetica.")

    # --- HEADER ---
    # Manually adding header here since we aren't extending the class for this simple version
    pdf.set_font(font_name, size=16)
    # bold=True is only available if we have a bold font file, so we stick to regular for safety
    # pdf.cell(0, 10, "EquityTool Chat History", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.cell(0, 10, "EquityTool Chat History", align='C', ln=1)
    pdf.ln(5)

    # --- CHAT CONTENT ---
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "system":
            continue

        # Set colors and titles
        if role == "user":
            pdf.set_font(font_name, size=12)
            pdf.set_text_color(0, 0, 128) # Navy Blue
            pdf.cell(0, 7, "You:", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_text_color(0, 0, 0)   # Black
            pdf.multi_cell(0, 6, content)
            
        elif role == "assistant":
            pdf.set_font(font_name, size=12)
            pdf.set_text_color(0, 100, 0) # Dark Green
            pdf.cell(0, 7, "EquityTool:", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_text_color(0, 0, 0)   # Black
            pdf.multi_cell(0, 6, content)
            
        pdf.ln(5)

    # --- OUTPUT ---
    # fpdf2 .output() returns a bytearray directly, which is exactly what Streamlit needs
    # return bytes(pdf.output())    # not the text content. The content is handled by the font.
    return pdf.output(dest='S').encode('latin-1')



def generate_chat_pdf(messages):
    # Initialize PDF with fpdf2
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- FONT HANDLING ---
    font_path = 'NotoSans-Regular.ttf'
    font_name = 'Helvetica' # Default fallback
    
    if os.path.exists(font_path):
        try:
            # Register the font. 

            pdf.add_font(fname=font_path)
            font_name = 'NotoSans-Regular' # fpdf2 usually uses the filename stem as the font name
        except Exception as e:
            print(f"Font loading error: {e}")
    else:
        print(f"⚠️ Font file {font_path} not found. Using Standard Helvetica.")

    # --- HEADER ---
    # Manually adding header here since we aren't extending the class for this simple version
    pdf.set_font(font_name, size=16)
    # bold=True is only available if we have a bold font file, so we stick to regular for safety
    pdf.cell(0, 10, "EquityTool Chat History", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(5)

    # --- CHAT CONTENT ---
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "system":
            continue

        # Set colors and titles
        if role == "user":
            pdf.set_font(font_name, size=12)
            pdf.set_text_color(0, 0, 128) # Navy Blue
            pdf.cell(0, 7, "You:", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_text_color(0, 0, 0)   # Black
            pdf.multi_cell(0, 6, content)
            
        elif role == "assistant":
            pdf.set_font(font_name, size=12)
            pdf.set_text_color(0, 100, 0) # Dark Green
            pdf.cell(0, 7, "EquityTool:", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_text_color(0, 0, 0)   # Black
            pdf.multi_cell(0, 6, content)
            
        pdf.ln(5)

    # --- OUTPUT ---
    # fpdf2 .output() returns a bytearray directly, which is exactly what Streamlit needs
    return bytes(pdf.output())    # not the text content. The content is handled by the font.
