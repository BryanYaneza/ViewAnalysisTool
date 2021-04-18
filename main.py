import openpyxl
import re
import teradatasql
from datetime import date

# Test Strings
sample = """SHOW VIEW VPROD_DIM.P_PKY_MPRS_GRP_INF;\r

CREATE VIEW VPROD_DIM.P_PKY_MPRS_GRP_INF AS\r
SELECT P_ID\r
    , PKY_ID\r
    , MPRS_CT_ID\r
    , GRP.P_MRS_GRP_CT\r
FROM VPROD_DIM.P_UPC_INF U\r
     INNER JOIN VPROD.P_UPC_MRS_GRP_INF GRP\r 
                ON GRP.P_UPC_ID = U.P_UPC_ID\r
GROUP BY 1,2,3,4;"""
sample2 = ["bryan\r", "bryan"]
sample3 = [
    'CREATE VIEW VPROD_DIM.P_PKY_MPRS_GRP_INF AS\rSELECT P_ID\r    , PKY_ID\r    '
    ', MPRS_CT_ID\r    , GRP.P_MRS_GRP_CT\rFROM VPROD_DIM.P_UPC_INF U\r     '
    'INNER JOIN VPROD.P_UPC_MRS_GRP_INF GRP \r                ON GRP.P_UPC_ID = U.P_UPC_ID\rGROUP BY 1,2,3,4;']

# # PROD A Credentials
HOST = "127.0.0.1"
USER = "dbc"
PASSWORD = "quebec"

# Load Target Table
with open("TargetView.txt") as f:
    content = f.readlines()
views = [x.strip().upper() for x in content]

# Presets
listReference = ["FROM", "INNER JOIN", "OUTER JOIN", "RIGHT OUTER JOIN", "LEFT OUTER JOIN"]
lockingReference = ["LOCKING TABLE", "LOCKING ROW"]
list1 = []
result = []
analyzedResult = []
isTerminate = False

# Connect To Teradata
def connectToTeradata(host, username, password):
    global con
    terminate = False
    while not terminate:
        try:
            con = teradatasql.connect(
                '{"host": "' + host + '","user":"' + username + '","password":"' + password + '"}')
            terminate = True
            print("Connection Successful\n")
        except teradatasql.Error:
            print("Connection Failed\n")
            exit()
    return con

# Extract view
def extractView(consCredential, view):
    with consCredential.cursor() as cur:
        cur.execute("SHOW VIEW {0}".format(view))
        return """{}""".format("".join([row for row in cur.fetchall()][0]).replace("\r", "\n").upper())

# Drill Down on the view
def drillDown(viewDef):
    list1 = []
    for ref in listReference:
        match = re.findall('(?<=%s).*$' % ref, viewDef, re.MULTILINE)
        for x in match:
            for result in re.split(r'\s', x):
                if len(result.split(".")) > 1:
                    list1.append(result)
    return list1

# Test Drill Down Function
def drillDownLocal(viewDef):
    list1 = []
    for ref in listReference:
        match = re.findall('(?<=%s).*$' % ref, viewDef, re.MULTILINE)
        for x in match:
            for result in re.split(r'\s', x):
                if len(result.split(".")) > 1:
                    list1.append(result)
    return list1

# Analyze the view
def analyzeView(conn, extractedViews):
    innerList = []
    extractedViewDictionary = {}
    for extrView in extractedViews:
        count = 0
        for ref in lockingReference:
            innerList.append(re.findall(ref, extractView(conn, extrView), re.MULTILINE))
        # Underlying view has Locking Table
        if innerList[0] and not innerList[1]:
            extractedViewDictionary[extrView] = 1
        # Underlying view has Locking Row
        elif not innerList[0] and innerList[1]:
            extractedViewDictionary[extrView] = 2
        # No Locking Statement
        else:
            extractedViewDictionary[extrView] = 3
        innerList = []

    print(extractedViewDictionary)

    for k,h in extractedViewDictionary:
        print(k,h)

    return extractedViewDictionary

def writeToExcel():
    workbook = openpyxl.Workbook
    sheet = workbook.active
    sheet["A1"] = "hello"
    workbook.save("View Analysis Results - " + date.strftime("%m/%d/%y"))




# Main Function
def main():
    writeToExcel()
    # conn = connectToTeradata(HOST, USER, PASSWORD)
    # for view in views:
    #     try:
    #         print("\nAnalyzing view: {0}".format(view))
    #         extractedView = extractView(conn, view)
    #         extractedViews = drillDown(extractedView)
    #         analyzeView(conn, extractedViews)
    #     except teradatasql.Error:
    #         print(extractedViews[0] + " has no Lock Statement\n")


print("Welcome")
main()
