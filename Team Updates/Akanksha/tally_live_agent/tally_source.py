import requests

TALLY_URL = "http://localhost:9000"

def fetch_daybook(from_date, to_date):
    xml = f"""
    <ENVELOPE>
      <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
      </HEADER>
      <BODY>
        <EXPORTDATA>
          <REQUESTDESC>
            <REPORTNAME>Day Book</REPORTNAME>
            <STATICVARIABLES>
              <SVFROMDATE>{from_date}</SVFROMDATE>
              <SVTODATE>{to_date}</SVTODATE>
              <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """
    return requests.post(TALLY_URL, data=xml, timeout=10).content
