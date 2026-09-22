import os
import pandas as pd
from difflib import SequenceMatcher
from tag_unpacker import normalize, split_cell, unpack_report_tag, get_base_and_suffix, unpack_letter_suffix

def fuzzy_score(a, b):
    return SequenceMatcher(None, a, b).ratio() * 100

def run_exact_match_generic(df, normalized_master_set, tag_col, extra_cols):
    results = []
    for idx, row in df.iterrows():
        raw_cell = row[tag_col]
        candidates = split_cell(str(raw_cell))
        for candidate in candidates:
            unpacked = unpack_report_tag(candidate)
            for single_tag in unpacked:
                norm_candidate = normalize(single_tag)
                if norm_candidate in normalized_master_set:
                    record = {
                        'matched_type': 'exact',
                        'matched_tag': norm_candidate,
                        'row_idx': idx, 
                        'raw_cell': raw_cell,
                        'score': 100
                    }
                    for col_name, col_key in extra_cols.items():
                        record[col_name] = row[col_key]
                    results.append(record)
    return results

def run_fuzzy_match_generic(df, normalized_master_set, tag_col, extra_cols, threshold = 80):
    results = []
    for idx, row in df.iterrows():
        raw_cell = row[tag_col]
        candidates = split_cell(raw_cell)
        for candidate in candidates:
            unpacked = unpack_report_tag(candidate)
            for single_tag in unpacked:
                norm_candidate = normalize(single_tag)
                if norm_candidate not in normalized_master_set:
                    prefix = norm_candidate[:4]
                    filtered_master = [tag for tag in normalized_master_set 
                                       if tag.startswith(prefix)]
                    best_score = 0
                    best_tag = None
                    for tag in filtered_master:
                        score = fuzzy_score(norm_candidate, tag)
                        if score > best_score:
                            best_score = score
                            best_tag = tag
                    if best_score >= threshold and best_tag is not None:
                        record = {
                            'matched_type': 'fuzzy',
                            'matched_tag': best_tag,
                            'row_idx': idx, 
                            'raw_cell': raw_cell,
                            'score': best_score
                        }
                        for col_name, col_key in extra_cols.items():
                            record[col_name] = row[col_key]
                        results.append(record)
    return results

if __name__ == "__main__":
    # Пример использования модуля с гибким сопоставлением
    psr_path = os.path.join("data", "sample_input.xlsx")
    vdb_path = os.path.join("data", "vdb_sample.xlsx")

    if os.path.exists(psr_path) and os.path.exists(vdb_path):
        df_psr = pd.read_excel(psr_path, sheet_name="PSR", header=4)
        df_vdb = pd.read_excel(vdb_path)

        # Вызываем универсальный сопоставитель
        df_matched = generic_matching_pipeline(
            df_report=df_psr,
            df_vdb=df_vdb,
            tag_col="TAG NUMBER",
            extra_cols={
                "PO No": "PO_No",
                "MR \n[NUMBER]": "MR_Number"
            }
        )
        print("Результат сопоставления готов:")
        print(df_matched.head())
    else:
        print("[INFO] Запустите скрипт с реальными файлами в папке data/")