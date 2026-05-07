import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path):
    """
    从PDF中提取所有页面的表格，返回一个字典：
    { "页码": [DataFrame列表] }
    """
    tables_dict = {}

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_no = i + 1
            # 提取该页所有表格
            page_tables = page.extract_tables()
            if page_tables:
                dfs = []
                for table in page_tables:
                    # 第一行通常作为列名
                    df = pd.DataFrame(table[1:], columns=table[0])
                    dfs.append(df)
                    print(f"第{page_no}页 发现表格，形状：{df.shape}")
                tables_dict[page_no] = dfs
            else:
                print(f"第{page_no}页 未检测到表格")

    return tables_dict

def save_tables(tables_dict, output_prefix="table"):
    """
     将提取的表格保存为CSV文件
    """ 
    for page_no, dfs in tables_dict.items():
        for idx, df in enumerate(dfs):
            filename = f"{output_prefix}_p{page_no}_{idx}.csv"
            df.to_csv(filename, index=False, encoding="utf-8")
            print(f"保存表格：{filename}")


def extract_table_descriptions(pdf_path):
    """返回所有表格的自然语言描述列表，每条类似：(第3页) 姓名张三，学号2021001。"""
    descriptions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                headers = [h.strip() if h else "" for h in table[0]]
                for row in table[1:]:
                    if not any(row):
                        continue
                    parts = []
                    for h, cell in zip(headers, row):
                        if cell and str(cell).strip():
                            parts.append(f"{h}{str(cell).strip()}")
                    if parts:
                        sentence = "，".join(parts) + "。"
                        sentence_with_page = f"(第{page_num}页) {sentence}"
                        descriptions.append(sentence_with_page)
    return descriptions
if __name__ == "__main__":
    # 替换成你自己的PDF路径
    pdf_file = "sample_table.pdf"

    print(f"正在解析：{pdf_file}")
    tables = extract_tables_from_pdf(pdf_file)

    if tables:
        save_tables(tables)
        print("所有表格提取完成。")
    else:
        print("未提取到任何表格，请确认PDF内容。")