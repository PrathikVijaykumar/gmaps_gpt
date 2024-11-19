# app.py
import os
from uuid import uuid4

import sqlparse
from flask import Flask, render_template, request, session
from flask_cors import CORS

from main import process_question

from io import BytesIO
from flask import Flask, render_template, request, session, send_file
import re

app = Flask(__name__)


app.secret_key = os.getenv("FLASK_SECRET")

# CORS(app, resources={r"/*": {"origins": "*"}})


# def format_sql(sql):
#     return sqlparse.format(sql, reindent=True, keyword_case="upper")


MAX_CONTEXT_LENGTH = 3  # Number of previous exchanges to keep

#----------------- CHANGING THE PYTHON CODE ON FLY----------------
def extract_pdf_filename(py_code):
    """
    Extract the PDF filename from the generated code
    """
    # Look for Canvas initialization with filename
    match = re.search(r'canvas\.Canvas\(["\'](.+?\.pdf)["\']', py_code)
    if match:
        return match.group(1)
    return "generated_report.pdf"  # Default filename if not found

# def execute_pdf_code(py_code):
#     try:
#         namespace = {}
#         buffer = BytesIO()
        
#         # Import all possibly needed libraries in namespace
#         exec("""
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from io import BytesIO
# """, namespace)
        
#         # Add buffer to namespace
#         namespace['buffer'] = buffer
        
#         # Handle different types of PDF generation code
#         if 'SimpleDocTemplate' in py_code:
#             # For SimpleDocTemplate pattern, replace the document creation
#             modified_code = py_code.replace(
#                 'SimpleDocTemplate(pdf_file,',
#                 'SimpleDocTemplate(buffer,'
#             ).replace(
#                 'SimpleDocTemplate("buildings_sales_report.pdf",',
#                 'SimpleDocTemplate(buffer,'
#             )
            
#         elif 'canvas.Canvas' in py_code:
#             # For canvas.Canvas pattern, modify the function
#             if 'def' in py_code:
#                 # If there's a function definition, modify its content
#                 modified_code = re.sub(
#                     r'canvas\.Canvas\(["\'].*?\.pdf["\']',
#                     'canvas.Canvas(buffer',
#                     py_code
#                 )
#             else:
#                 # If it's direct code, wrap it in a function
#                 modified_code = """
# def generate_pdf(buffer):
#     c = canvas.Canvas(buffer, pagesize=letter)
#     """ + re.sub(
#                     r'c\s*=\s*canvas\.Canvas\(["\'].*?\.pdf["\']',
#                     'c = canvas.Canvas(buffer',
#                     py_code.split('canvas.Canvas')[1]
#                 )
#                 modified_code += "\ngenerate_pdf(buffer)"
        
#         # Remove any direct file assignments
#         modified_code = re.sub(
#             r'pdf_file\s*=\s*["\'].*?\.pdf["\']',
#             'pdf_file = ""  # Using buffer',
#             modified_code
#         )
        
#         print("=== Modified Code ===")
#         print(modified_code)
#         print("====================")
        
#         # Execute the modified code
#         exec(modified_code, namespace)
        
#         # Check buffer content
#         buffer.seek(0)
#         content = buffer.getvalue()
#         size = len(content)
#         print(f"PDF Buffer size: {size} bytes")
        
#         if size == 0:
#             print("Warning: PDF buffer is empty!")
#             return None, None
            
#         buffer.seek(0)
        
#         # Extract original filename or use default
#         filename_match = re.search(r'["\'](.+?\.pdf)["\']', py_code)
#         filename = filename_match.group(1) if filename_match else "report.pdf"
        
#         return buffer, filename
        
#     except Exception as e:
#         print(f"Error generating PDF: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return None, None

def execute_pdf_code(py_code):
    try:
        namespace = {}
        buffer = BytesIO()
        
        # Import all possibly needed libraries in namespace
        exec("""
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
""", namespace)
        
        # Add buffer to namespace
        namespace['buffer'] = buffer
        
        # Handle different types of PDF generation code
        if 'SimpleDocTemplate' in py_code:
            # First, handle any variable assignments for PDF filename
            modified_code = re.sub(
                r'(?:pdf_file|pdf_filename)\s*=\s*["\'].*?\.pdf["\']',
                'pdf_file = ""  # Using buffer',
                py_code
            )
            
            # Then handle SimpleDocTemplate creation with any filename pattern
            modified_code = re.sub(
                r'SimpleDocTemplate\(["\'].*?\.pdf["\']',
                'SimpleDocTemplate(buffer',
                modified_code
            )
            # Also handle variable-based filename
            modified_code = re.sub(
                r'SimpleDocTemplate\((pdf_file|pdf_filename)',
                'SimpleDocTemplate(buffer',
                modified_code
            )
            
        elif 'canvas.Canvas' in py_code:
            if 'def' in py_code:
                # For function-based canvas code
                modified_code = re.sub(
                    r'canvas\.Canvas\(["\'].*?\.pdf["\']',
                    'canvas.Canvas(buffer',
                    py_code
                )
                # Remove any existing function call at the end
                modified_code = re.sub(r'generate_pdf\(\)\s*$', '', modified_code)
                # Add our function call with buffer
                modified_code += "\ngenerate_pdf()"
            else:
                # For direct canvas code
                modified_code = """
def generate_pdf(buffer):
    c = canvas.Canvas(buffer, pagesize=letter)
    """ + re.sub(
                    r'c\s*=\s*canvas\.Canvas\(["\'].*?\.pdf["\']',
                    'c = canvas.Canvas(buffer',
                    py_code.split('canvas.Canvas')[1]
                )
                modified_code += "\ngenerate_pdf(buffer)"
        
        print("=== Modified Code ===")
        print(modified_code)
        print("====================")
        
        # Execute the modified code
        exec(modified_code, namespace)
        
        # Check buffer content
        buffer.seek(0)
        content = buffer.getvalue()
        size = len(content)
        print(f"PDF Buffer size: {size} bytes")
        
        if size == 0:
            print("Warning: PDF buffer is empty!")
            return None, None
            
        buffer.seek(0)
        
        # Extract original filename or use default
        filename_match = re.search(r'["\'](.+?\.pdf)["\']', py_code)
        filename = filename_match.group(1) if filename_match else "report.pdf"
        
        return buffer, filename
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None
#----------------- CHANGING THE PYTHON CODE ON FLY----------------


def get_conversation_history():
    if "conversation_history" not in session:
        session["conversation_history"] = []
    return session["conversation_history"]


def add_to_conversation_history(question, answer):
    history = get_conversation_history()
    history.append({"question": question, "answer": answer})
    if len(history) > MAX_CONTEXT_LENGTH:
        history.pop(0) ##popping the oldest conversation
    session["conversation_history"] = history

#--- PDF GENERATION & HANDLING----
@app.route("/generate-pdf")
def serve_pdf():
    try:
        py_code = session.get('latest_pdf_code')
        if not py_code:
            return "No PDF generation code found. Please generate a PDF first.", 404
        
        pdf_buffer, filename = execute_pdf_code(py_code)
        if pdf_buffer is None:
            return "Error generating PDF", 500
        
        # Ensure buffer position is at start
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error generating PDF: {str(e)}", 500
#--- PDF GENERATION & HANDLING----


@app.route("/",methods=["GET","POST"])
def index():
    result = None
    formatted_query = None
    pdf_available = False

    if "user_id" not in session:
        session["user_id"] = str(uuid4()) ## random identifier for each user
    if request.method == "POST":
        if request.form.get("sign_out", None):
            session.clear() ## if signed out, clear user's conversation
            return render_template("index.html", result=result, query=formatted_query)
        question = request.form["question"]
        conversation_history = get_conversation_history()
        # Process the question and handle PDF generation
        raw_result = process_question(question, conversation_history)
        
        # Process the result
        processed_result = []
        for item in raw_result:
            if isinstance(item, tuple):
                content_type, content = item
                if content_type == 'pdf_code':
                    session['latest_pdf_code'] = content
                    pdf_available = True
                    processed_result.append("PDF has been generated and is ready for download!")
                elif content_type == 'text':
                    processed_result.append(content)
                elif content_type == 'html':
                    processed_result.append(content)
            else:
                # Handle legacy format or direct strings
                processed_result.append(item)
        
        add_to_conversation_history(question, processed_result)
        result = processed_result
    # return render_template("index.html",result=result)
    return render_template(
        "index.html",
        gmaps_api_key=os.getenv("GPLACES_API_KEY"),
        result=result,
        query=formatted_query,
        show_pdf_button=pdf_available
    )


if __name__ == "__main__":
    app.run(debug=True)
