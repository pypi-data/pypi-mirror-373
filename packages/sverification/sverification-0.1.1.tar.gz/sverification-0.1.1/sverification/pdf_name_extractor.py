import re
import pdfplumber

def get_company_name(filepath, password=''):
    with pdfplumber.open(filepath, password=password) as pdf:
        # Get the last page and extract text
        if not pdf.pages:
            return 'unknown'
            
        page = pdf.pages[-1]
        text = page.extract_text()
        
        if not text:
            return 'unknown'

        # Get the footer from the first page
        lines = text.split('\n')
        if len(lines) >= 2:
            lines = lines[-2:]
        else:
            lines = text.split('\n')

        # Extract company name from email address using regular expression
        match = re.search(r"[\w\.]+@(\w+)", str(lines))
        
        last_page = pdf.pages[-1]
        last_page_text = last_page.extract_text()
        if not last_page_text and len(pdf.pages) >= 2:
            last_page = pdf.pages[-2]
            last_page_text = last_page.extract_text()
        
        if not last_page_text:
            last_page_text = ""

        # First page text for checks
        first_page_text = pdf.pages[0].extract_text() if pdf.pages else ""
        first_page_lines = first_page_text.split('\n') if first_page_text else []
        last_page_lines = last_page_text.split('\n') if last_page_text else []

        if match:
            company_name = match.group(1)
            company_name = 'tigo' if 'Yas' in company_name or 'Tigo' in company_name else company_name
        elif len(first_page_lines) >= 2 and ('Vodacom Tanzania' in str(first_page_lines[-2:]) or 'Operator' in str(first_page_lines[-2:])):
            company_name = 'vodacom' 
        elif len(last_page_lines) >= 1 and '*000#' in last_page_lines[-1]:
            company_name = 'airtel'
        elif len(last_page_lines) >= 3 and 'DTB imm' in str(last_page_lines[-3:]):
            company_name = 'dtb'
        elif 'TxnID' in str(first_page_lines) and 'EntryDate' in str(first_page_lines):
            company_name = 'tigo'
        elif len(last_page_lines) >= 3 and len(last_page_lines[-3].split(' ')) > 0 and 'halopesa' in last_page_lines[-3].split(' ')[0]:
            company_name = 'halotel'
        elif len(first_page_lines) >= 6 and 'absa' in str(first_page_lines[-6:]):
            company_name = 'absa'
        elif 'Account Class' in str(first_page_lines) or 'Uncollected Amoun' in str(last_page_lines):
            company_name = 'nmbbank'
        elif 'OVERDRAFT FACILITY DETAILS' in last_page_text:
            company_name = 'crdbbank_cbs'
        elif len(first_page_lines) >= 15 and ('MICR Code' in str(first_page_lines[:15]) or 'BIC Code' in str(first_page_lines[:15])):
            company_name = 'exim'
        elif len(first_page_lines) >= 10 and 'Absa Bank Tanzania Limited' in str(first_page_lines[:10]):
            company_name = 'absa_cbs'
        elif 'tcb bank plc' in str(first_page_lines).lower():
            company_name = 'tcb'
        elif hasattr(pdf, 'metadata') and pdf.metadata and 'vodacom' in str(pdf.metadata).lower():
            company_name = 'vodalipa'
        elif len(first_page_lines) >= 10 and 'Summary of Book Balance as at' in str(first_page_lines[:10]):
            company_name = 'crdbbank'
        elif 'nbc.co.tz' in str(lines):
            company_name = 'nbc'
        elif 'Deposit Withdrawal Balance' in str(pdf.pages[0].extract_text().split('\n')[:10]):
            company_name = 'selcom'
        elif 'safaricom' in str(pdf.pages[0].extract_text().split('\n')[-3:]).lower():
            company_name = 'safaricom'
        elif 'people\'s bank of zanzibar' in str(pdf.pages[0].extract_text().split('\n')[:10]).lower() or 'people\'s bank' in str(last_page.extract_text().split('\n')[-5:]).lower():
            company_name = 'pbz'
        elif '<->' in str(pdf.pages[0].extract_text().split('\n')[:5]):
            company_name = 'selcombank'
        elif 'global bank' in str(last_page.extract_text().split('\n')[-5:]):
            company_name = 'uba'
        elif 'Chq. Nr.' in str(last_page.extract_text().split('\n')[:20]):
            company_name = 'azania'
        elif 'Mwanga Hakika' in str(pdf.pages[0].extract_text().split('\n')[:4]):
            company_name = 'mwanga'
        elif 'equitybank.co.ke' in str(pdf.pages[0].extract_text().split('\n')[:4]) or 'TTrraannssaaccttiioonn' in str(pdf.pages[0].extract_text().split('\n')[:25]):
            company_name = 'equitybank'
        elif 'Description Payment Details Reference' in str(pdf.pages[0].extract_text().split('\n')[:8]):
            company_name = 'fdh_bank'
        elif 'Ecobank Tanzania' in str(pdf.pages[0].extract_text().split('\n')[:8]):
            company_name = 'ecobank'
        elif 'type of a/c' in str(pdf.pages[0].extract_text().split('\n')[:8]).lower() and 'trans dt' in str(pdf.pages[0].extract_text().split('\n')[:8]).lower():
            company_name = 'sidianbank'
        elif 'Ledger Balance Available Balance' in str(pdf.pages[0].extract_text().split('\n')[:10]):
            company_name = 'stanbicbank'
        elif '@uchumibank' in str(last_page.extract_text().split('\n')[:5]):
            company_name = 'uchumibank'
        elif 'taarifa ya muamala' in str(pdf.pages[0].extract_text().split('\n')[:5]).lower():
            company_name = 'azampesa'
        else:
            company_name = 'unknown'
        return company_name