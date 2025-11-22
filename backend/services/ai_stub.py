import re
from datetime import datetime, timedelta
from ..schemas import AIStubResponse

class AIStubService:
    @staticmethod
    def parse_query(query: str) -> AIStubResponse:
        query = query.lower().strip()
        
        # "daily sales from 2024-01-01 to 2024-01-31"
        pattern1 = r"daily sales from (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})"
        match1 = re.search(pattern1, query)
        if match1:
            return AIStubResponse(
                from_date=match1.group(1),
                to_date=match1.group(2),
                intent="date_range",
                query_type="date_range"
            )
        
        # "daily sales last 30 days"
        pattern2 = r"daily sales last (\d+) days?"
        match2 = re.search(pattern2, query)
        if match2:
            days = int(match2.group(1))
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days - 1)
            
            return AIStubResponse(
                from_date=start_date.strftime("%Y-%m-%d"),
                to_date=end_date.strftime("%Y-%m-%d"),
                intent=f"last_{days}_days",
                query_type="summary"
            )
        
        # "sales last week"
        if "last week" in query:
            end_date = datetime.now().date() - timedelta(days=datetime.now().weekday() + 1)
            start_date = end_date - timedelta(days=6)
            
            return AIStubResponse(
                from_date=start_date.strftime("%Y-%m-%d"),
                to_date=end_date.strftime("%Y-%m-%d"),
                intent="last_week",
                query_type="summary"
            )
        
        # "how many sales" or "sales summary"
        if "how many sales" in query or "sales summary" in query or "total sales" in query:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=6)
            
            return AIStubResponse(
                from_date=start_date.strftime("%Y-%m-%d"),
                to_date=end_date.strftime("%Y-%m-%d"),
                intent="sales_summary",
                query_type="summary"
            )
        
        # Default to last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
        
        return AIStubResponse(
            from_date=start_date.strftime("%Y-%m-%d"),
            to_date=end_date.strftime("%Y-%m-%d"),
            intent="default_last_7_days",
            query_type="summary"
        )