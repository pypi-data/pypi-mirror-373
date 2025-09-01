from fpdf import FPDF

def generate_pdf(biomarker_data, outfile_src):
    pdf = FPDF()

    pdf.add_page()


    pdf.output(outfile_src)