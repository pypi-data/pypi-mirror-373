from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Status:
    battery_level: int
    battery_state: str
    model: str
    os_version: str
    app_name: str
    app_version: str
    last_interaction: datetime
    last_update: datetime
    device_id: str
    last_motion: Optional[datetime]
    ambient_light: Optional[float]
    
    @classmethod
    def from_dict(cls, status_data):
        return cls(battery_level=status_data['batteryLevel'], battery_state=status_data['batteryState'], model=status_data['model'], os_version=status_data['osVersion'], app_name=status_data['appName'], app_version=status_data['appVersion'], last_interaction=datetime.fromisoformat(status_data['lastInteraction']), last_motion=datetime.fromisoformat(status_data['lastMotion']) if status_data.get('lastMotion') else None, last_update=datetime.fromisoformat(status_data['date']), device_id=status_data['deviceId'], ambient_light=status_data['ambientLight'] if status_data.get('ambientLight') else None)

@dataclass
class Result:
    error: bool
    reason: Optional[str]
    function: Optional[str]
    
    @classmethod
    def from_dict(cls, result_data):
        return cls(error=result_data['error'], reason=result_data['reason'] if result_data.get('reason') else None , function=result_data.get('function') if result_data.get('function') else None)

@dataclass
class ScreensaverState:
    visible: bool
    disabled: bool
    
    @classmethod
    def from_dict(cls, state_data):
        return cls(visible=state_data['visible'], disabled=state_data['disabled'])

        
@dataclass
class Blackout:
    visible: bool
    background: Optional[str] = None
    foreground: Optional[str] = None
    expire: Optional[int] = None
    text: Optional[str] = None
    icon: Optional[str] = None
    dismissible: Optional[bool] = False
    buttonBackground: Optional[str] = None
    buttonForeground: Optional[str] = None
    buttonText: Optional[str] = None
    sound: Optional[str] = None

    def to_dict(self):
        return {
            'visible': self.visible,
            'background': self.background,
            'foreground': self.foreground,
            'expire': self.expire,
            'text': self.text,
            'icon': self.icon,
            'dismissible': self.dismissible,
            'buttonBackground': self.buttonBackground,
            'buttonForeground': self.buttonForeground,
            'buttonText': self.buttonText,
            'sound': self.sound,
        }

    @classmethod
    def from_dict(cls, blackout_data):
        return cls(
            visible=blackout_data['visible'],
            background=blackout_data['background'],
            foreground=blackout_data['foreground'],
            expire=blackout_data['expire'],
            text=blackout_data.get('text'),
            icon=blackout_data.get('icon'),
            dismissible=blackout_data.get('dismissible', False),
            buttonBackground=blackout_data.get('buttonBackground'),
            buttonForeground=blackout_data.get('buttonForeground'),
            buttonText=blackout_data.get('buttonText'),
            sound=blackout_data.get('sound'),
        )
