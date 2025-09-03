from codemie_tools.base.models import ToolMetadata

FILE_ANALYSIS_TOOL = ToolMetadata(
    name="file_analysis",
    description="""
    Use this tool to read the content of files and convert it into markdown format. 
    It supports various file types such as plain text files, Word documents, and HTML, zip archives, etc.
    This tool ensures that content is structured and easy to read with markdown syntax. 
    Do not use this tool for PDFs, PowerPoint presentations (PPTX), Excel files (XLS/XLSX), or CSV files, 
    as separate tools handle those formats. Call this tool when tasks involve reading and analyzing file content or 
    extracting information in a structured, markdown-friendly format. The output will include elements like headers, 
    lists, tables, and more, converted into an easy-to-read markdown style. Useful for tasks like summarization, 
    knowledge extraction, or reasoning based on file input.
    """,
    label="File Analysis",
)

PPTX_TOOL = ToolMetadata(
    name="pptx_tool",
    description="""
    Use this tool to extract content from PowerPoint presentation files (PPTX). The tool parses slide data, including 
    text, titles, bullet points, and other slide content. Ideal for tasks requiring analysis, summarization, or 
    question-answering based on the content of PPTX slides. This tool enables processing of multi-slide presentations 
    with structured output for each slide, making the content easier to interpret and utilize in further 
    reasoning tasks
    """,
    label="PPTX Processing Tool",
)

PDF_TOOL = ToolMetadata(
    name="pdf_tool",
    description="""
    A specialized tool for extracting content from PDF documents. This tool supports text extraction from both the 
    main document and embedded elements such as tables and images. Additionally, it leverages LLM-based image 
    recognition to extract text from embedded images within PDFs. This is useful for processing scanned documents, 
    extracting knowledge from PDF reports, or summarizing document content. Use this tool when dealing with any PDF 
    file requiring text-based or image-based information retrieval
    """,
    label="PDF Processing Tool",
)

CSV_TOOL = ToolMetadata(
    name="csv_tool",
    description="""
    Tool for interpreting and working with tabular data inside CSV files. This tool allows for 
    structured data handling, such as column-based querying, applying filters, aggregations, and analysis of numeric or 
    textual data. Use this tool when tasks involve extracting insights or calculations from CSV datasets, or when 
    reasoning over structured tabular data is required.
    """,
    label="CSV Interpretation",
)

EXCEL_TOOL = ToolMetadata(
    name="excel_tool",
    description="""
    Use this tool to extract and analyze content from Excel files (XLS, XLSX). The tool processes spreadsheet data,
    converting it into readable markdown tables. It can handle multiple sheets and filter out empty rows and columns
    for better readability. Ideal for tasks requiring analysis, data extraction, or question-answering based on
    tabular data in Excel format.

    Key capabilities:
    - Process all sheets or specify sheets by name using the `sheet_names` parameter
    - Get a list of all sheet names in an Excel file with `get_sheet_names=True`
    - Access a specific sheet by its index (0-based) using `sheet_index` parameter
    - Get comprehensive statistics about the Excel file with `get_stats=True` (includes sheet counts, column names, data types, sample values)
    - Control sheet visibility with `visible_only=True/False` parameter to include or exclude hidden sheets
    - Automatically normalize column names for better readability
    - Process multiple Excel files with clear separation between documents
    - Intelligent data cleaning to remove empty rows and columns
    """,
    label="Excel Processing Tool",
)
