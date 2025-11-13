"""Download and file management components."""
import streamlit as st
import zipfile
import io
from typing import Dict
from datetime import datetime


def create_zip_archive(files: Dict[str, str], worker_name: str) -> bytes:
    """
    Create ZIP archive with all generated files.

    Args:
        files: Dictionary mapping filenames to content
        worker_name: Worker name for ZIP filename

    Returns:
        ZIP file as bytes
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add all files to ZIP
        for filepath, content in files.items():
            # Create proper path structure
            zip_path = f"{worker_name}/{filepath}"
            zip_file.writestr(zip_path, content)

    return zip_buffer.getvalue()


def render_download_section(files: Dict[str, str], worker_name: str):
    """
    Render download section with various download options.

    Args:
        files: Dictionary mapping filenames to content
        worker_name: Worker name
    """
    if not files:
        return

    st.markdown("---")
    st.subheader("⬇️ Download & Deploy")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Download as ZIP
        zip_data = create_zip_archive(files, worker_name)
        st.download_button(
            label="📦 Download All Files (.zip)",
            data=zip_data,
            file_name=f"{worker_name}.zip",
            mime="application/zip",
            help="Download all files as a ZIP archive",
            use_container_width=True
        )

    with col2:
        # Download individual files
        st.button(
            "📄 Download Individual Files",
            help="Downloads are available in each code tab above",
            disabled=True,
            use_container_width=True
        )

    with col3:
        # Export configuration
        config_json = export_configuration(files)
        st.download_button(
            label="⚙️ Export Configuration",
            data=config_json,
            file_name=f"{worker_name}-config.json",
            mime="application/json",
            help="Save configuration for later reuse",
            use_container_width=True
        )


def export_configuration(files: Dict[str, str]) -> str:
    """
    Export configuration as JSON.

    Args:
        files: Dictionary mapping filenames to content

    Returns:
        JSON string of configuration
    """
    import json

    # Extract config from session state
    config = {
        "worker_name": st.session_state.get('worker_name', ''),
        "domain": st.session_state.get('domain', ''),
        "email_pattern": st.session_state.get('email_pattern', ''),
        "generated_at": datetime.utcnow().isoformat() + 'Z'
    }

    return json.dumps(config, indent=2)


def render_deployment_instructions(worker_name: str, domain: str, email_pattern: str):
    """
    Render deployment instructions.

    Args:
        worker_name: Worker name
        domain: Domain name
        email_pattern: Email pattern
    """
    st.markdown("---")
    st.subheader("🚀 Deployment Instructions")

    with st.expander("📖 Quick Start Guide", expanded=True):
        st.markdown(f"""
### 1. Extract Files

```bash
unzip {worker_name}.zip
cd {worker_name}
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Secrets

```bash
wrangler secret put TWILIO_ACCOUNT_SID
wrangler secret put TWILIO_AUTH_TOKEN
wrangler secret put TWILIO_PHONE_NUMBER
```

### 4. Deploy to Cloudflare

```bash
npm run deploy
```

### 5. Configure Email Routing

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Email** → **Email Routing**
3. Add domain: `{domain}`
4. Create routing rule:
   - **Match:** `{email_pattern.replace('{domain}', domain)}`
   - **Action:** Send to Worker
   - **Worker:** `{worker_name}`

### 6. Test

Send a test email to: `{email_pattern.replace('{domain}', domain).replace('*', '15551234567')}`

### Troubleshooting

- **Not receiving SMS?** Check `wrangler tail` for logs
- **Email not routing?** Verify Email Routing configuration
- **Errors?** Check Twilio credentials are set correctly
        """)

    with st.expander("🔧 Advanced Configuration"):
        st.markdown("""
### Local Development

```bash
npm run dev
```

### Type Checking

```bash
npm run check
```

### Testing

```bash
npm test
```

### View Logs

```bash
wrangler tail
```

### Update Secrets

```bash
wrangler secret put SECRET_NAME
```

### Create KV Namespace (if using rate limiting)

```bash
wrangler kv:namespace create "RATE_LIMIT_KV"
# Update wrangler.toml with the namespace ID
```
        """)


def render_copy_buttons(files: Dict[str, str]):
    """
    Render copy-to-clipboard functionality.

    Args:
        files: Dictionary mapping filenames to content
    """
    st.markdown("### 📋 Quick Copy")

    # Create columns for quick copy buttons
    cols = st.columns(min(len(files), 4))

    for i, (filename, content) in enumerate(files.items()):
        with cols[i % 4]:
            st.button(
                f"Copy {filename}",
                key=f"copy_{filename}",
                help=f"Copy {filename} to clipboard",
                use_container_width=True
            )


def render_export_options(config):
    """
    Render configuration export options.

    Args:
        config: WorkerConfig object
    """
    st.markdown("### 💾 Save Configuration")

    col1, col2 = st.columns(2)

    with col1:
        # Export as JSON
        config_json = config.to_dict()
        import json
        json_str = json.dumps(config_json, indent=2)

        st.download_button(
            label="📥 Export as JSON",
            data=json_str,
            file_name=f"{config.basic.worker_name}-config.json",
            mime="application/json",
            help="Save configuration for later reuse",
            use_container_width=True
        )

    with col2:
        # Load from JSON
        uploaded_file = st.file_uploader(
            "📤 Import Configuration",
            type=['json'],
            help="Load previously saved configuration",
            key="config_upload"
        )

        if uploaded_file:
            try:
                import json
                loaded_config = json.load(uploaded_file)
                st.success("✅ Configuration loaded! Click 'Apply' to use it.")

                if st.button("Apply Configuration"):
                    # Update session state with loaded config
                    for key, value in loaded_config.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                st.session_state[sub_key] = sub_value
                        else:
                            st.session_state[key] = value
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading configuration: {str(e)}")


def show_download_success():
    """Show success message after download."""
    st.success("✅ Files downloaded successfully!")
    st.balloons()
