# File: ventaxiaiot/sentinel_kinetic.py

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
import logging

from ventaxiaiot.pending_request_tracker import PendingRequestTracker
from ventaxiaiot.schedule import Schedule

_LOGGER = logging.getLogger(__name__)

@dataclass
class SentinelKinetic:
    # Metadata
    m: Optional[str] = None  # message type
    t: Optional[str] = None  # topic
    i: Optional[int] = None  # message ID
    
    # Core operational state
    ar_af: Optional[int] = None  # User Airflow mode: 1=low, 2=normal, 3=boost, 4=purge 
    ar_min: Optional[int] = None  # Boost duration
    ts: Optional[int] = None  # Device timestamp (UNIX)

    # Environmental sensors
    temp_indoor: Optional[float] = None
    temp_outdoor: Optional[float] = None
    humidity: Optional[float] = None

    # Config / network status
    netmode: Optional[str] = None
    wifi_signal: Optional[int] = None

    # Device flags / identifiers
    serial: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None

    # Raw message cache (for optional access)
    # last_update: datetime = field(default_factory=datetime.utcnow)
    # last_raw: Dict[str, Any] = field(default_factory=dict)  
    
    # Realtime status
    set_rtc: Optional[str] = None
    cm_af_sup: Optional[int] = None # supply air  flow
    cm_af_exh: Optional[int] = None # exhust  air  flow
    hand: Optional[int] = None

    # Airflow stages
    af1sup: Optional[int] = None
    af1exh: Optional[int] = None
    af2sup: Optional[int] = None
    af2exh: Optional[int] = None
    af3sup: Optional[int] = None
    af3exh: Optional[int] = None
    af4sup: Optional[int] = None
    af4exh: Optional[int] = None

    # Identification
    dname: Optional[str] = None
    svcpn: Optional[str] = None
    loc: Optional[str] = None

    # Airflow settings
    af_ls1: Optional[int] = None
    af_sw1: Optional[int] = None
    af_p1: Optional[int] = None
    af_p2: Optional[int] = None
    af_irh: Optional[int] = None
    af_do: Optional[int] = None
    

    # Logic switches and timers
    ls1o: Optional[int] = None
    ls1d: Optional[int] = None
    sw1t: Optional[int] = None
    p1t: Optional[int] = None
    p2t: Optional[int] = None

    # Preset thresholds
    p1a_lo: Optional[int] = None
    p1a_hi: Optional[int] = None
    p1b_lo: Optional[int] = None
    p1b_hi: Optional[int] = None
    p1c_lo: Optional[int] = None
    p1c_hi: Optional[int] = None

    p2a_lo: Optional[int] = None
    p2a_hi: Optional[int] = None
    p2b_lo: Optional[int] = None
    p2b_hi: Optional[int] = None
    p2c_lo: Optional[int] = None
    p2c_hi: Optional[int] = None

    irh_sp: Optional[int] = None

     # Summer bypass data
    m_byp: Optional[int] = None # bypass mode
    by_ti: Optional[int] = None # indoor temp
    by_to: Optional[int] = None # outdoor temp
    af_enp: Optional[int] = None # goto mode


    # Device mode and runtime
    m_ctl: Optional[int] = None
    m_afr: Optional[int] = None   
    flife: Optional[int] = None

    # Settings & Flags
    btn_en: Optional[int] = None
    moda: Optional[int] = None
    ctry: Optional[int] = None
    cfgf: Optional[int] = None
    svci: Optional[int] = None

    # Relay flags
    rlf1: Optional[int] = None
    rlf2: Optional[int] = None
    rlf1sp: Optional[int] = None
    rlf2sp: Optional[int] = None
    
        # Firmware / Info
    swver: Optional[int] = None
    wfver: Optional[int] = None
    mser: Optional[int] = None
    rtc: Optional[str] = None
    su_ver: Optional[int] = None

    # Runtime & diagnostics
    runh: Optional[int] = None
    shrem: Optional[int] = None
    fhrem: Optional[int] = None
    bfit: Optional[int] = None
    fl_l: Optional[int] = None
    fl_r: Optional[int] = None

    # Airflow/Temp/Humidity Sensors
    exr_rh: Optional[int] = None
    itk_rh: Optional[int] = None
    exr_t: Optional[int] = None
    itk_t: Optional[int] = None
    sup_t: Optional[int] = None
    exh_t: Optional[int] = None
    exr_thm: Optional[int] = None
    itk_thm: Optional[int] = None
    exr_sen: Optional[int] = None
    itk_sen: Optional[int] = None
    exr_f: Optional[int] = None
    itk_f: Optional[int] = None
    exr_ft: Optional[int] = None
    itk_ft: Optional[int] = None
    exr_cp: Optional[int] = None
    itk_cp: Optional[int] = None

    sup_pwm: Optional[int] = None
    exh_pwm: Optional[int] = None
    sup_rpm: Optional[int] = None  # supply rpm
    exh_rpm: Optional[int] = None  # exhust rpm 

    # Control & status
    mstat: Optional[int] = None
    byp: Optional[int] = None
    mflags: Optional[int] = None
    mdl_afu: Optional[int] = None

    # Auto-settings
    as_af: Optional[int] = None  # User Airflow mode: 1=low, 2=normal, 3=boost, 4=purge  
    as_ts: Optional[str] = None
    as_rsec: Optional[int] = None 
    as_oa: Optional[int] = None
    as_os: Optional[int] = None

    # Power
    pwr: Optional[int] = None #Power as a %
    afr_m: Optional[int] = None
    afr_php: Optional[int] = None

    # Server
    svr_conn: Optional[int] = None
    svrerr: Optional[int] = None
    svrstat: Optional[int] = None
    cmsrc: Optional[int] = None

    # Mode names
    mn: List[Optional[str]] = field(default_factory=lambda: [None]*16)
    
    # new schedules field
    _schedules: Schedule = field(default_factory=Schedule)
    
    timer_started_at: Optional[datetime] = None  # wall-clock when Boost timer began
    
    AIRFLOW_MODES = {
        "reset": 0, # This stops the current user requested airflow mode
        "normal": 1,
        "low": 2,
        "boost": 3,
        "purge": 4,
    }
    
    BYPASS_MODES = {
        0: "Off",
        1: "Normal",
        2: "Evening fresh",
        3: "Night fresh",
    }

    AF_ENP_MODES = {        
        1: "Normal",  
        2: "Low",     
        3: "Boost",
        4: "Purge",
    }
        
    VALID_DURATIONS = {0,15, 30, 45, 60} # 0 is sent with "reset": 0 to stop the current user requested airflow mode  
    # Approximate average days per month
    DAYS_PER_MONTH = 30.44    
    # Step 2.5: Decode ts1–ts27 (ignore empty/garbage)
    MIN_VALID_TS = 33_554_432    

    def apply_payload(self, data: Any,tracker : PendingRequestTracker):
        """Initialize or update the instance with nested or flat payload, handling mn0–mn15."""
        try:
            # Step 0: If input is a raw JSON string, try to parse it
            if isinstance(data, str):
                data = json.loads(data)
                
            # Step 0.5: Handle response metadata and assign to self
            msg_id = data.get("i")
            if msg_id is not None:
                meta = tracker.pop(msg_id) 
                if meta:
                    _LOGGER.debug(f"✅ Matched metadata for msg_id {msg_id}: {meta}")
                    key = meta.get("cfgcmd")
                    value = data.get("r")
                    if key and value is not None:
                        # Clean up key (e.g., "netmode?" → "netmode")
                        clean_key = key.rstrip("?")
                        _LOGGER.debug(f"Setting attribute: {clean_key} = {value}")
                        setattr(self, clean_key, value)    
                        return  # ✅ Done — no need to process further
                

            # Step 1: Unwrap nested keys if present
            if isinstance(data, dict):
                flat_data = data.get('d') or data.get('r') or data
            else:
                raise ValueError(f"Unexpected data type: {type(data)}")
            
            # Step 2.1: Define fields to ignore (e.g., internal timestamps)           
            IGNORED_FIELDS = {
                "mlang", "diag", "ls", "sw", "ps1", "ps2", "dsav", "warn", "secpin",
                "byp_ept", "afmax", "afcnt", "f90", "brid"
            }            

            # Step 2: Extract mn0–mn15 into a list and assign to `mn`
            mn_list = [flat_data.get(f'mn{i}') for i in range(16)]
            if any(v is not None for v in mn_list):
                self.mn = mn_list
                
            # Step 2.5: Decode ts1–ts27 if present
            for i in range(1, 28):
                key = f"ts{i}"
                ts_val = flat_data.get(key)
                if ts_val and isinstance(ts_val, int) and ts_val >= SentinelKinetic.MIN_VALID_TS:
                    try:
                        self._schedules.decode_ts_field(key, ts_val)
                    except Exception as e:
                        _LOGGER.error(f"Failed to decode {key}={ts_val}: {e}") 

            # Step 3: Update all fields defined in the dataclass
            for key, value in flat_data.items():
                if key.startswith("mn") and key[2:].isdigit(): 
                    continue  # already handled in Step 2
                if key.startswith("ts") and key[2:].isdigit():
                    continue  # skip tsN, handled in Step 2.5
                if key == "shrs" and isinstance(value, int) and value >= SentinelKinetic.MIN_VALID_TS:
                    self._schedules.decode_ts_field(key, value, is_ts=False)
                    continue 
                if hasattr(self, key):
                    setattr(self, key, value)
                elif key not in IGNORED_FIELDS:
                    _LOGGER.debug(f"Unknown field ignored: {key}")
                    
            # Step 4: Handle Boost timer start/stop tracking
            if self.as_os == 1 and self.as_rsec and self.as_rsec > 0:
                # Start (or restart) the timer
                if self.timer_started_at is None:
                    self.timer_started_at = datetime.now(timezone.utc)
                    _LOGGER.debug(f"Boost timer started at {self.timer_started_at.isoformat()} " f"for {self.as_rsec}s")
            else:
                # Timer stopped
                if self.timer_started_at is not None:
                    _LOGGER.debug("Boost timer stopped")
                self.timer_started_at = None            

        except Exception as e:
            _LOGGER.error(f"apply_payload failed: {e}")

    @property
    def extract_temp_c(self) -> Optional[float]:
        """Extract (indoor) temperature in Celsius."""
        return self.exr_t / 10 if self.exr_t is not None and self.exr_t > -1000 else None
      
    @property
    def outdoor_temp_c(self) -> Optional[float]:
        """Outdoor (external) temperature in Celsius."""
        return self.itk_t / 10 if self.itk_t is not None and self.itk_t > -1000 else None   

    @property
    def supply_temp_c(self) -> Optional[float]:
        """Supply air temperature in Celsius."""           
        # Check if there's another field for supply temp; if not, maybe None
        if self.sup_t is not None and self.sup_t != -1000:
            return self.sup_t / 10.0
        return None
    
   
    @property
    def manual_airflow_sec(self) -> Optional[int]:
        """Manual Airflow timer Remaining seconds, or None if timer is off."""
        if self.manual_airflow_active:
            return self.as_rsec
        return None

    @property
    def manual_airflow_timer_min(self) -> Optional[float]:
        """Manual Airflow timer remaining in minutes."""
        if self.as_rsec is not None:
            return self.as_rsec / 60.0
        return None 
    
    @property
    def manual_airflow_active(self) -> bool:
        """True if Manual Airflow timer is currently active."""
        return self.as_os == 1 and (self.as_rsec or 0) > 0
    
    @property
    def manual_airflow_end_time(self) -> Optional[datetime]:
        if self.timer_started_at and self.as_rsec and self.as_rsec > 0:
            return self.timer_started_at + timedelta(seconds=self.as_rsec)
        return None
    
    @property
    def manual_airflow_mode(self) -> Optional[str]:
        """Translate airflow setting to a friendly label."""
        manual_airflow_modes = {
            1: "Normal",
            2: "Low",
            3: "Boost",
            4: "Purge"
        }
        return manual_airflow_modes.get(self.as_af) if self.as_af is not None else "Unknown" # type: ignore
            
    @property
    def filter_months_remaining(self) -> Optional[float]:
        """Remaining filter life in months, if available."""
        if self.fhrem is None:
            return None
        return self.fhrem / 24 / SentinelKinetic.DAYS_PER_MONTH
    
    @property
    def service_months_remaining(self) -> Optional[float]:
        """Remaining service interval in months, if available."""
        if self.shrem is None:
            return None
        return self.shrem / 24 / SentinelKinetic.DAYS_PER_MONTH
    
    @property
    def schedules(self) -> Dict[str, Dict[str, Optional[str]]]:
        """Return all decoded schedules (ts1–ts27)."""
        return self._schedules.ts_decoded
    
    @property
    def silent_hours(self) -> Dict[str, Optional[str]]:
        """Return the decoded silent hours."""
        return self._schedules.silent_hours_decoded    
    
    @property
    def summer_bypass_mode(self) -> str:
        if self.m_byp is None:
            return "Unknown"
        return SentinelKinetic.BYPASS_MODES[self.m_byp]

    @property
    def summer_bypass_af_mode(self) -> str:
        if self.af_enp is None:
            return "Unknown(None)"
        return self.AF_ENP_MODES.get(self.af_enp, f"Unknown({self.af_enp})")
    
    @property
    def summer_bypass_indoor_temp(self) -> Optional[float]:
        """Summer bypass indoor temperature in Celsius."""           
        # Check if there's another field for supply temp; if not, maybe None
        return self.by_ti / 10 if self.by_ti is not None and self.by_ti >= -1000 else None    
    
    @property
    def summer_bypass_outdoor_temp(self) -> Optional[float]:
        """Summer bypass outdoor temperature in Celsius."""           
        return self.by_to / 10 if self.by_to is not None and self.by_to >= -1000 else None  
    
    def __str__(self):
        return (
            f"<VentAxiaDevice "
            f"name={self.dname} "
            f"airflow_mode={self.manual_airflow_mode} "
            f"supply={self.sup_rpm} "
            f"exhaust={self.exh_rpm} "
            f"summer_bypass_af_mode={self.summer_bypass_af_mode} "
            f"summer_bypass_mode={self.summer_bypass_mode} "
            f"summer_bypass_indoor_temp={self.summer_bypass_indoor_temp} "
            f"summer_bypass_outdoor_temp={self.summer_bypass_outdoor_temp} " 
            f">"
        )