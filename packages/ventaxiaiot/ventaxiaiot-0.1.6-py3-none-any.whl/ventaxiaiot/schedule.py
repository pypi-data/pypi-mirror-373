from typing import Dict, Optional
from dataclasses import dataclass, field

@dataclass
class Schedule:
    
    # Timer/schedule fields
    ts_raw: Dict[str, int] = field(default_factory=dict)   # raw int values
    ts_decoded: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)  
    # Each entry: { "from": "HH:MM", "to": "HH:MM", "days": "Mon,Tue", "mode": "Boost" }  
       
    shrs_raw: Optional[int] = None
    silent_hours_decoded: Dict[str, Optional[str]] = field(default_factory=dict)      
    
    DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    MODE_MAP = {
        0b001: "Normal",
        0b010: "Low",
        0b011: "Boost",
        0b100: "Purge",
    }   
        
    def minutes_to_hhmm(self, mins: int) -> str:
        """Convert minute count to HH:MM (wraps at 24h)."""
        # mins = mins % (24 * 60)
        h = mins // 60
        m = mins % 60
        return f"{h:02d}:{m:02d}"    

    def decode_ts_field(self, ts_name: str, ts_val: int, is_ts: bool = True) -> None:
        """Decode a tsN field and update state_obj.ts_raw and state_obj.ts_decoded."""
        # Save raw value
        decoded: Dict[str, Optional[str]]        
        
        if is_ts:
            self.ts_raw[ts_name] = ts_val
            decoded = self.ts_decoded.setdefault(ts_name, {})
        else:
            self.shrs_raw = ts_val
            decoded = self.silent_hours_decoded or {}
            self.silent_hours_decoded = decoded


        # Ensure 32-bit view
        bin32 = format(ts_val & 0xFFFFFFFF, '032b')

        # Slice groups: days (0:7), time_to (7:18), time_from (18:29), mode (29:32)
        days_bits_s  = bin32[0:7]
        time_to_s    = bin32[7:18]
        time_from_s  = bin32[18:29]
        mode_s       = bin32[29:32]

        days_bits = int(days_bits_s, 2)
        time_to_val = int(time_to_s, 2)
        time_from_val = int(time_from_s, 2)
        mode_bits = int(mode_s, 2)

        # Convert times
        time_from = self.minutes_to_hhmm(time_from_val)
        time_to   = self.minutes_to_hhmm(time_to_val)

        # Days decode
        if days_bits == 0b1111111:
            days_str = "Every day"
        else:
            days = [self.DAY_NAMES[i] for i in range(7) if (days_bits >> i) & 1]
            days_str = ",".join(days) if days else "None"

        # Mode decode
        mode_str = self.MODE_MAP.get(mode_bits, f"Unknown({mode_bits:#03b})")

        decoded["from"] = time_from
        decoded["to"] = time_to
        decoded["days"] = days_str
        decoded["mode"] = mode_str

 