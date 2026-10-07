import requests
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

SUB_SUBJECT_ID = 22

# الخطوة 1: جلب قائمة كل المؤشرات تحت القسم
list_url = f"https://www.capmas.gov.eg:8080/api/Subject/SubSubjectWithIndicator/{SUB_SUBJECT_ID}"
resp = requests.get(list_url, headers=headers)
data = resp.json()

# دالة بتدور جوه أي قاموس أو قائمة وتجمع كل indicatorId مع اسمه
indicators = {}

def collect(obj):
    if isinstance(obj, dict):
        if "indicatorId" in obj and "name" in obj:
            indicators[obj["indicatorId"]] = obj["name"]
        for v in obj.values():
            collect(v)
    elif isinstance(obj, list):
        for item in obj:
            collect(item)

collect(data)
print("عدد المؤشرات اللي اتلقطت:", len(indicators))

# الخطوة 2: سحب بيانات كل مؤشر
all_rows = []
filter_url = "https://www.capmas.gov.eg:8080/api/Indicator/IndicatorFilter"

for ind_id, ind_name in indicators.items():
    try:
        r = requests.get(filter_url, params={
            "IndicatorId": ind_id,
            "SubSubjectId": SUB_SUBJECT_ID
        }, headers=headers)
        result = r.json()
        for category in result.get("data", []):
            cat_name_ar = category.get("name")
            for point in category.get("data", []):
                all_rows.append({
                    "indicator_id": ind_id,
                    "indicator_name": ind_name,
                    "category_ar": cat_name_ar,
                    "year": point.get("year"),
                    "value": point.get("value")
                })
        print(f"تم: {ind_id} - {ind_name}")
    except Exception as e:
        print(f"فشل المؤشر {ind_id}: {e}")
    time.sleep(0.5)

df = pd.DataFrame(all_rows)
df.to_excel("all_indicators_subsubject22.xlsx", index=False)
print("تم حفظ الملف بنجاح، عدد الصفوف:", len(df))