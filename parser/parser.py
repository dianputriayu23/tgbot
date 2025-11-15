import os
import re
import logging
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from python_calamine import CalamineWorkbook
    CALAMINE_AVAILABLE = True
except ImportError:
    CALAMINE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScheduleParser:
    def __init__(self, download_url: str, storage_path: str = "schedules"):
        self.download_url = download_url
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    async def download_schedule(self, filename: str) -> Optional[str]:
        """Download schedule file from URL"""
        try:
            url = f"{self.download_url}{filename}"
            file_path = os.path.join(self.storage_path, filename)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        logger.info(f"Downloaded schedule: {filename}")
                        return file_path
                    else:
                        logger.error(f"Failed to download {filename}: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading schedule {filename}: {e}")
            return None

    def parse_xlsx(self, file_path: str) -> Dict[str, Any]:
        """Parse XLSX file using calamine or fallback to XML"""
        try:
            if CALAMINE_AVAILABLE:
                return self._parse_with_calamine(file_path)
            else:
                return self._parse_with_xml(file_path)
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {}

    def _parse_with_calamine(self, file_path: str) -> Dict[str, Any]:
        """Parse XLSX using python-calamine"""
        try:
            workbook = CalamineWorkbook.from_path(file_path)
            schedule_data = {}
            
            for sheet_name in workbook.sheet_names:
                logger.info(f"Parsing sheet: {sheet_name}")
                sheet_data = workbook.get_sheet_by_name(sheet_name)
                
                if sheet_data:
                    rows = sheet_data.to_python()
                    parsed_sheet = self._extract_schedule_data(sheet_name, rows)
                    if parsed_sheet:
                        schedule_data[sheet_name] = parsed_sheet
            
            return schedule_data
        except Exception as e:
            logger.error(f"Calamine parsing error: {e}")
            return {}

    def _parse_with_xml(self, file_path: str) -> Dict[str, Any]:
        """Fallback: Parse XLSX as XML (ZIP archive)"""
        import zipfile
        
        try:
            schedule_data = {}
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Extract sheets from workbook
                # This is a simplified fallback - full implementation would parse sharedStrings.xml too
                logger.warning("Using XML fallback parser - limited functionality")
                # For now, return empty dict - full XML parsing is complex
                pass
            
            return schedule_data
        except Exception as e:
            logger.error(f"XML parsing error: {e}")
            return {}

    def _extract_schedule_data(self, sheet_name: str, rows: List[List[Any]]) -> Dict[str, Any]:
        """Extract schedule data from sheet rows"""
        try:
            # Determine course from sheet name
            course = self._determine_course(sheet_name)
            
            # Find groups in headers
            groups = self._find_groups(rows)
            
            # Extract schedule for each day
            schedule = self._extract_daily_schedule(rows, groups)
            
            return {
                "course": course,
                "groups": groups,
                "schedule": schedule
            }
        except Exception as e:
            logger.error(f"Error extracting data from sheet {sheet_name}: {e}")
            return {}

    def _determine_course(self, sheet_name: str) -> int:
        """Determine course number from sheet name"""
        match = re.search(r'(\d+)\s*курс', sheet_name.lower())
        if match:
            return int(match.group(1))
        
        # Check for pattern like "1 курс" or "2 курс" 
        if "1" in sheet_name or "первый" in sheet_name.lower():
            return 1
        elif "2" in sheet_name or "второй" in sheet_name.lower():
            return 2
        elif "3" in sheet_name or "третий" in sheet_name.lower():
            return 3
        
        return 1  # default

    def _find_groups(self, rows: List[List[Any]]) -> List[str]:
        """Find group names in the schedule"""
        groups = []
        
        # Look for groups in first 20 rows
        for row_idx, row in enumerate(rows[:20]):
            for cell in row:
                if isinstance(cell, str):
                    # Match patterns like БУ-25, ТД1-24, Ю1-24(1), etc.
                    matches = re.findall(r'[А-ЯЁ]{1,3}\d?-\d{2}(?:\(\d+\))?', cell)
                    for match in matches:
                        if match not in groups:
                            groups.append(match)
                    
                    # Also check for patterns like Б1-123, Д1-234
                    matches2 = re.findall(r'[А-ЯЁ]\d-\d{2,3}', cell)
                    for match in matches2:
                        if match not in groups:
                            groups.append(match)
        
        logger.info(f"Found groups: {groups}")
        return groups

    def _extract_daily_schedule(self, rows: List[List[Any]], groups: List[str]) -> Dict[str, Any]:
        """Extract daily schedule from rows"""
        daily_schedule = {}
        current_day = None
        
        weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
        
        for row_idx, row in enumerate(rows):
            # Check if row contains a day name
            for cell in row:
                if isinstance(cell, str):
                    cell_lower = cell.lower()
                    for day in weekdays:
                        if day in cell_lower:
                            current_day = day.capitalize()
                            if current_day not in daily_schedule:
                                daily_schedule[current_day] = {}
                            break
            
            # Extract lesson data if we have a current day
            if current_day and len(row) > 5:
                # Look for time patterns like "12:30-13:50" or "III пара"
                time_pattern = r'(\d{1,2}:\d{2}[-–]\d{1,2}:\d{2})|([IVX]+\s*пара)'
                
                for cell in row:
                    if isinstance(cell, str) and re.search(time_pattern, cell):
                        # This row likely contains lesson times
                        lesson_data = self._parse_lesson_row(row, groups)
                        if lesson_data:
                            time_key = cell.strip()
                            daily_schedule[current_day][time_key] = lesson_data
        
        return daily_schedule

    def _parse_lesson_row(self, row: List[Any], groups: List[str]) -> Dict[str, Any]:
        """Parse a row containing lesson information"""
        lesson_data = {}
        
        # Simple extraction - just collect non-empty cells
        for cell in row:
            if cell and str(cell).strip() and str(cell) not in ['nan', 'NaT']:
                # Skip if it's just a number (likely a room number alone)
                cell_str = str(cell).strip()
                if not cell_str.isdigit() or len(cell_str) > 3:
                    lesson_data[len(lesson_data)] = cell_str
        
        return lesson_data if lesson_data else {}

    def cleanup_old_files(self, days: int = 8):
        """Delete files older than specified days"""
        try:
            now = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, filename)
                if os.path.isfile(file_path):
                    file_age = now - datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_age.days > days:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old file: {filename}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old files")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")

    def get_local_schedules(self) -> List[str]:
        """Get list of local schedule files"""
        try:
            files = []
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.xlsx'):
                    files.append(os.path.join(self.storage_path, filename))
            return sorted(files)
        except Exception as e:
            logger.error(f"Error getting local schedules: {e}")
            return []
