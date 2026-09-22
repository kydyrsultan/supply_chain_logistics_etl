import os
import re
import pandas as pd
from tag_unpacker import normalize, split_cell, unpack_report_tag

def is_valid_tag(tag: str) -> bool:
    """Проверяет, является ли тэг валидным инженерным тэгом."""
    if not tag or pd.isna(tag):
        return False

    tag_str = str(tag).strip()

    # 1. Запрещенные символы диапазонов/перечислений
    invalid_chars = ['~', '&', '/', '、']
    for char in invalid_chars:
        if char in tag_str:
            return False

    # 2. Если строка содержит китайские иероглифы — бракуем
    if re.search(r'[\u4e00-\u9fff]', tag_str):
        return False

    # 3. Тэг должен быть не короче 3 символов и содержать хотя бы одну цифру или букву
    if len(tag_str) < 3 or not re.search(r'[A-Za-z0-9]', tag_str):
        return False

    return True


def process_report_dataframe(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Общий обработчик для колонок с тэгами."""
    unpacked_records = []

    for row_id, raw_cell in enumerate(df[column_name]):
        # 1. Если ячейка изначально пустая
        if pd.isna(raw_cell) or not str(raw_cell).strip():
            unpacked_records.append({
                'Row_id': row_id,
                'Raw_cell': raw_cell,
                'Normalized_tag': None,
            })
            continue

        raw_str = str(raw_cell).strip()
        candidates = split_cell(raw_cell)
        valid_tags_found = []

        # 2. Прогоняем через правила unpacker
        for candidate in candidates:
            unpacked_tags = unpack_report_tag(candidate)
            for tag in unpacked_tags:
                norm_tag = normalize(tag)

                if norm_tag:
                    # Точечная очистка: убираем кавычки, скобки и мусорные знаки препинания по краям
                    norm_tag = norm_tag.strip('"\'();:<>?=@-. \t\n\r\uff0c')

                # Проверяем через обновленный фильтр
                if is_valid_tag(norm_tag):
                    valid_tags_found.append(norm_tag)

        # 3. Записываем результаты
        if valid_tags_found:
            for norm_tag in valid_tags_found:
                unpacked_records.append({
                    'Row_id': row_id,
                    'Raw_cell': raw_str,
                    'Normalized_tag': norm_tag,
                })
        else:
            unpacked_records.append({
                'Row_id': row_id, 
                'Raw_cell': raw_str, 
                'Normalized_tag': None
            })

    # Удаляем точные дубликаты комбинаций (Row_id + Normalized_tag)
    res_df = pd.DataFrame(unpacked_records).drop_duplicates(
        subset=['Row_id', 'Normalized_tag']
    )
    return res_df.reset_index(drop=True)


def extract_errors(df_clean: pd.DataFrame, report_name: str) -> pd.DataFrame:
    """Берет строки, где Normalized_tag пустой, но Raw_cell содержал текст."""
    errors = df_clean[
        df_clean['Normalized_tag'].isna() & df_clean['Raw_cell'].notna()
    ].copy()
    errors['Source_Report'] = report_name
    return errors[['Row_id', 'Raw_cell', 'Source_Report']]


def run_full_pipeline(psr_file, esr_file, ssr_file, output_path, errors_path):
    """Главный ETL пайплайн для сбора и распаковки PSR, ESR, SSR отчетов."""
    
    # 1. ОБРАБОТКА PSR
    if os.path.exists(psr_file):
        df_psr = pd.read_excel(psr_file, sheet_name='PSR', header=4)
        df_psr_clean = process_report_dataframe(df_psr, 'TAG NUMBER')
        df_psr_clean.to_excel(output_path, sheet_name='PSR', index=False)
        print(f'PSR обработан: {len(df_psr_clean)} строк.')
    else:
        df_psr_clean = pd.DataFrame(columns=['Row_id', 'Raw_cell', 'Normalized_tag'])
        print(f'[WARNING] PSR файл не найден: {psr_file}')

    # 2. ОБРАБОТКА ESR
    if os.path.exists(esr_file):
        df_esr = pd.read_excel(esr_file, sheet_name='Expediting Report', header=1)
        df_esr_clean = process_report_dataframe(df_esr, 'Tag No.')
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_esr_clean.to_excel(writer, sheet_name='ESR', index=False)
        print(f'ESR обработан: {len(df_esr_clean)} строк.')
    else:
        df_esr_clean = pd.DataFrame(columns=['Row_id', 'Raw_cell', 'Normalized_tag'])
        print(f'[WARNING] ESR файл не найден: {esr_file}')

    # 3. ОБРАБОТКА SSR
    if os.path.exists(ssr_file):
        df_ssr = pd.read_excel(ssr_file, sheet_name='CCP二期', header=1)
        df_ssr_clean = process_report_dataframe(df_ssr, '设备位号\nTag number')
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_ssr_clean.to_excel(writer, sheet_name='SSR', index=False)
        print(f'SSR обработан: {len(df_ssr_clean)} строк.')
    else:
        df_ssr_clean = pd.DataFrame(columns=['Row_id', 'Raw_cell', 'Normalized_tag'])
        print(f'[WARNING] SSR файл не найден: {ssr_file}')

    # 4. ФОРМИРОВАНИЕ 'Master_Tags'
    reports_columns_list = [
        df_psr_clean['Normalized_tag'],
        df_esr_clean['Normalized_tag'],
        df_ssr_clean['Normalized_tag'],
    ]

    all_tags = pd.concat(reports_columns_list)
    df_master = (
        all_tags.dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
        .to_frame(name='Normalized_tag')
    )

    if os.path.exists(output_path):
        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_master.to_excel(writer, sheet_name='Master_Tags', index=False)
        print(f'\nMaster_Tags сформирован: {len(df_master)} уникальных чистых тэгов.')

    # 5. ВЫГРУЗКА ОШИБОК
    psr_errors = extract_errors(df_psr_clean, 'PSR')
    esr_errors = extract_errors(df_esr_clean, 'ESR')
    ssr_errors = extract_errors(df_ssr_clean, 'SSR')

    with pd.ExcelWriter(errors_path, engine='openpyxl') as writer:
        psr_errors.to_excel(writer, sheet_name='PSR_errors', index=False)
        esr_errors.to_excel(writer, sheet_name='ESR_errors', index=False)
        ssr_errors.to_excel(writer, sheet_name='SSR_errors', index=False)

    print(f'\nГотово!\nОсновной файл: {output_path}\nФайл с ошибками: {errors_path}')


if __name__ == "__main__":
    # Относительные пути для запуска внутри проекта
    DATA_DIR = "data"
    OUTPUT_DIR = os.path.join("data", "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    PSR_PATH = os.path.join(DATA_DIR, "psr_sample.xlsx")
    ESR_PATH = os.path.join(DATA_DIR, "esr_sample.xlsx")
    SSR_PATH = os.path.join(DATA_DIR, "ssr_sample.xlsx")
    
    OUT_PATH = os.path.join(OUTPUT_DIR, "unpacked_tags_from_reports.xlsx")
    ERRORS_PATH = os.path.join(OUTPUT_DIR, "tags_to_fix.xlsx")

    run_full_pipeline(PSR_PATH, ESR_PATH, SSR_PATH, OUT_PATH, ERRORS_PATH)