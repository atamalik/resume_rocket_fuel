import streamlit as st
import logging
import traceback
from pathlib import Path
import PyPDF2
import time
import markdown  # Added for HTML conversion
import pdfkit  # Added for HTML to PDF conversion

from resume_rocket_fuel.crew import ResumeRocketFuel
from resume_rocket_fuel.pdf_export import convert_markdown_to_pdf

# Logging Setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_uploaded_file(uploaded_file, output_path):
    try:
        with open(output_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return True
    except Exception as e:
        logger.error(f"Error saving file to {output_path}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"Failed to read PDF at {pdf_path}: {str(e)}")
    return text

def simulate_agent_progress(status_callback):
    agent_steps = [
        "👀 Agent 1 analyzing your CV...",
        "🧠 Agent 2 researching company details...",
        "✍️ Agent 3 crafting personalized improvements...",
        "🤖 QA Agent preparing the final version..."
    ]
    for step in agent_steps:
        status_callback(step)
        time.sleep(2)

def generate_html_from_md(md_path: Path, html_path: Path) -> bool:
    try:
        with open(md_path, "r", encoding="utf-8") as f_in:
            md_content = f_in.read()
        html_content = markdown.markdown(md_content)
        with open(html_path, "w", encoding="utf-8") as f_out:
            f_out.write(html_content)
        logger.info(f"✅ HTML successfully created at {html_path}")
        return True
    except Exception as e:
        logger.error(f"❌ HTML conversion failed: {str(e)}")
        return False

def convert_html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    try:
        logger.info("=== Starting PDF Conversion Process ===")
        logger.info(f"Current working directory: {Path.cwd()}")
        logger.info(f"HTML file path (absolute): {html_path.absolute()}")
        logger.info(f"PDF file path (absolute): {pdf_path.absolute()}")
        
        # Check if HTML file exists and is readable
        if not html_path.exists():
            logger.error(f"❌ HTML file not found at {html_path}")
            return False
            
        logger.info(f"✅ HTML file exists at {html_path}")
        logger.info(f"HTML file size: {html_path.stat().st_size} bytes")
        
        # Read and verify HTML content
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                logger.info(f"HTML content length: {len(html_content)} characters")
                logger.info(f"HTML content preview: {html_content[:200]}...")
                if not html_content.strip():
                    logger.error("❌ HTML file is empty")
                    return False
        except Exception as e:
            logger.error(f"❌ Error reading HTML file: {str(e)}")
            return False
        
        # Configure pdfkit options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'quiet': None,
            'enable-local-file-access': None,  # Allow access to local files
            'debug-javascript': None,  # Enable JavaScript debugging
            'javascript-delay': '1000',  # Wait for JavaScript to execute
            'no-stop-slow-scripts': None  # Don't stop on slow scripts
        }
        
        logger.info(f"PDF conversion options: {options}")
        
        # Ensure output directory exists
        try:
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Output directory created/verified: {pdf_path.parent}")
        except Exception as e:
            logger.error(f"❌ Error creating output directory: {str(e)}")
            return False
        
        # Convert HTML to PDF
        logger.info("Starting PDF conversion with pdfkit...")
        try:
            pdfkit.from_file(str(html_path), str(pdf_path), options=options)
            logger.info("✅ PDF conversion completed")
        except Exception as e:
            logger.error(f"❌ Error during PDF conversion: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        
        # Verify PDF was created
        if pdf_path.exists():
            pdf_size = pdf_path.stat().st_size
            logger.info(f"✅ PDF successfully created at {pdf_path}")
            logger.info(f"PDF file size: {pdf_size} bytes")
            
            if pdf_size == 0:
                logger.error("❌ PDF file is empty")
                return False
                
            return True
        else:
            logger.error("❌ PDF file was not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unexpected error in PDF conversion: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def pipeline_run(cv_path: Path, jd_path: Path, company_name: str, output_format: str, status_callback=None) -> bool:
    try:
        logger.info("=== Starting Pipeline Run ===")
        logger.info(f"Current working directory: {Path.cwd()}")
        logger.info(f"CV path: {cv_path}")
        logger.info(f"JD path: {jd_path}")
        logger.info(f"Company name: {company_name}")
        logger.info(f"Output format: {output_format}")
        
        rocket_fuel = ResumeRocketFuel()
        crew = rocket_fuel.crew()

        cv_content = extract_text_from_pdf(cv_path)
        jd_content = extract_text_from_pdf(jd_path)

        if status_callback:
            status_callback("🚀 Starting CV optimization process...")
            simulate_agent_progress(status_callback)

        task_variables = {
            "CANDIDATE_CV": cv_content,
            "JOB_DESCRIPTION": jd_content,
            "COMPANY_NAME": company_name,
            "COMPANY_PROFILE_REPORT": "",
            "CV_ANALYSIS_REPORT": "",
            "UPDATED_CV_ANALYSIS_REPORT": "",
            "FINAL_CV_MARKDOWN": ""
        }

        result = crew.kickoff(inputs=task_variables)

        # Use absolute paths for output files
        output_dir = Path.cwd() / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        final_md_path = output_dir / "final_cv.md"
        final_pdf_path = output_dir / "final_cv.pdf"
        final_html_path = output_dir / "final_polished_cv.html"

        logger.info("=== Checking Output Files ===")
        logger.info(f"Output directory: {output_dir.absolute()}")
        logger.info(f"Markdown file exists: {final_md_path.exists()}")
        if final_md_path.exists():
            logger.info(f"Markdown file size: {final_md_path.stat().st_size} bytes")
            
        logger.info(f"HTML file exists: {final_html_path.exists()}")
        if final_html_path.exists():
            logger.info(f"HTML file size: {final_html_path.stat().st_size} bytes")
            
        logger.info(f"PDF file exists: {final_pdf_path.exists()}")
        if final_pdf_path.exists():
            logger.info(f"PDF file size: {final_pdf_path.stat().st_size} bytes")

        if final_md_path.exists() and final_md_path.stat().st_size > 0:
            logger.info("=== Starting Output Generation ===")
            logger.info(f"Output format requested: {output_format}")
            
            if output_format.upper() == "PDF":
                logger.info("PDF output requested, checking prerequisites...")
                # First ensure we have the HTML version
                if not final_html_path.exists():
                    logger.warning("⚠️ HTML file not found. Converting from markdown...")
                    html_success = generate_html_from_md(final_md_path, final_html_path)
                    if not html_success:
                        logger.warning("⚠️ HTML conversion failed.")
                        return False
                    logger.info("✅ HTML file created successfully")
                
                # Then convert HTML to PDF
                if final_html_path.exists():
                    logger.info("Starting PDF conversion process...")
                    logger.info(f"HTML file path: {final_html_path}")
                    logger.info(f"PDF file path: {final_pdf_path}")
                    try:
                        pdf_success = convert_html_to_pdf(final_html_path, final_pdf_path)
                        if not pdf_success:
                            logger.error("❌ PDF conversion failed")
                            return False
                        logger.info("✅ PDF conversion completed successfully")
                    except Exception as e:
                        logger.error(f"❌ Error during PDF conversion: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return False
                else:
                    logger.error("❌ HTML file not found for PDF conversion")
                    return False
            elif output_format.upper() == "HTML":
                if not final_html_path.exists():
                    logger.warning("⚠️ HTML file not found. Converting from markdown...")
                    html_success = generate_html_from_md(final_md_path, final_html_path)
                    if not html_success:
                        logger.warning("⚠️ HTML conversion failed.")
        else:
            logger.warning("⚠️ final_cv.md not found or empty. No output generated.")

        if status_callback:
            status_callback("🎉 Your optimized CV is ready!")

        return True

    except Exception as e:
        logger.error(f"Error in pipeline_run: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if status_callback:
            status_callback("❌ An error occurred during processing.")
        return False

def main():
    st.title("📄 Resume Rocket Fuel")
    st.write("Upload your CV and Job Description to get started.")

    cv_file = st.file_uploader("📂 Upload your CV (PDF)", type=['pdf'])
    jd_file = st.file_uploader("📂 Upload Job Description (PDF)", type=['pdf'])
    company_name = st.text_input("🏢 Enter Company Name")
    output_format = st.selectbox("📦 Select Output Format", ["PDF", "HTML"])

    if st.button("🚀 Submit"):
        # Create output directory relative to project root
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        if not all([cv_file, jd_file, company_name]):
            st.error("❗ Please provide all required inputs: CV, Job Description, and Company Name")
            return

        cv_path = output_dir / "cv.pdf"
        jd_path = output_dir / "jd.pdf"

        if not save_uploaded_file(cv_file, cv_path) or not save_uploaded_file(jd_file, jd_path):
            st.error("❗ File saving failed.")
            return

        status_placeholder = st.empty()

        def update_status(message: str):
            status_placeholder.info(message)

        try:
            with st.spinner("🚀 Launching Agents..."):
                logger.info("Running backend pipeline with real-time updates...")
                result = pipeline_run(cv_path, jd_path, company_name, output_format, status_callback=update_status)

            final_pdf = output_dir / "final_cv.pdf"
            final_html = output_dir / "final_polished_cv.html"

            if result:
                st.success("✅ CV optimization completed successfully!")

                if output_format.upper() == "PDF" and final_pdf.exists():
                    with open(final_pdf, "rb") as f:
                        st.download_button(
                            label="📄 Download Final CV (PDF)",
                            data=f,
                            file_name="final_cv.pdf",
                            mime="application/pdf"
                        )
                    st.info("💡 Your recruiter-ready CV is available for download (PDF)!")
                elif output_format.upper() == "HTML" and final_html.exists():
                    with open(final_html, "r", encoding="utf-8") as f:
                        st.download_button(
                            label="🌐 Download Final CV (HTML)",
                            data=f.read(),
                            file_name="final_cv.html",
                            mime="text/html"
                        )
                    st.info("💡 Your recruiter-ready CV is available for download (HTML)!")
                else:
                    st.warning("⚠️ Final output not found. Please check the output folder.")
            else:
                st.error("❌ An error occurred during CV optimization. Please try again.")

        except Exception as e:
            logger.error(f"Unexpected error during submission: {str(e)}")
            st.error(f"❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
