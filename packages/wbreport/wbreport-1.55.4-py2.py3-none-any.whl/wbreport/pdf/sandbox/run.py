import importlib
import sys
from datetime import datetime

from wbportfolio.models import Product

report = sys.argv[1]

module = importlib.import_module("wbreport.pdf.sandbox.templates.{report}")
product = Product.objects.get(id=sys.argv[2])

start = datetime.strptime(sys.argv[3], "%Y-%m-%d").date()
end = datetime.strptime(sys.argv[4], "%Y-%m-%d").date()
context = product.report._get_file_context(start=start, end=end)
result = module.generate_report(context)
with open("portfolio/report/pdf/sandbox/templates/testfile.pdf", "wb") as test_file:
    test_file.write(result.read())
