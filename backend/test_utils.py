"""
Test utilities for AI Model Evaluation Platform.
"""

import os
import csv
import random
from io import StringIO
import tempfile


def generate_valid_csv(num_rows=10, num_cols=5, include_header=True):
    """
    Generate a valid CSV file with random data
    
    Args:
        num_rows: Number of data rows to generate
        num_cols: Number of columns to generate
        include_header: Whether to include a header row
        
    Returns:
        String containing CSV content
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Create header if requested
    if include_header:
        header = [f"column_{i}" for i in range(num_cols)]
        writer.writerow(header)
    
    # Generate random data rows
    for _ in range(num_rows):
        row = []
        for j in range(num_cols):
            # Generate different types of data
            if j % 4 == 0:
                # Integer
                row.append(str(random.randint(1, 1000)))
            elif j % 4 == 1:
                # Float
                row.append(str(random.random() * 100))
            elif j % 4 == 2:
                # String without commas
                row.append(f"value_{random.randint(1, 100)}")
            else:
                # String that would need quoting
                row.append(f"complex, value {random.randint(1, 100)}")
        writer.writerow(row)
    
    return output.getvalue()


def generate_invalid_csv_with_issues(issue_type="column_mismatch"):
    """
    Generate an invalid CSV file with specific issues
    
    Args:
        issue_type: Type of issue to introduce:
            - column_mismatch: Different number of columns in rows
            - quoting_issue: Unquoted fields with commas
            - mixed_line_endings: Mixed line ending types
            - null_chars: Include null characters
            - invalid_encoding: Non-UTF8 characters
            
    Returns:
        Bytes containing the invalid CSV content
    """
    base_content = "header1,header2,header3,header4\n"
    
    if issue_type == "column_mismatch":
        # One row has too many columns, another has too few
        content = base_content
        content += "value1,value2,value3,value4\n"
        content += "value1,value2,value3,value4,extra_value\n"  # Extra column
        content += "value1,value2,value3\n"  # Missing column
        content += "value1,value2,value3,value4"
    
    elif issue_type == "quoting_issue":
        # Contains unquoted commas in fields
        content = base_content
        content += "value1,This has a comma, in it,value3,value4\n"
        content += "value1,value2,Another, comma here,value4"
    
    elif issue_type == "mixed_line_endings":
        # Mix of Windows and Unix line endings
        content = base_content
        content += "value1,value2,value3,value4\r\n"
        content += "value1,value2,value3,value4\n"
        content += "value1,value2,value3,value4\r\n"
        content += "value1,value2,value3,value4"
    
    elif issue_type == "null_chars":
        # Include null bytes (which will cause parsing issues)
        content = base_content
        content += "value1,value2,value3,value4\n"
        content += f"value1,value{chr(0)}2,value3,value4\n"
        content += "value1,value2,value3,value4"
    
    elif issue_type == "invalid_encoding":
        # Add non-UTF8 characters
        content = base_content
        content += "value1,value2,value3,value4\n"
        content += "value1,valué2,值3,value4\n"  # Non-ASCII unicode 
        content += "value1,value2,value3,value4"
    else:
        content = base_content
        content += "value1,value2,value3,value4\n"
        content += "value1,value2,value3,value4"
    
    # Return as bytes
    return content.encode("utf-8")


def create_test_csv_file(content, filename="test.csv"):
    """
    Create a temporary CSV file with the given content
    
    Args:
        content: String or bytes content to write to file
        filename: Name of the file
        
    Returns:
        Path to the created file
    """
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    # Convert to bytes if needed
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path 