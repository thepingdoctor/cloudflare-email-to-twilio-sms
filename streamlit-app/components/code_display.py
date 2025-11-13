"""Code display and syntax highlighting components."""
import streamlit as st
from pygments import highlight
from pygments.lexers import (
    TypeScriptLexer, TOMLLexer, JsonLexer,
    MarkdownLexer, BashLexer, get_lexer_by_name
)
from pygments.formatters import HtmlFormatter
from typing import Dict


def get_lexer_for_file(filename: str):
    """
    Get appropriate Pygments lexer for file.

    Args:
        filename: Filename to determine lexer

    Returns:
        Pygments lexer
    """
    if filename.endswith('.ts'):
        return TypeScriptLexer()
    elif filename.endswith('.toml'):
        return TOMLLexer()
    elif filename.endswith('.json'):
        return JsonLexer()
    elif filename.endswith('.md'):
        return MarkdownLexer()
    elif filename.endswith('.sh'):
        return BashLexer()
    else:
        return get_lexer_by_name('text')


def syntax_highlight(code: str, filename: str) -> str:
    """
    Apply syntax highlighting to code.

    Args:
        code: Code to highlight
        filename: Filename to determine language

    Returns:
        HTML with syntax highlighting
    """
    lexer = get_lexer_for_file(filename)
    formatter = HtmlFormatter(
        style='monokai',
        noclasses=True,
        linenos='table',
        cssclass='highlight'
    )
    return highlight(code, lexer, formatter)


def render_code_tab(filename: str, code: str, show_download: bool = True):
    """
    Render a single code tab with syntax highlighting.

    Args:
        filename: Name of the file
        code: File content
        show_download: Whether to show download button
    """
    # Show file info
    st.markdown(f"**File:** `{filename}`")
    st.caption(f"📏 {len(code)} characters, {len(code.splitlines())} lines")

    # Code display with syntax highlighting
    if filename.endswith('.md'):
        # Render markdown directly
        st.markdown(code)
    else:
        # Use syntax highlighting
        st.code(code, language=get_language_name(filename), line_numbers=True)

    # Download button
    if show_download:
        st.download_button(
            label=f"⬇️ Download {filename}",
            data=code,
            file_name=filename,
            mime=get_mime_type(filename),
            key=f"download_{filename}"
        )


def get_language_name(filename: str) -> str:
    """
    Get language name for st.code.

    Args:
        filename: Filename

    Returns:
        Language identifier
    """
    if filename.endswith('.ts'):
        return 'typescript'
    elif filename.endswith('.js'):
        return 'javascript'
    elif filename.endswith('.toml'):
        return 'toml'
    elif filename.endswith('.json'):
        return 'json'
    elif filename.endswith('.md'):
        return 'markdown'
    elif filename.endswith('.sh'):
        return 'bash'
    elif filename.endswith('.yml') or filename.endswith('.yaml'):
        return 'yaml'
    else:
        return 'text'


def get_mime_type(filename: str) -> str:
    """
    Get MIME type for file.

    Args:
        filename: Filename

    Returns:
        MIME type string
    """
    if filename.endswith('.ts'):
        return 'application/typescript'
    elif filename.endswith('.js'):
        return 'application/javascript'
    elif filename.endswith('.json'):
        return 'application/json'
    elif filename.endswith('.toml'):
        return 'application/toml'
    elif filename.endswith('.md'):
        return 'text/markdown'
    elif filename.endswith('.sh'):
        return 'application/x-sh'
    else:
        return 'text/plain'


def render_code_tabs(files: Dict[str, str], worker_type: str = "standard"):
    """
    Render multiple code tabs with worker type awareness.

    Args:
        files: Dictionary mapping filenames to content
        worker_type: Type of worker ("standard" or "email")
    """
    if not files:
        st.warning("⚠️ No files generated yet. Please fill in the configuration and click 'Generate Code'.")
        return

    # Create tabs with appropriate icons based on worker type
    tab_names = list(files.keys())
    if worker_type == "email":
        tab_icons = {
            'src/index.ts': '📧',
            'src/types.ts': '🔤',
            'src/utils.ts': '🛠️',
            'wrangler.toml': '⚙️',
            'package.json': '📦',
            'tsconfig.json': '🔧',
            '.env.example': '🔐',
            '.gitignore': '🚫',
            'README.md': '📖',
            'deploy.sh': '🚀'
        }
    else:
        tab_icons = {filename: '📄' for filename in tab_names}

    tabs = st.tabs([f"{tab_icons.get(name, '📄')} {name}" for name in tab_names])

    # Render each tab
    for tab, (filename, content) in zip(tabs, files.items()):
        with tab:
            render_code_tab(filename, content)


def render_preview_panel(files: Dict[str, str]):
    """
    Render code preview panel with tabs.

    Args:
        files: Dictionary mapping filenames to content
    """
    st.markdown("---")
    st.subheader("💻 Generated Code Preview")

    if files:
        st.success(f"✅ Generated {len(files)} file(s)")
        render_code_tabs(files)
    else:
        st.info("👆 Configure your settings above and click 'Generate Code' to see the preview.")


def render_file_tree(files: Dict[str, str]):
    """
    Render visual file tree.

    Args:
        files: Dictionary mapping filenames to content
    """
    st.markdown("### 📁 File Structure")

    tree_md = "```\n"
    tree_md += "email-to-sms-worker/\n"

    # Organize files by directory
    directories = {}
    for filepath in files.keys():
        parts = filepath.split('/')
        if len(parts) > 1:
            dir_name = parts[0]
            file_name = '/'.join(parts[1:])
            if dir_name not in directories:
                directories[dir_name] = []
            directories[dir_name].append(file_name)
        else:
            if '_root_' not in directories:
                directories['_root_'] = []
            directories['_root_'].append(filepath)

    # Build tree
    for dir_name in sorted(directories.keys()):
        if dir_name == '_root_':
            for file in sorted(directories[dir_name]):
                tree_md += f"├── {file}\n"
        else:
            tree_md += f"├── {dir_name}/\n"
            for i, file in enumerate(sorted(directories[dir_name])):
                prefix = "└──" if i == len(directories[dir_name]) - 1 else "├──"
                tree_md += f"│   {prefix} {file}\n"

    tree_md += "```"
    st.markdown(tree_md)


def show_file_stats(files: Dict[str, str]):
    """
    Show statistics about generated files.

    Args:
        files: Dictionary mapping filenames to content
    """
    if not files:
        return

    total_lines = sum(len(content.splitlines()) for content in files.values())
    total_chars = sum(len(content) for content in files.values())
    total_size_kb = total_chars / 1024

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📁 Files", len(files))

    with col2:
        st.metric("📏 Lines", f"{total_lines:,}")

    with col3:
        st.metric("📊 Characters", f"{total_chars:,}")

    with col4:
        st.metric("💾 Size", f"{total_size_kb:.1f} KB")
