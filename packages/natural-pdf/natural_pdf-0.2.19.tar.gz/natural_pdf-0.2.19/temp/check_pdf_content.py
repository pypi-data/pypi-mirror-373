from natural_pdf import PDF

pdf = PDF('pdfs/01-practice.pdf')
page = pdf.pages[0]
texts = page.find_all('text')
print(f'Total text elements: {len(texts)}')
print('Sample texts:')
for t in texts[:20]:
    print(f'  - {repr(t.text)}')