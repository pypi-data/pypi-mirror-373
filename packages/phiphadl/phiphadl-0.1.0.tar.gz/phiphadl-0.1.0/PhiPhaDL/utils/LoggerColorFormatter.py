import logging
import os
from datetime import datetime

class TerminalColorFormatter(logging.Formatter):
    """
    Color formatter for terminal output using ANSI escape codes
    """
    
    # ANSI color codes
    COLORS = {
        'grey': '\033[90m',      # Dark grey
        'white': '\033[97m',     # Bright white
        'debug': '\033[94m',     # Blue
        'info': '\033[92m',      # Green
        'warning': '\033[93m',   # Yellow
        'error': '\033[91m',     # Red
        'critical': '\033[95m',  # Magenta
        'reset': '\033[0m'       # Reset color
    }
    
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Split the message into components
        parts = log_message.split(' - ', 2)
        if len(parts) >= 3:
            timestamp, level, message = parts[0], parts[1], parts[2]
        else:
            return log_message  # Fallback if format doesn't match expected pattern
        
        # Apply colors
        colored_timestamp = f"{self.COLORS['grey']}{timestamp}{self.COLORS['reset']}"
        
        # Get level color
        level_lower = level.lower()
        if level_lower in self.COLORS:
            level_color = self.COLORS[level_lower]
        else:
            level_color = self.COLORS['white']  # Default color for unknown levels
        
        colored_level = f"{level_color}{level}{self.COLORS['reset']}"
        colored_message = f"{self.COLORS['white']}{message}{self.COLORS['reset']}"
        
        return f"{colored_timestamp} - {colored_level} - {colored_message}"

# [.log file] plain text format
class LogColorFormatter(logging.Formatter):
    """
    Formatter for plain text .log file output
    Creates logs in a structured text format
    """

    def __init__(self, fmt, datefmt, log_folder, log_file_name):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.log_folder = log_folder
        self.log_file_name = log_file_name
        self._initialize_log_file()

    def _initialize_log_file(self):
        """Initialize the log file with a header"""
        log_file_path = os.path.join(self.log_folder, f'{self.log_file_name}.log')
        with open(log_file_path, 'w') as f:
            f.write("Training Log\n")
            f.write("-" * 50 + "\n")
            f.write("Timestamp            Level   Message\n")
            f.write("-" * 50 + "\n")

    def format(self, record):
        """Format log record as plain text row with aligned columns"""
        # Get the original formatted message
        log_message = super().format(record)

        # Split the message into components
        parts = log_message.split(' - ', 2)
        if len(parts) >= 3:
            timestamp, level, message = parts[0], parts[1], parts[2]
            # Reformat timestamp to exclude milliseconds
            try:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f').strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            level = 'UNKNOWN'
            message = log_message

        # Format the log entry with fixed-width columns
        log_entry = f"{timestamp:<20} {level:<7} {message}\n"

        # Append to log file
        log_file_path = os.path.join(self.log_folder, f'{self.log_file_name}.log')
        with open(log_file_path, 'a') as f:
            f.write(log_entry)

        # Return empty string to prevent default logging to file
        return ''

    def close(self):
        """Close the log file by adding a footer"""
        log_footer = "-" * 50 + "\nEnd of Log\n"
        log_file_path = os.path.join(self.log_folder, f'{self.log_file_name}.log')
        with open(log_file_path, 'a') as f:
            f.write(log_footer)

# [HTML-CSS] table format
# class LogColorFormatter(logging.Formatter):
#     """
#     Color formatter for HTML file output with rich text markup
#     Creates colored logs in a structured HTML format with accompanying CSS
#     """

#     def __init__(self, fmt, log_folder, log_file_name):
#         super().__init__(fmt)
#         self.log_folder = log_folder
#         self.log_file_name = log_file_name
#         self._initialize_html_file()

#     def _initialize_html_file(self):
#         """Initialize the HTML log file with boilerplate and CSS link"""
#         html_content = """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Training Log</title>
#     <link rel="stylesheet" href="log_styles.css">
# </head>
# <body>
#     <header>
#         <h1>Training Log</h1>
#     </header>
#     <main>
#         <table class="log-table">
#             <thead>
#                 <tr>
#                     <th>Timestamp</th>
#                     <th>Level</th>
#                     <th>Message</th>
#                 </tr>
#             </thead>
#             <tbody>
# """
#         html_file_path = os.path.join(self.log_folder, f'{self.log_file_name}.html')
#         with open(html_file_path, 'w') as f:
#             f.write(html_content)

#         # Create CSS file with updated styles
#         css_content = """/* Log styles for training.html */
# @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

# body {
#     font-family: 'JetBrains Mono', monospace;
#     margin: 20px;
#     background-color: #f5f5f5;
#     font-size: 10pt; /* Fallback font size for non-table, non-h1 text */
# }

# header {
#     text-align: center;
#     margin-bottom: 20px;
# }

# h1 {
#     color: #333; /* Font size unchanged to preserve "Training Log" header size */
# }

# .log-table {
#     width: 100%;
#     border-collapse: collapse;
#     background-color: white;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     font-size: 7pt; /* Smaller font size for table headers and cells */
# }

# .log-table th,
# .log-table td {
#     padding: 6px;
#     border: 1px solid #ddd;
#     text-align: left;
# }

# .log-table th {
#     background-color: #f0f0f0;
#     font-weight: bold;
# }

# .log-table th:nth-child(1),
# .log-table td:nth-child(1) { /* Timestamp column */
#     width: 14%;
# }

# .log-table th:nth-child(2),
# .log-table td:nth-child(2) { /* Level column */
#     width: 6%;
#     font-weight: bold; /* Bold text for level column */
# }

# .log-table th:nth-child(3),
# .log-table td:nth-child(3) { /* Message column */
#     width: 80%;
# }

# .log-level-debug { color: #0000FF; }
# .log-level-info { color: #008000; }
# .log-level-warning { color: #FFA500; }
# .log-level-error { color: #FF0000; }
# .log-level-critical { color: #FF00FF; }
# .log-timestamp { color: #666; }
# .log-message { color: #000; }
# """
#         css_file_path = os.path.join(self.log_folder, 'log_styles.css')
#         with open(css_file_path, 'w') as f:
#             f.write(css_content)

#     def format(self, record):
#         """Format log record as HTML table row with colored styling"""
#         # Get the original formatted message
#         log_message = super().format(record)

#         # Split the message into components
#         parts = log_message.split(' - ', 2)
#         if len(parts) >= 3:
#             timestamp, level, message = parts[0], parts[1], parts[2]
#             # Reformat timestamp to exclude milliseconds
#             try:
#                 timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f').strftime('%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         else:
#             timestamp, level, message = datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'UNKNOWN', log_message

#         # Map log levels to CSS classes
#         level_lower = level.lower()
#         level_class_map = {
#             'debug': 'log-level-debug',
#             'info': 'log-level-info',
#             'warning': 'log-level-warning',
#             'error': 'log-level-error',
#             'critical': 'log-level-critical'
#         }
#         level_class = level_class_map.get(level_lower, 'log-level-info')

#         # Escape HTML special characters
#         def escape_html(text):
#             return (text.replace('&', '&amp;')
#                        .replace('<', '&lt;')
#                        .replace('>', '&gt;')
#                        .replace('"', '&quot;')
#                        .replace("'", '&#39;'))

#         # Create HTML table row
#         html_row = f"""                <tr>
#                     <td class="log-timestamp">{escape_html(timestamp)}</td>
#                     <td class="{level_class}">{escape_html(level)}</td>
#                     <td class="log-message">{escape_html(message)}</td>
#                 </tr>
# """
#         # Append to HTML file
#         html_file_path = os.path.join(self.log_folder, 'training.html')
#         with open(html_file_path, 'a') as f:
#             f.write(html_row)

#         # Return empty string to prevent default logging to file
#         return ''

#     def close(self):
#         """Close the HTML file by adding closing tags"""
#         html_footer = """            </tbody>
#         </table>
#     </main>
# </body>
# </html>
# """
#         html_file_path = os.path.join(self.log_folder, 'training.html')
#         with open(html_file_path, 'a') as f:
#             f.write(html_footer)

# [HTML-CSS] normal text format, no table
# class LogColorFormatter(logging.Formatter):
#     """
#     Color formatter for HTML file output with rich text markup
#     Creates colored logs in a structured HTML format with accompanying CSS using flexbox
#     """

#     def __init__(self, fmt, datefmt, log_folder, log_file_name):
#         super().__init__(fmt=fmt, datefmt=datefmt)
#         self.log_folder = log_folder
#         self.log_file_name = log_file_name
#         self._initialize_html_file()

#     def _initialize_html_file(self):
#         """Initialize the HTML log file with boilerplate and CSS link"""
#         html_content = """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Training Log</title>
#     <link rel="stylesheet" href="log_styles.css">
# </head>
# <body>
#     <header>
#         <h1>Training Log</h1>
#     </header>
#     <main>
#         <div class="log-container">
#             <div class="log-header">
#                 <div class="log-timestamp-header">Timestamp</div>
#                 <div class="log-level-header">Level</div>
#                 <div class="log-message-header">Message</div>
#             </div>
# """
#         html_file_path = os.path.join(self.log_folder, f'{self.log_file_name}.html')
#         with open(html_file_path, 'w') as f:
#             f.write(html_content)

#         # Create CSS file with updated styles using flexbox, no borders, no padding between rows
#         css_content = """/* Log styles for training.html */
# @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

# body {
#     font-family: 'JetBrains Mono', monospace;
#     margin: 20px;
#     background-color: #f5f5f5;
#     font-size: 10pt; /* Fallback font size for non-log, non-h1 text */
# }

# header {
#     text-align: center;
#     margin-bottom: 20px;
# }

# h1 {
#     color: #333; /* Font size unchanged to preserve "Training Log" header size */
# }

# .log-container {
#     width: 100%;
#     background-color: white;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     font-size: 9pt; /* Smaller font size for log entries */
# }

# .log-header, .log-row {
#     display: flex;
#     align-items: center;
# }

# .log-header {
#     background-color: #f0f0f0;
#     font-weight: bold;
#     padding: 6px 0; /* Padding only for header */
# }

# .log-timestamp-header, .log-timestamp {
#     width: 14%;
#     color: #666;
#     padding-left: 6px; /* Left padding for alignment */
# }

# .log-level-header, .log-level-info {
#     width: 6%;
#     font-weight: bold; /* Bold text for level */
#     padding-left: 6px; /* Left padding for alignment */
# }

# .log-message-header, .log-message {
#     width: 80%;
#     padding-left: 6px; /* Left padding to align with header */
# }

# .log-level-debug { color: #0000FF; }
# .log-level-info { color: #008000; }
# .log-level-warning { color: #FFA500; }
# .log-level-error { color: #FF0000; }
# .log-level-critical { color: #FF00FF; }
# .log-message { color: #000; }
# """
#         css_file_path = os.path.join(self.log_folder, 'log_styles.css')
#         with open(css_file_path, 'w') as f:
#             f.write(css_content)

#     def format(self, record):
#         """Format log record as HTML div row with colored styling"""
#         # Get the original formatted message
#         log_message = super().format(record)

#         # Split the message into components
#         parts = log_message.split(' - ', 2)
#         if len(parts) >= 3:
#             timestamp, level, message = parts[0], parts[1], parts[2]
#             # Reformat timestamp to exclude milliseconds
#             try:
#                 timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f').strftime('%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         else:
#             timestamp, level, message = datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'UNKNOWN', log_message

#         # Map log levels to CSS classes
#         level_lower = level.lower()
#         level_class_map = {
#             'debug': 'log-level-debug',
#             'info': 'log-level-info',
#             'warning': 'log-level-warning',
#             'error': 'log-level-error',
#             'critical': 'log-level-critical'
#         }
#         level_class = level_class_map.get(level_lower, 'log-level-info')

#         # Escape HTML special characters
#         def escape_html(text):
#             return (text.replace('&', '&amp;')
#                        .replace('<', '&lt;')
#                        .replace('>', '&gt;')
#                        .replace('"', '&quot;')
#                        .replace("'", '&#39;'))

#         # Create HTML div row
#         html_row = f"""            <div class="log-row">
#                 <div class="log-timestamp">{escape_html(timestamp)}</div>
#                 <div class="{level_class}">{escape_html(level)}</div>
#                 <div class="log-message">{escape_html(message)}</div>
#             </div>
# """
#         # Append to HTML file
#         html_file_path = os.path.join(self.log_folder, 'training.html')
#         with open(html_file_path, 'a') as f:
#             f.write(html_row)

#         # Return empty string to prevent default logging to file
#         return ''

#     def close(self):
#         """Close the HTML file by adding closing tags"""
#         html_footer = """        </div>
#     </main>
# </body>
# </html>
# """
#         html_file_path = os.path.join(self.log_folder, 'training.html')
#         with open(html_file_path, 'a') as f:
#             f.write(html_footer)

