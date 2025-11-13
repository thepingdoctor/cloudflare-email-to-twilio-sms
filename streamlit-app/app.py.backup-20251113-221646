"""
Email-to-SMS Code Generator
Streamlit application for generating Cloudflare Worker code
"""
import streamlit as st
from components import (
    render_form,
    render_preview_panel,
    show_file_stats,
    render_download_section,
    render_deployment_instructions,
    render_export_options
)
from generators import CodeGenerator
from utils import APP_TITLE, APP_SUBTITLE, APP_VERSION


# Page configuration
st.set_page_config(
    page_title="Email-to-SMS Code Generator",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        margin: 1rem 0;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = {}

    if 'current_config' not in st.session_state:
        st.session_state.current_config = None


def render_header():
    """Render application header."""
    st.markdown(f"""
    <div class="main-header">
        <h1>📧 {APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
        <small>Version {APP_VERSION}</small>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with information and actions."""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/FF6B35/FFFFFF?text=Email-to-SMS", use_column_width=True)

        st.markdown("## 🎯 Quick Guide")

        st.markdown("""
        ### Steps:
        1. **Configure** your settings
        2. **Generate** code
        3. **Download** files
        4. **Deploy** to Cloudflare

        ### Features:
        - ✅ Email-to-SMS conversion
        - ✅ Twilio integration
        - ✅ Rate limiting
        - ✅ Logging & monitoring
        - ✅ Security features
        - ✅ Automatic retries
        """)

        st.markdown("---")

        st.markdown("## 📚 Resources")
        st.markdown("""
        - [Cloudflare Workers](https://developers.cloudflare.com/workers/)
        - [Twilio SMS API](https://www.twilio.com/docs/sms)
        - [Email Routing](https://developers.cloudflare.com/email-routing/)
        - [Hono Framework](https://hono.dev/)
        """)

        st.markdown("---")

        st.markdown("## ℹ️ About")
        st.caption(f"""
        This tool generates production-ready Cloudflare Worker code
        for converting emails to SMS messages using Twilio.

        **Version:** {APP_VERSION}

        Made with ❤️ using Streamlit
        """)


def main():
    """Main application logic."""
    # Initialize
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar
    render_sidebar()

    # Main content area
    st.markdown("## ⚙️ Configuration")

    # Render configuration form
    config = render_form()

    # Store config in session state
    st.session_state.current_config = config

    # Generate button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        generate_button = st.button(
            "🚀 Generate Code",
            type="primary",
            help="Generate all Worker files based on your configuration"
        )

    # Generate code when button clicked
    if generate_button:
        with st.spinner("⚙️ Generating code..."):
            try:
                # Create code generator
                generator = CodeGenerator(config)

                # Validate configuration
                is_valid, errors = generator.validate_config()

                if not is_valid:
                    st.error("❌ Configuration validation failed:")
                    for error in errors:
                        st.error(f"  • {error}")
                else:
                    # Generate all files
                    files = generator.generate_all()

                    # Store in session state
                    st.session_state.generated_files = files

                    # Show success
                    st.success(f"✅ Successfully generated {len(files)} files!")
                    st.balloons()

            except Exception as e:
                st.error(f"❌ Error generating code: {str(e)}")
                st.exception(e)

    # Display generated code
    if st.session_state.generated_files:
        # Show file statistics
        show_file_stats(st.session_state.generated_files)

        # Show code preview
        render_preview_panel(st.session_state.generated_files)

        # Download section
        render_download_section(
            st.session_state.generated_files,
            config.basic.worker_name
        )

        # Deployment instructions
        render_deployment_instructions(
            config.basic.worker_name,
            config.basic.domain,
            config.basic.email_pattern
        )

        # Configuration export
        st.markdown("---")
        render_export_options(config)

    else:
        # Show placeholder when no code generated yet
        st.info("""
        👆 **Get started by:**
        1. Filling in your configuration above
        2. Clicking the "Generate Code" button
        3. Downloading your customized Worker files
        """)

        # Show example
        with st.expander("📖 See Example Configuration"):
            st.markdown("""
            **Example Setup:**
            - **Worker Name:** `my-email-sms`
            - **Domain:** `example.com`
            - **Email Pattern:** `*@sms.example.com`
            - **Twilio Phone:** `+15551234567`

            **This creates a worker that:**
            - Receives emails at `15551234567@sms.example.com`
            - Sends SMS to `+15551234567`
            - Includes rate limiting (10 msgs/sender/hour)
            - Logs to Analytics Engine
            - Retries failed sends up to 3 times
            """)


if __name__ == "__main__":
    main()
