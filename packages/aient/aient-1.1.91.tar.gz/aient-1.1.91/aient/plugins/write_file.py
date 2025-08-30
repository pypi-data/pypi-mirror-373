from .registry import register_tool
from ..utils.scripts import unescape_html

import os

@register_tool()
def write_to_file(path, content, mode='w', newline=False):
    """
## write_to_file
Description: Request to write full content to a file at the specified path. If the file exists, it will be overwritten with the provided content. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file.
Parameters:
- path: (required) The path of the file to write to (relative to the current working directory ${args.cwd})
- content: (required) The content to write to the file. ALWAYS provide the COMPLETE intended content of the file, without any truncation or omissions. You MUST include ALL parts of the file, even if they haven't been modified. Do NOT include the line numbers in the content though, just the actual content of the file.
- mode: (optional) The mode to write to the file. Default is 'w'. 'w' for write, 'a' for append.
- newline: (optional) Whether to add a newline before the content. Default is False.
Usage:
<write_to_file>
<path>File path here</path>
<content>
Your file content here
</content>
<mode>w</mode>
<newline>False</newline>
</write_to_file>

Example: Requesting to write to frontend-config.json
<write_to_file>
<path>frontend-config.json</path>
<content>
{
  "apiEndpoint": "https://api.example.com",
  "theme": {
    "primaryColor": "#007bff",
    "secondaryColor": "#6c757d",
    "fontFamily": "Arial, sans-serif"
  },
  "features": {
    "darkMode": true,
    "notifications": true,
    "analytics": false
  },
  "version": "1.0.0"
}
</content>
</write_to_file>
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    if content.startswith("##") and (path.endswith(".md") or path.endswith(".txt")):
        content = "\n\n" + content

    if content.startswith("---\n") and (path.endswith(".md") or path.endswith(".txt")):
        content = "\n" + content

    if newline:
        content = '\n' + content

    # 写入文件
    try:
        with open(path, mode, encoding='utf-8') as file:
            file.write(unescape_html(content))
    except PermissionError as e:
        return f"<tool_error>写入文件失败: {e}</tool_error>"

    return f"已成功写入文件：{path}"


if __name__ == "__main__":
    text = """
&lt;!DOCTYPE html&gt;
&lt;html lang=&quot;zh-CN&quot;&gt;
&lt;head&gt;
    &lt;meta charset=&quot;UTF-8&quot;&gt;
    &lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1.0&quot;&gt;
    &lt;title&gt;Continuous Thought Machines (CTM) 原理解读&lt;/title&gt;
    &lt;script&gt;MathJax={chtml:{fontURL:'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2'}}&lt;/script&gt;
    &lt;script src=&quot;https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js&quot; id=&quot;MathJax-script&quot; async&gt;&lt;/script&gt;
    &lt;script src=&quot;https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js&quot; defer&gt;&lt;/script&gt;
    &lt;script src=&quot;https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js&quot; defer&gt;&lt;/script&gt;
    &lt;script src=&quot;https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js&quot; defer&gt;&lt;/script&gt;
    &lt;link href=&quot;https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css&quot; rel=&quot;stylesheet&quot;/&gt;
    &lt;link href=&quot;https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Fira+Code:wght@400;500&amp;display=swap&quot; rel=&quot;stylesheet&quot;&gt;
    &lt;link href=&quot;https://fonts.googleapis.com/icon?family=Material+Icons+Outlined&quot; rel=&quot;stylesheet&quot;&gt;
&lt;style&gt;
    """
    with open("test.txt", "r", encoding="utf-8") as file:
        content = file.read()
    print(write_to_file("test.txt", content))
    # python -m beswarm.aient.aient.plugins.write_file