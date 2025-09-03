from typing import Dict, Any
import logging


class PoiExcelServiceBase:
    """Base class for POI Excel export operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_excel_headers(self):
        """Get standardized 58-column headers for Excel export."""
        base = ["type", "properties/typeCode", "sid", "bid", "lvl", "fid", "name", "description", 
                "logo", "images", "tags", "eid", "price", "priceMax", "priceSign", "rating", 
                "ratingMax", "numberOfRatings", "keywords", "email", "phoneNumber", "websiteURL", 
                "orderURL", "orderURLOverrideMode", "bookURL", "bookURLOverrideMode", "menuURL", 
                "menuURLOverrideMode", "extra", "style"]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return base + [f"openningHours_{d}_{f}" for d in days for f in ["open", "close", "isClosed", "isAlwaysOpen"]]

    def _process_poi_to_row(self, feature):
        """Convert a POI feature to CSV row data."""
        p = feature.get("properties", {})
        
        # Basic fields
        row = [
            str(feature.get("type", "")),
            str(p.get("typeCode", "")),
            str(p.get("sid", "")),
            str(p.get("bid", "")),
            str(p.get("lvl", "")),
            str(p.get("fid", "")),
            str(p.get("name", "")),
            str(p.get("description", "")),
            str(p.get("logo", "")),
            str(p.get("images", [])) if p.get("images") else "",
            str(p.get("tags", [])) if p.get("tags") else "",
            str(p.get("eid", "")),
            str(p.get("price", "")),
            str(p.get("priceMax", "")),
            str(p.get("priceSign", "")),
            str(p.get("rating", "")),
            str(p.get("ratingMax", "")),
            str(p.get("numberOfRatings", "")),
            str(p.get("keywords", [])) if p.get("keywords") else "",
        ]
        
        # Extract contact/URLs from buttons
        contact = {"email": "", "phone": "", "website": "", "order_url": "", "order_override": "FALSE", 
                  "book_url": "", "book_override": "FALSE", "menu_url": "", "menu_override": "FALSE"}
        
        for btn in p.get("buttons", []):
            if not isinstance(btn, dict): continue
            name, action, intent = btn.get("name", ""), btn.get("action", ""), btn.get("intent", "")
            
            if action == "mailto": contact["email"] = intent
            elif action == "tel": contact["phone"] = intent
            elif name == "Website" and action == "href": contact["website"] = intent
            elif name in ["Order", "Book", "Menu"]:
                key = name.lower()
                contact[f"{key}_url"] = intent
                contact[f"{key}_override"] = "TRUE" if action == "custom" else "FALSE"
        
        row.extend([
            str(contact["email"]),
            str(contact["phone"]),
            str(contact["website"]),
            str(contact["order_url"]),
            str(contact["order_override"]),
            str(contact["book_url"]),
            str(contact["book_override"]),
            str(contact["menu_url"]),
            str(contact["menu_override"]),
        ])
        
        # Extra and style
        row.extend([
            str(p.get("extra", {})) if p.get("extra") else "",
            str(p.get("style", {})) if p.get("style") else "",
        ])
        
        # Opening hours for all 7 days
        oh = p.get("openHours", {})
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_hours = oh.get(day, [])
            if day_hours and len(day_hours) > 0 and len(day_hours[0]) >= 2:
                open_time, close_time = day_hours[0][:2]
                is_closed = open_time == close_time == "00:00"
                is_always_open = open_time == close_time and not is_closed
                row.extend([
                    str(open_time),
                    str(close_time),
                    str(is_closed).upper(),
                    str(is_always_open).upper(),
                ])
            else:
                row.extend(["", "", "TRUE", "FALSE"])
        
        return row

    def _convert_to_excel_csv(self, response):
        """Convert API response to Excel-compatible CSV format."""
        headers = self._get_excel_headers()
        return "\n".join(["\t".join(headers)] + ["\t".join(self._process_poi_to_row(f)) for f in response.get("features", [])])
