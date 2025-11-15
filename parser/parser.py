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
        
        # Search for column headers (groups, dates, days)
        for row_idx, row in enumerate(data[:20]):  # Check first 20 rows
            for col_idx, cell in enumerate(row):
                if cell and isinstance(cell, str):
                    cell_str = str(cell).strip()
                    
                    # Check for date column
                    if 'дата' in cell_str.lower() or 'число' in cell_str.lower():
                        date_column = col_idx
                    
                    # Check for day of week column
                    if 'день' in cell_str.lower():
                        day_column = col_idx
                    
                    # Check for group names (like А-211, Б-311, etc.)
                    if re.match(r'^[А-Я]-\d{3}', cell_str):
                        group_columns[col_idx] = cell_str
        
        if not group_columns:
            logger.warning(f"No groups found in sheet for base {base}, course {course}")
            return schedule_entries
        
        # Parse schedule data
        current_date = None
        current_day = None
        
        for row_idx, row in enumerate(data):
            if row_idx < 10:  # Skip header rows
                continue
            
            # Get date and day
            if date_column is not None and len(row) > date_column:
                date_val = row[date_column]
                if date_val and str(date_val).strip():
                    current_date = self._parse_date(date_val)
            
            if day_column is not None and len(row) > day_column:
                day_val = row[day_column]
                if day_val and isinstance(day_val, str):
                    current_day = day_val.strip()
            
            if not current_date:
                continue
            
            # Check for lesson number in first columns
            lesson_number = None
            for i in range(min(5, len(row))):
                cell = row[i]
                if cell and isinstance(cell, str):
                    cell_str = str(cell).strip()
                    if cell_str in self.LESSON_NUMBERS:
                        lesson_number = self.LESSON_NUMBERS[cell_str]
                        break
                    # Also check for Roman numerals
                    match = re.match(r'^(III|IV|V|VI|VII)$', cell_str)
                    if match:
                        lesson_number = self.LESSON_NUMBERS[match.group(1)]
                        break
            
            if lesson_number is None:
                continue
            
            # Parse schedule for each group
            for col_idx, group_name in group_columns.items():
                if col_idx >= len(row):
                    continue
                
                # Get subject, teacher, and room (usually in consecutive rows or same cell)
                subject = None
                teacher = None
                room = None
                
                cell_value = row[col_idx]
                if cell_value:
                    cell_str = str(cell_value).strip()
                    if cell_str and cell_str != 'nan':
                        # Try to extract subject, teacher, and room
                        lines = cell_str.split('\n')
                        if len(lines) >= 1:
                            subject = lines[0].strip()
                        if len(lines) >= 2:
                            teacher = lines[1].strip()
                        if len(lines) >= 3:
                            room = lines[2].strip()
                        
                        # If not multiline, just use as subject
                        if len(lines) == 1:
                            subject = cell_str
                
                # Only add if there's actual content
                if subject:
                    schedule_entries.append({
                        'group_name': group_name,
                        'base': base,
                        'course': course,
                        'date': current_date,
                        'day_of_week': current_day or '',
                        'lesson_number': lesson_number,
                        'subject': subject,
                        'teacher': teacher,
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
