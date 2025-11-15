"""
XLSX Parser for college schedule
Uses calamine for efficient parsing with openpyxl as fallback
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ScheduleParser:
    """Parser for XLSX schedule files"""
    
    # Lesson numbers and their corresponding row positions
    LESSON_NUMBERS = {
        'III': 3,
        'IV': 4,
        'V': 5,
        'VI': 6,
        'VII': 7
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.schedule_data = []
        
    async def parse(self) -> List[Dict[str, Any]]:
        """Parse XLSX file and extract schedule data"""
        try:
            # Try calamine first for better performance
            return await self._parse_with_calamine()
        except Exception as e:
            logger.warning(f"Calamine parsing failed: {e}, trying openpyxl")
            try:
                return await self._parse_with_openpyxl()
            except Exception as e:
                logger.error(f"Failed to parse file: {e}")
                return []
    
    async def _parse_with_calamine(self) -> List[Dict[str, Any]]:
        """Parse using python-calamine library"""
        try:
            from python_calamine import CalamineWorkbook
            
            workbook = CalamineWorkbook.from_path(self.file_path)
            schedule_data = []
            
            # Get all sheet names
            sheet_names = workbook.sheet_names
            
            for sheet_name in sheet_names:
                # Determine base and course from sheet name
                base, course = self._get_base_and_course(sheet_name)
                if base is None or course is None:
                    continue
                
                # Load the sheet
                sheet = workbook.get_sheet_by_name(sheet_name)
                if sheet is None:
                    continue
                
                data = sheet.to_python()
                parsed = self._parse_sheet_data(data, base, course)
                schedule_data.extend(parsed)
            
            return schedule_data
            
        except ImportError:
            logger.error("python-calamine not installed")
            raise
        except Exception as e:
            logger.error(f"Calamine parsing error: {e}")
            raise
    
    async def _parse_with_openpyxl(self) -> List[Dict[str, Any]]:
        """Parse using openpyxl library as fallback"""
        try:
            from openpyxl import load_workbook
            
            workbook = load_workbook(self.file_path, data_only=True)
            schedule_data = []
            
            for sheet_name in workbook.sheetnames:
                # Determine base and course from sheet name
                base, course = self._get_base_and_course(sheet_name)
                if base is None or course is None:
                    continue
                
                sheet = workbook[sheet_name]
                
                # Convert to list of lists
                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append(list(row))
                
                parsed = self._parse_sheet_data(data, base, course)
                schedule_data.extend(parsed)
            
            return schedule_data
            
        except Exception as e:
            logger.error(f"Openpyxl parsing error: {e}")
            raise
    
    def _get_base_and_course(self, sheet_name: str) -> tuple:
        """Extract base and course from sheet name"""
        # Sheet names like "1 курс", "2 курс", "3 курс" for base 9
        # or "1 курс", "2 курс" for base 11
        
        match = re.search(r'(\d+)\s*курс', sheet_name.lower())
        if match:
            course = int(match.group(1))
            # Courses 1-3 are for base 9, courses 1-2 can also be for base 11
            # We'll handle this by parsing both and letting the database handle it
            return (9, course) if course <= 3 else (None, None)
        
        return (None, None)
    
    def _parse_sheet_data(self, data: List[List[Any]], base: int, course: int) -> List[Dict[str, Any]]:
        """Parse sheet data and extract schedule information"""
        schedule_entries = []
        
        if not data or len(data) < 10:
            return schedule_entries
        
        # Find header row with group names
        group_columns = {}
        date_column = None
        day_column = None
        pair_column = None
        
        # Search for the row with individual group names (around row 13-14, 0-indexed)
        # This row has one group per column
        group_row_idx = None
        for row_idx in range(10, min(20, len(data))):
            row = data[row_idx]
            found_groups_in_row = 0
            temp_groups = {}
            
            for col_idx, cell in enumerate(row):
                if cell and isinstance(cell, str):
                    cell_str = str(cell).strip()
                    
                    # Check for "Пара" column
                    if 'пара' in cell_str.lower() and len(cell_str) < 10:
                        pair_column = col_idx
                    
                    # Look for individual group names (not lists)
                    match = re.match(r'^([А-ЯA-Z]{1,3}\d*-\d{2,3})$', cell_str)
                    if match:
                        temp_groups[col_idx] = match.group(1)
                        found_groups_in_row += 1
            
            # If we found several groups in this row, use it
            if found_groups_in_row >= 3:
                group_columns = temp_groups
                group_row_idx = row_idx
                logger.info(f"Found {len(group_columns)} groups in row {row_idx + 1}")
                break
        
        # Find date and day columns - look specifically in rows after the group header
        for row_idx in range(13, min(20, len(data))):  # Start from row after group names
            row = data[row_idx]
            for col_idx in range(min(12, len(row))):
                cell = row[col_idx] if col_idx < len(row) else None
                if not cell:
                    continue
                    
                cell_str = str(cell).strip().lower()
                
                # Check for day of week
                day_match = False
                for day in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']:
                    if day == cell_str or day in cell_str:
                        if day_column is None:
                            day_column = col_idx
                            logger.info(f"Found day column at {col_idx}, value: {cell}")
                            day_match = True
                            break
                
                # If we found day, next column should be date
                if day_match and col_idx + 1 < len(row):
                    next_cell = row[col_idx + 1]
                    if next_cell and (hasattr(next_cell, 'strftime') or '2025' in str(next_cell) or '2024' in str(next_cell)):
                        date_column = col_idx + 1
                        logger.info(f"Found date column at {date_column}, value: {next_cell}")
                        break
            
            if day_column is not None and date_column is not None:
                # Pair column should be right after date column
                if pair_column is None:
                    pair_column = date_column + 1
                    logger.info(f"Setting pair column to {pair_column}")
                break
        
        if not group_columns:
            logger.warning(f"No groups found in sheet for base {base}, course {course}")
            return schedule_entries
        
        logger.info(f"Found groups: {list(group_columns.values())}")
        logger.info(f"Day column: {day_column}, Date column: {date_column}, Pair column: {pair_column}")
        
        # Parse schedule data - start from the row after we found groups
        current_date = None
        current_day = None
        
        # Start from the row after group names
        start_row = (group_row_idx + 1) if group_row_idx is not None else 13
        
        for row_idx in range(start_row, len(data)):
            row = data[row_idx]
            
            # Get date and day
            if day_column is not None and day_column < len(row):
                day_val = row[day_column]
                if day_val and isinstance(day_val, str):
                    day_str = str(day_val).strip().lower()
                    if any(d in day_str for d in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']):
                        current_day = day_val.strip()
            
            if date_column is not None and date_column < len(row):
                date_val = row[date_column]
                if date_val and str(date_val).strip():
                    parsed_date = self._parse_date(date_val)
                    if parsed_date:
                        current_date = parsed_date
            
            if not current_date:
                continue
            
            # Check for lesson number
            lesson_number = None
            
            # Check pair column
            if pair_column is not None and pair_column < len(row):
                cell = row[pair_column]
                if cell and isinstance(cell, str):
                    cell_str = str(cell).strip()
                    # Look for Roman numerals
                    match = re.search(r'(I{1,3}|IV|V|VI|VII)\s*пара', cell_str)
                    if match:
                        roman = match.group(1)
                        if roman == 'I':
                            lesson_number = 1
                        elif roman == 'II':
                            lesson_number = 2
                        elif roman in self.LESSON_NUMBERS:
                            lesson_number = self.LESSON_NUMBERS[roman]
            
            if lesson_number is None:
                continue
            
            # Parse schedule for each group
            for col_idx, group_name in group_columns.items():
                if col_idx >= len(row):
                    continue
                
                # Get subject
                subject = None
                room = None
                
                cell_value = row[col_idx]
                if cell_value:
                    cell_str = str(cell_value).strip()
                    if cell_str and cell_str not in ['nan', 'None', '', 'ауд.', 'ауд']:
                        subject = cell_str
                
                # Get room (next column after subject)
                if col_idx + 1 < len(row):
                    room_value = row[col_idx + 1]
                    if room_value:
                        room_str = str(room_value).strip()
                        if room_str and room_str not in ['nan', 'None', '', 'ауд.', 'ауд']:
                            room = room_str
                
                # Only add if there's a subject
                if subject:
                    schedule_entries.append({
                        'group_name': group_name,
                        'base': base,
                        'course': course,
                        'date': current_date,
                        'day_of_week': current_day or '',
                        'lesson_number': lesson_number,
                        'subject': subject,
                        'teacher': None,  # Teacher info usually in next row
                        'room': room
                    })
        
        return schedule_entries
    
    def _parse_date(self, date_val: Any) -> Optional[str]:
        """Parse date value to string format YYYY-MM-DD"""
        if not date_val:
            return None
        
        try:
            # If it's already a datetime object
            if hasattr(date_val, 'strftime'):
                return date_val.strftime('%Y-%m-%d')
            
            # Try parsing string
            date_str = str(date_val).strip()
            
            # Try different date formats
            formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse date: {date_val}, error: {e}")
            return None


async def parse_schedule_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse a schedule file and return schedule data"""
    parser = ScheduleParser(file_path)
    return await parser.parse()
