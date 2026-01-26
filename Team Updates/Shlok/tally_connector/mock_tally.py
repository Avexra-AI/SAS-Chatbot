from http.server import BaseHTTPRequestHandler, HTTPServer

MOCK_LEDGER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
  <BODY>
    <DATA>
      <COLLECTION>
        <LEDGER>
          <NAME>Cash</NAME>
          <PARENT>Cash-in-Hand</PARENT>
        </LEDGER>
        <LEDGER>
          <NAME>Sales</NAME>
          <PARENT>Income</PARENT>
        </LEDGER>
      </COLLECTION>
    </DATA>
  </BODY>
</ENVELOPE>
"""

MOCK_VOUCHER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ENVELOPE>
  <BODY>
    <DATA>
      <VOUCHER>
        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
        <DATE>20260119</DATE>
        <LEDGERENTRIES>
          <LEDGERENTRY>
            <LEDGERNAME>Sales</LEDGERNAME>
            <AMOUNT>-1000</AMOUNT>
          </LEDGERENTRY>
          <LEDGERENTRY>
            <LEDGERNAME>Cash</LEDGERNAME>
            <AMOUNT>1000</AMOUNT>
          </LEDGERENTRY>
        </LEDGERENTRIES>
      </VOUCHER>
    </DATA>
  </BODY>
</ENVELOPE>
"""


class MockTallyHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        if "List of Accounts" in body:
            response = MOCK_LEDGER_XML
        elif "Voucher Register" in body:
            response = MOCK_VOUCHER_XML
        else:
            response = "<ENVELOPE><BODY><ERROR>Unknown Request</ERROR></BODY></ENVELOPE>"

        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))


def run():
    server = HTTPServer(("localhost", 9000), MockTallyHandler)
    print("✅ Mock Tally running on http://localhost:9000")
    server.serve_forever()


if __name__ == "__main__":
    run()
