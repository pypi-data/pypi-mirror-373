from kiosker import KioskerAPI, Blackout
import time
import os

host = os.environ["HOST"]
token = os.environ["TOKEN"]
ssl = os.environ.get("SSL", "false").lower() in ("true", "1", "yes", "on")
verify = os.environ.get("VERIFY", "false").lower() in ("true", "1", "yes", "on")

api = KioskerAPI(host, token, ssl=ssl, verify=verify)

def test_ping():

    result = api.ping()
    
    print(f'Ping: {result}')
    assert result == True

def test_status():
    
    status = api.status()
    
    print('Status:')
    print(f'Device ID: {status.device_id}')
    print(f'Model: {status.model}')
    print(f'OS version: {status.os_version}')
    print(f'Battery level: {status.battery_level}%')
    print(f'Battery state: {status.battery_state}')
    print(f'Last interaction: {status.last_interaction}')
    print(f'Last motion: {status.last_motion}')
    print(f'Ambient light: {status.ambient_light}')
    print(f'Last status update: {status.last_update}')
    print(f'App name: {status.app_name}')
    print(f'App version: {status.app_version}')
    

    assert api.ping() == True

def test_navigate():
    
    print('Navigating to URL...')
    result = api.navigate_url('https://google.com')
    print(f'Navigate URL: {result}')
    
    time.sleep(5)

    print('Navigating to refresh...')
    result = api.navigate_refresh()
    print(f'Navigate refresh: {result}')

    time.sleep(5)
    
    print('Navigating to home...')
    result = api.navigate_home()
    print(f'Navigate home: {result}')

    time.sleep(5)

    print('Navigating to backward...')
    result = api.navigate_backward()
    print(f'Navigate backward: {result}')
    
    time.sleep(5)
    
    print('Navigating to forward...')
    result = api.navigate_forward()
    print(f'Navigate forward: {result}')

    time.sleep(5)

def test_print():
    
    print('Printing...')
    result = api.print()
    print(f'Print: {result}')

    time.sleep(10)
    
def test_clear():
    
    print('Clearing cookies...')
    result = api.clear_cookies()
    print(f'Clear cookies: {result}')

    time.sleep(5)
    
    print('Clearing cache...')
    result = api.clear_cache()
    print(f'Clear cache: {result}')

    time.sleep(5)

def test_screensaver():
    
    print('Interacting with screensaver...')
    result = api.screensaver_interact()
    print(f'Screensaver interact: {result}')

    time.sleep(5)
    
    print('Getting screensaver state...')
    state = api.screensaver_get_state()
    print(f'Screensaver state: {state}')
    
    time.sleep(5)
    
    print('Setting screensaver state to disabled...')
    result = api.screensaver_set_disabled_state(disabled=True)
    print(f'Screensaver set state: {result}')

    time.sleep(5)
    
    print('Getting screensaver state...')
    state = api.screensaver_get_state()
    print(f'Screensaver state: {state}')
    
    time.sleep(5)
    
    print('Setting screensaver state to enabled...')
    result = api.screensaver_set_disabled_state(disabled=False)
    print(f'Screensaver set state: {result}')
    
    time.sleep(5)
    
    print('Getting screensaver state...')
    state = api.screensaver_get_state()
    print(f'Screensaver state: {state}')
        
def test_blackout():
        
    print(f'Blackout state: {api.blackout_get()}')
    
    api.blackout_set(Blackout(visible=True, text='This is a test from Python that should clear', background='#000000', foreground='#FFFFFF', icon='ladybug', expire=20))
    
    time.sleep(5)
    
    print(f'Blackout state: {api.blackout_get()}')
    
    api.blackout_clear()
    
    time.sleep(5)
    
    print(f'Blackout state: {api.blackout_get()}')
    
    time.sleep(1)
    
    api.blackout_set(Blackout(visible=True, text='This is a test from Python', background='#000000', foreground='#FFFFFF', icon='ladybug', expire=20))

    time.sleep(5)
    
    api.blackout_set(Blackout(visible=True, text='This is a change from Python', background='#000000', foreground='#FFFFFF', icon='ladybug', expire=5))

    print(f'Blackout state: {api.blackout_get()}')
    
    time.sleep(7)
    
    print(f'Blackout state: {api.blackout_get()}')
    
    api.blackout_set(Blackout(visible=True, text='This is a test from Python that is dismissible', background='#000000', foreground='#FFFFFF', icon='hand.point.up', expire=25, dismissible=True, buttonBackground='#FA0000', buttonForeground='#FFFFFF', buttonText='Hide me then...', sound="1003"))
    
    time.sleep(5)
