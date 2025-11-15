import aiohttp
import logging
import os
import hashlib
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from database.db import Database

SCHEDULE_URL = "https://pkeu.ru/raspisanie-zanyatiy"
BASE_URL = "https://pkeu.ru"
DOWNLOADS_DIR = "downloads"

async def cleanup_old_files():
    """Delete schedule files older than 8 days"""
    if not os.path.exists(DOWNLOADS_DIR):
        return
    
    now = datetime.now()
    for filename in os.listdir(DOWNLOADS_DIR):
        file_path = os.path.join(DOWNLOADS_DIR, filename)
        if os.path.isfile(file_path):
            file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age.days > 8:
                try:
                    os.remove(file_path)
                    logging.info(f"[CLEANUP] Deleted old file: {filename}")
                except Exception as e:
                    logging.error(f"[CLEANUP] Error deleting file {filename}: {e}")

async def run_initial_parsing(db: Database):
    logging.info("[SCHEDULER] Starting scheduled check for a new schedule file...")
    await cleanup_old_files()
    file_path, file_hash = await download_latest_schedule_file()
    if file_path and file_hash:
        existing_hash = await db.get_schedule_hash(file_hash)
        if not existing_hash:
            logging.info("[SCHEDULER] New schedule file detected. Starting parser.")
            await parse_schedule(file_path, file_hash, db)
            logging.info("[SCHEDULER] Update complete.")
        else:
            logging.info("[SCHEDULER] No new schedule files found.")
    else:
        logging.warning("[SCHEDULER] Failed to download schedule file.")

def clean_value(value):
    if value is None: return ""
    return str(value).strip()

def is_header_row(row_list):
    row_str = ' '.join(filter(None, [str(s) for s in row_list]))
    return ('БУ' in row_str or 'Ф' in row_str or 'Ю' in row_str or 'ТД' in row_str or 'К' in row_str) and 'ауд.' in row_str

def parse_with_calamine(file_path):
    try:
        from calamine import CalamineWorkbook
        logging.info("[PARSER_STRATEGY_A] Attempting to use 'calamine'...")
        workbook = CalamineWorkbook.from_path(file_path)
        all_rows = []
        for sheet_name in workbook.sheet_names:
            if 'курс' not in sheet_name.lower(): continue
            sheet = workbook.get_sheet_by_name(sheet_name)
            data = sheet.to_python(skip_empty_rows=False)
            for merged_range in sheet.merged_cells:
                first_row, first_col, last_row, last_col = merged_range
                value = data[first_row - 1][first_col - 1]
                for r in range(first_row - 1, last_row):
                    for c in range(first_col - 1, last_col):
                        data[r][c] = value
            all_rows.extend(data)
        logging.info("[PARSER_STRATEGY_A] 'calamine' successfully parsed the file.")
        return all_rows
    except Exception as e:
        logging.warning(f"[PARSER_STRATEGY_A] 'calamine' failed: {e}. Falling back to Strategy B.")
        return None

def parse_with_manual_xml(file_path):
    logging.info("[PARSER_STRATEGY_B] Using 'Manual XML Parsing' fallback.")
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            shared_strings_xml = z.read('xl/sharedStrings.xml')
            shared_strings_tree = ET.fromstring(shared_strings_xml)
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            shared_strings = [t.text or '' for t in shared_strings_tree.findall('main:si/main:t', ns)]

            all_rows = []
            sheet_files = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet')]
            for sheet_file in sheet_files:
                sheet_xml = z.read(sheet_file)
                sheet_tree = ET.fromstring(sheet_xml)
                rows_data = {}
                for cell in sheet_tree.findall('.//main:c', ns):
                    row_num = int(re.search(r'(\d+)', cell.get('r')).group(1))
                    col_letter = re.search(r'([A-Z]+)', cell.get('r')).group(1)
                    value = ""
                    value_node = cell.find('main:v', ns)
                    if value_node is not None:
                        if cell.get('t') == 's':
                            try:
                                value = shared_strings[int(value_node.text)]
                            except (ValueError, IndexError):
                                value = ""
                        else:
                            value = value_node.text
                    if row_num not in rows_data: rows_data[row_num] = {}
                    rows_data[row_num][col_letter] = clean_value(value)
                max_row = max(rows_data.keys()) if rows_data else 0
                for r in range(1, max_row + 1):
                    row_list = []
                    for i in range(100):
                        col_name = ''; temp = i
                        while temp >= 0:
                            col_name = chr(temp % 26 + ord('A')) + col_name; temp = temp // 26 - 1
                            if temp < 0: break
                        row_list.append(rows_data.get(r, {}).get(col_name, ''))
                    all_rows.append(row_list)
        logging.info("[PARSER_STRATEGY_B] Manual XML parsing complete.")
        return all_rows
    except Exception as e:
        logging.error(f"[PARSER_STRATEGY_B] CRITICAL FAILURE in Manual XML parsing: {e}", exc_info=True)
        return None

async def download_latest_schedule_file():
    logging.info("[PARSER_HTTP] Searching for schedule file on the site...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SCHEDULE_URL) as response:
                if response.status != 200: logging.error(f"[PARSER_HTTP] Site unavailable (status {response.status})"); return None, None
                soup = BeautifulSoup(await response.text(), 'lxml')
                link = soup.find('a', href=lambda href: href and ('.xlsx' in href or '.xls' in href))
                if not link: logging.warning("[PARSER_HTTP] Link to XLSX/XLS file not found."); return None, None
                file_url = BASE_URL + link['href'] if not link['href'].startswith('http') else link['href']
                file_name = os.path.basename(link['href'].split('?')[0])
                file_path = os.path.join(DOWNLOADS_DIR, file_name)
                os.makedirs(DOWNLOADS_DIR, exist_ok=True)
                async with session.get(file_url) as file_response:
                    content = await file_response.read()
                    with open(file_path, 'wb') as f: f.write(content)
                    file_hash = hashlib.sha256(content).hexdigest()
                    logging.info(f"[PARSER_HTTP] File '{file_name}' downloaded successfully.")
                    return file_path, file_hash
    except Exception as e:
        logging.error(f"[PARSER_HTTP] Error downloading file: {e}"); return None, None

async def parse_schedule(file_path, file_hash, db: Database):
    logging.info("[PARSER_CORE] Starting Adaptive Parsing Strategy.")
    data = parse_with_calamine(file_path)
    if data is None: data = parse_with_manual_xml(file_path)

    if data is None:
        logging.error("[PARSER_CORE] All parsing strategies failed. Unable to extract data.")
        return

    logging.info("[PARSER_ANALYZER] Starting data analysis phase.")
    all_lessons = []
    header_indices = [i for i, row in enumerate(data) if is_header_row(row)]
    logging.info(f"[PARSER_ANALYZER] Found {len(header_indices)} headers at rows: {header_indices}")

    for i, header_idx in enumerate(header_indices):
        header_row = data[header_idx]
        start_row = header_idx + 1
        end_row = header_indices[i + 1] if i + 1 < len(header_indices) else len(data)

        current_groups = {}
        for col_idx, group_cell in enumerate(header_row):
            group_name_raw = clean_value(group_cell)
            if group_name_raw and 'ауд' not in group_name_raw.lower() and len(group_name_raw) > 2 and 'курс' not in group_name_raw:
                aud_col_idx = col_idx + 1
                if aud_col_idx < len(header_row) and 'ауд' in clean_value(header_row[aud_col_idx]).lower():
                    for group_name in [g.strip() for g in group_name_raw.split(',')]:
                        if group_name: current_groups[group_name] = {'subject': col_idx, 'aud': aud_col_idx}
        if not current_groups: continue
        logging.info(f"[PARSER_ANALYZER] For header at row {header_idx}, found {len(current_groups)} groups: {list(current_groups.keys())}")
        
        for j in range(start_row, end_row):
            lesson_row = data[j]
            if not any(lesson_row): continue
            lesson_info_str = clean_value(lesson_row[3]) if len(lesson_row) > 3 else ""
            lesson_match = re.search(r'([IVX]+)\s*пара\s*(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})', lesson_info_str, re.I)
            
            if lesson_match:
                lesson_num, time_start, time_end = lesson_match.groups()
                day_of_week, date_str = clean_value(lesson_row[0]).lower(), clean_value(lesson_row[1])

                for group, cols in current_groups.items():
                    subject = clean_value(lesson_row[cols.get('subject', -1)])
                    if subject:
                        teacher = ""
                        if j + 1 < end_row and len(data[j+1]) > 3 and 'пара' not in clean_value(data[j+1][3]).lower():
                             teacher = clean_value(data[j+1][cols.get('subject', -1)])
                        cabinet = clean_value(lesson_row[cols.get('aud', -1)])
                        
                        # Extract resource link if present in subject or cabinet
                        resource_link = ""
                        if 'http' in subject:
                            # Extract URL from subject
                            url_match = re.search(r'https?://[^\s\)]+', subject)
                            if url_match:
                                resource_link = url_match.group(0)
                        
                        all_lessons.append({
                            "group_name": group, "day_of_week": day_of_week, "date": date_str,
                            "lesson_number": lesson_num.upper(), "time_start": time_start, "time_end": time_end,
                            "subject": subject, "teacher": teacher, "cabinet": cabinet, 
                            "resource_link": resource_link, "file_hash": file_hash
                        })
    
    if all_lessons:
        await db.clear_schedule_for_new_parse(file_hash)
        await db.save_schedule(all_lessons)
        logging.info(f"PARSING FINAL RESULT: SUCCESS! Total lessons found and saved: {len(all_lessons)}")
    else:
        logging.warning("PARSING FINAL RESULT: ATTENTION! No lessons found in the entire file.")