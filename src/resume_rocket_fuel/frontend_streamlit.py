# More aggressive SQLite hack
import sys
try:
    if 'sqlite3' in sys.modules:
        del sys.modules['sqlite3'] # Try to remove it if it's already imported
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except Exception as e:
    print('SQLite hack failed: ', e) # Log this exception to see if this block itself causes issues
    # import logging
    # logging.warning(f"SQLite hack failed: {e}")
    pass

from resume_rocket_fuel.pipeline import pipeline_run
import streamlit as st
import os
from pathlib import Path
import logging
import traceback
import time

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_uploaded_file(uploaded_file, output_path):
    """Helper function to save uploaded files with error handling"""
    try:
        logger.info(f"Saving file to {output_path}")
        with open(output_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        logger.info(f"Successfully saved file to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file to {output_path}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'status' not in st.session_state:
        st.session_state.status = "Ready"
    if 'show_download_info' not in st.session_state:
        st.session_state.show_download_info = False
    if 'final_pdf_path_str' not in st.session_state:
        st.session_state.final_pdf_path_str = None

    st.title("📄 Resume Rocket Fuel")
    st.write("Upload your CV and Job Description to get started.")

    # Create a container for the form
    with st.container():
        # File uploaders with disabled state
        cv_file = st.file_uploader("📄 Upload CV (PDF)", type=['pdf'], disabled=st.session_state.processing, help="Select your CV file")
        jd_file = st.file_uploader("📄 Upload JD (PDF)", type=['pdf'], disabled=st.session_state.processing, help="Select the job description file")
        company_name = st.text_input("Enter Company Name", disabled=st.session_state.processing)

        # Create a container for file names
        file_names_container = st.empty()
        
        # Show file names only when not processing
        if not st.session_state.processing and (cv_file or jd_file):
            with file_names_container.container():
                if cv_file:
                    st.write(f"✅ CV uploaded: {cv_file.name}")
                if jd_file:
                    st.write(f"✅ JD uploaded: {jd_file.name}")
        elif st.session_state.processing:
            file_names_container.empty()

        # Submit button
        if st.button("🚀 Submit", disabled=st.session_state.processing):
            st.session_state.processing = True
            st.session_state.status = "Processing..."
            st.session_state.show_download_info = False
            st.session_state.final_pdf_path_str = None
            st.rerun()

    # Status and processing section
    if st.session_state.processing:
        with st.status(st.session_state.status, expanded=True) as status_widget:
            try:
                # Validate inputs
                if not all([cv_file, jd_file, company_name]):
                    st.error("Please provide all required inputs: CV, Job Description, and Company Name")
                    st.session_state.processing = False
                    st.session_state.status = "Ready"
                    st.rerun()
                    return

                # Output directory
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)

                # Save files
                cv_path = output_dir / "cv.pdf"
                jd_path = output_dir / "jd.pdf"

                if not save_uploaded_file(cv_file, cv_path) or not save_uploaded_file(jd_file, jd_path):
                    st.error("File saving failed")
                    st.session_state.processing = False
                    st.session_state.status = "Ready"
                    st.rerun()
                    return

                # Simulate processing steps shown to the user via st.status
                status_widget.update(label="🚀 Starting CV optimization...")
                time.sleep(1)
                status_widget.update(label="📝 Analyzing your CV...")
                time.sleep(1)
                status_widget.update(label="🎯 Optimizing for the role...")
                time.sleep(1)
                
                def update_status_callback(message: str):
                    status_widget.update(label=message)
                
                # Run the actual pipeline
                result = pipeline_run(cv_path, jd_path, company_name, status_callback=update_status_callback, output_format="PDF")

                if result:
                    status_widget.update(label="✅ Pipeline completed!", state="complete")
                    final_pdf_check_path = output_dir / "final_cv.pdf"
                    if final_pdf_check_path.exists():
                        st.session_state.show_download_info = True
                        st.session_state.final_pdf_path_str = str(final_pdf_check_path.absolute())
                    else:
                        st.session_state.show_download_info = False
                        logger.error("Pipeline reported success but final_cv.pdf not found in output.")
                        status_widget.update(label="⚠️ Error: Optimized PDF not found after processing.", state="error")

                else:
                    status_widget.update(label="❌ Pipeline failed.", state="error")
                    st.session_state.show_download_info = False

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                st.error(f"An unexpected error occurred: {str(e)}")
                status_widget.update(label=f"❌ Error: {str(e)}", state="error")
                st.session_state.show_download_info = False
            finally:
                st.session_state.processing = False
                st.session_state.status = "Ready"
                st.rerun()

    # Download button and success message section (displayed when not processing)
    if st.session_state.get('show_download_info', False) and st.session_state.get('final_pdf_path_str'):
        st.success("✅ CV optimization completed! Your PDF is ready for download.")
        
        pdf_path_for_download = Path(st.session_state.final_pdf_path_str)
        
        if pdf_path_for_download.exists():
            with open(pdf_path_for_download, "rb") as f_download:
                st.download_button(
                    label="📄 Download Final CV (PDF)",
                    data=f_download,
                    file_name=pdf_path_for_download.name,
                    mime="application/pdf"
                )
            st.info("Click the button above to download your final, recruiter-ready CV!")
        else:
            st.error("Error: The generated PDF could not be found for download. Please try again.")

if __name__ == "__main__":
    main()
