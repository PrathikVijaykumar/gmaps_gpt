import os
import markdown
import re

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from markupsafe import Markup



from prefix import SQL_PREFIX
from boilerplate import (
    building_marker_format_boilerplate,
    holding_period_boilerplate,
    javascript_map_boilerplate,
    marker_boilerplate,
    school_marker_format_boilerplate,
    two_bed_holding_period_boilerplate,
)
from tools import setup_tools

# for generating the pdf report, we receive reportlab code and execute it arbitrarily
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from flask import Response  # Import Flask Response to send the PDF directly
import io


POSTGRES_USER = os.getenv("PG_USER")
POSTGRES_PASSWORD = os.getenv("PG_PASSWORD")
POSTGRES_PORT = os.getenv("PG_PORT")
POSTGRES_DB = os.getenv("PG_DB")

#connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@ep-noisy-mountain-a5djey6c.us-east-2.aws.neon.tech/{POSTGRES_DB}?sslmode=require"

db = SQLDatabase.from_uri(connection_string)

llm = ChatOpenAI(model="gpt-4o-mini")

prefix = SQL_PREFIX.format(
    table_names=db.get_usable_table_names(),
    marker_boilerplate=marker_boilerplate,
    holding_period_boilerplate=holding_period_boilerplate,
    two_bed_holding_period_boilerplate=two_bed_holding_period_boilerplate,
    javascript_map_boilerplate=javascript_map_boilerplate,
    building_marker_format_boilerplate=building_marker_format_boilerplate,
    school_marker_format_boilerplate=school_marker_format_boilerplate,
)

system_message = SystemMessage(content=prefix)


tools = setup_tools(db, llm)

agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)

def print_sql(sql):
    print(
        """
        The SQL query is:

        {}
    """.format(sql)
    )

# setup_tools(db,llm)

def extract_and_remove_html_extract_python(text):
    # Pattern to match HTML code block
    html_pattern = r"```html\s*([\s\S]*?)\s*```" #identifies HTML code present in markup
    match = re.search(html_pattern, text, re.IGNORECASE)
    python_pattern = (
        r'<pre\s+class="codehilite"><code\s+class="language-python">(.*?)</code></pre>'
    )
    md_pattern = r"```python(.*?)```"
    python_match = re.search(python_pattern, text, re.DOTALL | re.IGNORECASE)
    md_match = re.search(md_pattern, text, re.DOTALL)
    code_match = python_match or md_match ## gpt provides python code either in general python or python wrapped in markdown 
    if code_match:
        print(text)
        code = code_match.group(1)
        code = code.replace("&quot;", '"')
        code = code.replace("&amp;", "&")
        code = code.replace("&lt;", "<")
        code = code.replace("&gt;", ">")
        code = code.replace("&#39;", "'")
        print("=== Extracted PDF Code ===")
        print(code)
        print("========================")
        
        # Check for either Canvas or SimpleDocTemplate
        if 'canvas.Canvas' in code or 'SimpleDocTemplate' in code:
            return None, process_markdown("PDF Generated!"), code
        else:
            print("Warning: No PDF generation code found")
            return None, text, None
            
        return None, process_markdown("PDF Generated!"), code
        
        #return None, "PDF Generated!", code


    if match:
        html_code = match.group(1).strip()
        # Remove the HTML code block from the original text
        text_without_html = re.sub(html_pattern, "", text, flags=re.IGNORECASE).strip()
        # Return both the extracted HTML and the text without HTML
        return Markup(html_code), process_markdown(text_without_html), None #return Markup(html_code), text_without_html, False
        #We use markup as HTML has a lot '\x' in them which can be misinterpreted by python. Thus we wrap it in markup
    return None, process_markdown(text), None#return None,text, False #if no HTML is found

def process_markdown(text):
    # Convert Markdown to HTML
    html = markdown.markdown(text, extensions=["extra", "codehilite"])
    # Wrap the result in Markup to prevent auto-escaping
    return Markup(html)

# Function to detect malicious patterns
def detect_malicious_code(code):
    # Define a list of regex patterns for dangerous functions or modules
    malicious_patterns = [
        r'import\s+(sys|subprocess|shlex|socket|ctypes|signal|multiprocessing)',  # Importing dangerous modules
        r'os\.(system|popen|remove|rmdir|rename|chmod|chown|kill|fork)',  # Dangerous os methods
        r'subprocess\.(Popen|run|call|check_output)',  # Subprocess methods
        r'eval\(',  # Use of eval()
        r'exec\(',  # Use of exec()
        r'compile\(',  # Use of compile()
        r'shutil\.(copy|move|rmtree)',  # shutil file operations
        r'socket\.',  # Use of sockets for network access
        r'requests\.',  # Use of requests library
        r'urllib\.',  # Use of urllib library
        r'getattr\(', r'setattr\(',  # Reflection
        r'globals\(', r'locals\(',  # Accessing global or local variable scopes
        r'importlib\.',  # Dynamic importing
        r'input\(',  # Use of input() for potentially malicious prompts
        r'os\.exec',  # exec family in os module
        r'ast\.(literal_eval)',  # Use of ast.literal_eval() for dynamic evaluation
    ]

    for pattern in malicious_patterns:
        if re.search(pattern, code):
            print(f"Potentially dangerous pattern detected: {pattern}")
            return True
    return False


def process_question(prompted_question, conversation_history):
    context = "\n".join(
        [
            f"Q: {entry['question']}\nA: {entry['answer']}"
            for entry in conversation_history
        ]
    )
    consolidated_prompt = f"""
    Previous conversation:
    {context}

    New question: {prompted_question}

    Please answer the new question, taking into account the context from the previous conversation if relevant.
    """
    prompt = consolidated_prompt if conversation_history else prompted_question
    content = []
    for s in agent_executor.stream({"messages":[HumanMessage(content=prompt)]}):
        for msg in s.get("agent",{}).get("messages",[]):
            for call in msg.tool_calls:
                if sql := call.get("args", {}).get("query", None): # := walrus operator. Stores the value and checks if true. No need of 2 statements
                    print(print_sql(sql))
            print(msg.content)
            html, stripped_text, py_code = extract_and_remove_html_extract_python(msg.content)
            if py_code:
                # # ----- Checking for Malicious Code
                
                # Check for malicious patterns before executing - we dont want the user to execute python that allows malicious code to be executed on system
                if not detect_malicious_code(py_code):
                    print("***********************")
                    print(py_code)
                    print("***********************")
                    # Instead of executing, return the code for Flask to handle
                    content.append(('pdf_code', py_code))
                    continue  # Skip adding stripped_text since we've handled the PDF code
                    # # ----- Checking for Malicious Code
            
            # Handle non-PDF content
            if stripped_text:
                content.append(('text', process_markdown(stripped_text)))
            if html:
                content.append(('html', html))
    return content
