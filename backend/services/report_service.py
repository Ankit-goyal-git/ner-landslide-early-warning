import uuid
from datetime import datetime
from typing import List, Dict, Any
from backend.models.schemas import CitizenReportCreate, CitizenReport

class ReportService:
    def __init__(self):
        self.reports: List[Dict[str, Any]] = []
        self.seed_initial_reports()
        
    def seed_initial_reports(self):
        initial = [
            {
                "id": "RPT-101",
                "latitude": 27.3341,
                "longitude": 88.6083,
                "state": "Sikkim",
                "report_type": "crack",
                "severity": "HIGH",
                "description": "Visible longitudinal tension crack expanding along road edge near Pani House, Gangtok.",
                "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=400&q=80",
                "timestamp": "2026-09-01 18:30:00",
                "reporter_name": "Tashi Bhutia (Local Resident)",
                "status": "VERIFIED"
            },
            {
                "id": "RPT-102",
                "latitude": 25.5215,
                "longitude": 93.1645,
                "state": "Assam",
                "report_type": "slope movement",
                "severity": "CRITICAL",
                "description": "Mud sludge and rock fragments shifting towards railway track cutting near Lumding-Badarpur route.",
                "image_url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=400&q=80",
                "timestamp": "2026-09-01 21:15:00",
                "reporter_name": "R. K. Sharma (Track Inspector)",
                "status": "VERIFIED"
            },
            {
                "id": "RPT-103",
                "latitude": 24.7505,
                "longitude": 93.4221,
                "state": "Manipur",
                "report_type": "road blockage",
                "severity": "HIGH",
                "description": "Minor rockfall blocking half carriageway on NH-37 near Nungba.",
                "image_url": "",
                "timestamp": "2026-09-02 00:45:00",
                "reporter_name": "M. Singh (Driver)",
                "status": "INVESTIGATING"
            }
        ]
        self.reports.extend(initial)
        
    def get_all_reports(self, report_type: str = None, state: str = None) -> List[Dict[str, Any]]:
        results = self.reports
        if report_type and report_type.lower() != 'all':
            results = [r for r in results if r['report_type'].lower() == report_type.lower()]
        if state and state.lower() != 'all':
            results = [r for r in results if r.get('state', '').lower() == state.lower()]
        return results

    def add_report(self, report: CitizenReportCreate) -> Dict[str, Any]:
        new_report = report.model_dump()
        new_report['id'] = f"RPT-{str(uuid.uuid4())[:6].upper()}"
        new_report['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_report['status'] = "SUBMITTED"
        if not new_report.get('state'):
            new_report['state'] = "Assam"
        self.reports.insert(0, new_report)
        return new_report

report_service = ReportService()
