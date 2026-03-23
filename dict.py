import pandas as pd

filePath = "LTS Delays Codes with ID.csv"
dataFrame = pd.read_csv(filePath, dtype=str).fillna("")

for columnName in dataFrame.columns:
    dataFrame[columnName] = dataFrame[columnName].astype(str).str.strip()

# 1) Dept: dept_code -> dept_name
deptRows = dataFrame[
    ["Dept/Roll-up Code", "Dept/Roll-up Name"]
].drop_duplicates()

deptCodeDict = dict(
    zip(deptRows["Dept/Roll-up Code"], deptRows["Dept/Roll-up Name"])
)

# 2) System: dept_code -> {system_code -> system_name}
systemCodeDict = {}

systemRows = dataFrame[
    ["Dept/Roll-up Code", "System Code", "System Name"]
].drop_duplicates()

for deptCode, group in systemRows.groupby("Dept/Roll-up Code"):
    currentSystemDict = {}
    for _, row in group.iterrows():
        systemCode = row["System Code"]
        systemName = row["System Name"]
        if systemCode != "":
            currentSystemDict[systemCode] = systemName
    systemCodeDict[deptCode] = currentSystemDict

# 3) Symptom: (dept_code, system_code) -> {symptom_code -> symptom_name}
symptomCodeDict = {}

symptomRows = dataFrame[
    [
        "Dept/Roll-up Code",
        "System Code",
        "Symptom/Component Code",
        "Symptom/Component Name",
    ]
].drop_duplicates()

for (deptCode, systemCode), group in symptomRows.groupby(
    ["Dept/Roll-up Code", "System Code"]
):
    currentSymptomDict = {}
    for _, row in group.iterrows():
        symptomCode = row["Symptom/Component Code"]
        symptomName = row["Symptom/Component Name"]
        if symptomCode != "":
            currentSymptomDict[symptomCode] = symptomName
    symptomCodeDict[(deptCode, systemCode)] = currentSymptomDict

def getDeptName(deptCode):
    deptCode = str(deptCode).strip()
    return deptCodeDict.get(deptCode, "N/A")


def getSystemName(deptCode, systemCode):
    deptCode = str(deptCode).strip()
    systemCode = str(systemCode).strip()
    return systemCodeDict.get(deptCode, {}).get(systemCode, "N/A")


def getSymptomName(deptCode, systemCode, symptomCode):
    deptCode = str(deptCode).strip()
    systemCode = str(systemCode).strip()
    symptomCode = str(symptomCode).strip()
    return symptomCodeDict.get((deptCode, systemCode), {}).get(symptomCode, "N/A")
