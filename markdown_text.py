import re

def apply_markdown(text):
    formatted_text = []
    lines = text.split('\n')
    in_code_block = False
    
    for line in lines:
        # Code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                formatted_text.append(('code_start', line + '\n'))
            else:
                formatted_text.append(('code_end', line + '\n'))
            continue
        
        if in_code_block:
            formatted_text.append(('code', line + '\n'))
            continue
        
        # Headers
        header_match = re.match(r'^(#{1,6})\s(.+)', line)
        if header_match:
            level = len(header_match.group(1))
            formatted_text.append((f'h{level}', header_match.group(2) + '\n'))
            continue
        
        # Process inline elements
        processed_line = []
        remaining_line = line
        
        while remaining_line:
            # Links
            link_match = re.match(r'\[([^\]]+)\]\(([^\)]+)\)', remaining_line)
            if link_match:
                processed_line.append(('link', link_match.group(1)))
                remaining_line = remaining_line[link_match.end():]
                continue
            
            # Inline code
            code_match = re.match(r'`([^`]+)`', remaining_line)
            if code_match:
                processed_line.append(f'<code class="inline-code">{code_match.group(1)}</code>')
                remaining_line = remaining_line[code_match.end():]
                continue
            
            # Bold and Italic
            bold_italic_match = re.match(r'\*\*\*([^\*]+)\*\*\*', remaining_line)
            if bold_italic_match:
                processed_line.append(('bold italic', bold_italic_match.group(1)))
                remaining_line = remaining_line[bold_italic_match.end():]
                continue
            
            bold_match = re.match(r'\*\*([^\*]+)\*\*', remaining_line)
            if bold_match:
                processed_line.append(('bold', bold_match.group(1)))
                remaining_line = remaining_line[bold_match.end():]
                continue
            
            italic_match = re.match(r'\*([^\*]+)\*', remaining_line)
            if italic_match:
                processed_line.append(('italic', italic_match.group(1)))
                remaining_line = remaining_line[italic_match.end():]
                continue
            
            # Normal text
            normal_match = re.match(r'[^\[\*`]+', remaining_line)
            if normal_match:
                processed_line.append(('normal', normal_match.group(0)))
                remaining_line = remaining_line[normal_match.end():]
                continue
            
            # If no match found, add the first character as normal text
            processed_line.append(('normal', remaining_line[0]))
            remaining_line = remaining_line[1:]
        
        # Blockquotes
        if line.startswith('>'):
            formatted_text.append(('quote', line[1:].strip() + '\n'))
        else:
            formatted_text.extend(processed_line)
            if line != lines[-1]:  # Only add a newline if it's not the last line
                formatted_text.append(('normal', '\n'))
    
    return formatted_text

# Example CSS styles for code blocks and inline code
css_styles = '''
<style>
.code-block {
    background-color: #2e2e2e;
    color: #ffffff;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
    font-family: monospace;
}

.inline-code {
    background-color: #2e2e2e;
    color: #ffffff;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
}
</style>
'''