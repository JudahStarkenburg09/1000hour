import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.scrollview import ScrollView
from functools import partial
import json
import os
import time
from datetime import datetime, timedelta
import calendar

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Title
        title = Label(
            text='1000 Hour Challenge',
            font_size=dp(24),
            size_hint=(1, 0.2),
            halign='center'
        )
        layout.add_widget(title)
        
        # Buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(1, 0.5))
        
        new_challenge_btn = Button(
            text='Create New Challenge',
            size_hint=(1, None),
            height=dp(60),
            background_color=(0.2, 0.6, 1, 1)
        )
        new_challenge_btn.bind(on_press=self.go_to_create_challenge)
        
        load_challenge_btn = Button(
            text='Load Challenge',
            size_hint=(1, None),
            height=dp(60),
            background_color=(0.2, 0.6, 1, 1)
        )
        load_challenge_btn.bind(on_press=self.go_to_load_challenge)
        
        btn_layout.add_widget(new_challenge_btn)
        btn_layout.add_widget(load_challenge_btn)
        
        layout.add_widget(btn_layout)
        
        # Version info
        version_label = Label(
            text='v1.0.0',
            font_size=dp(12),
            size_hint=(1, 0.1),
            halign='center'
        )
        layout.add_widget(version_label)
        
        self.add_widget(layout)
    
    def go_to_create_challenge(self, instance):
        self.manager.current = 'create_challenge'
    
    def go_to_load_challenge(self, instance):
        load_screen = self.manager.get_screen('load_challenge')
        load_screen.load_challenges()
        self.manager.current = 'load_challenge'

class CreateChallengeScreen(Screen):
    def __init__(self, **kwargs):
        super(CreateChallengeScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Title
        title = Label(
            text='Create New Challenge',
            font_size=dp(24),
            size_hint=(1, 0.2),
            halign='center'
        )
        layout.add_widget(title)
        
        # Challenge name input
        name_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=dp(5))
        name_label = Label(text='Challenge Name:', halign='left', size_hint=(1, 0.3))
        self.name_input = TextInput(
            hint_text='e.g., Electric Guitar Practice',
            multiline=False,
            size_hint=(1, 0.7),
            font_size=dp(18)
        )
        name_layout.add_widget(name_label)
        name_layout.add_widget(self.name_input)
        layout.add_widget(name_layout)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, 0.2))
        
        back_btn = Button(
            text='Back',
            size_hint=(0.5, None),
            height=dp(50),
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        create_btn = Button(
            text='Create',
            size_hint=(0.5, None),
            height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        create_btn.bind(on_press=self.create_challenge)
        
        btn_layout.add_widget(back_btn)
        btn_layout.add_widget(create_btn)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.name_input.text = ''
        self.manager.current = 'home'
    
    def create_challenge(self, instance):
        challenge_name = self.name_input.text.strip()
        if not challenge_name:
            self.show_error_popup("Please enter a challenge name.")
            return
        
        # Create new challenge data
        challenge_data = {
            'name': challenge_name,
            'total_seconds': 0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'daily_logs': {},
            'is_running': False,
            'last_start_time': None
        }
        
        # Save to storage
        store = JsonStore('challenges.json')
        challenge_id = str(int(time.time()))
        store.put(challenge_id, **challenge_data)
        
        # Reset input and go to challenge screen
        self.name_input.text = ''
        challenge_screen = self.manager.get_screen('challenge')
        challenge_screen.load_challenge(challenge_id)
        self.manager.current = 'challenge'
    
    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message))
        
        btn = Button(text='OK', size_hint=(1, None), height=dp(50))
        content.add_widget(btn)
        
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class LoadChallengeScreen(Screen):
    def __init__(self, **kwargs):
        super(LoadChallengeScreen, self).__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Title
        title = Label(
            text='Load Challenge',
            font_size=dp(24),
            size_hint=(1, 0.1),
            halign='center'
        )
        self.layout.add_widget(title)
        
        # Scrollable list of challenges
        self.scroll_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 0.7))
        scroll_view.add_widget(self.scroll_layout)
        self.layout.add_widget(scroll_view)
        
        # Back button
        back_btn = Button(
            text='Back',
            size_hint=(1, 0.1),
            height=dp(50),
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)
    
    def load_challenges(self):
        self.scroll_layout.clear_widgets()
        
        try:
            store = JsonStore('challenges.json')
            if not store.count():
                no_challenges_label = Label(
                    text='No challenges found. Create a new one!',
                    size_hint_y=None,
                    height=dp(50)
                )
                self.scroll_layout.add_widget(no_challenges_label)
                return
            
            for challenge_id in store.keys():
                challenge = store.get(challenge_id)
                
                # Calculate hours and format
                total_hours = challenge['total_seconds'] / 3600
                hours_text = f"{total_hours:.1f} hours"
                
                challenge_btn = Button(
                    text=f"{challenge['name']}\n{hours_text}",
                    size_hint_y=None,
                    height=dp(70),
                    halign='center',
                    valign='middle',
                    background_color=(0.2, 0.6, 1, 1)
                )
                challenge_btn.bind(on_press=partial(self.select_challenge, challenge_id))
                self.scroll_layout.add_widget(challenge_btn)
                
        except Exception as e:
            error_label = Label(
                text=f'Error loading challenges: {str(e)}',
                size_hint_y=None,
                height=dp(50)
            )
            self.scroll_layout.add_widget(error_label)
    
    def select_challenge(self, challenge_id, instance):
        challenge_screen = self.manager.get_screen('challenge')
        challenge_screen.load_challenge(challenge_id)
        self.manager.current = 'challenge'
    
    def go_back(self, instance):
        self.manager.current = 'home'

class ChallengeScreen(Screen):
    challenge_id = StringProperty('')
    challenge_name = StringProperty('')
    timer_text = StringProperty('0:00:00')
    total_seconds = NumericProperty(0)
    is_running = BooleanProperty(False)
    last_start_time = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(ChallengeScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Challenge name
        self.name_label = Label(
            text='Challenge Name',
            font_size=dp(24),
            size_hint=(1, 0.1),
            halign='center'
        )
        layout.add_widget(self.name_label)
        
        # Timer display
        self.timer_label = Label(
            text='0:00:00',
            font_size=dp(40),
            size_hint=(1, 0.2),
            halign='center'
        )
        layout.add_widget(self.timer_label)
        
        # Progress toward 1000 hours
        self.progress_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.1))
        self.progress_label = Label(
            text='Progress: 0 / 1000 hours (0%)',
            font_size=dp(18),
            halign='center'
        )
        self.progress_layout.add_widget(self.progress_label)
        layout.add_widget(self.progress_layout)
        
        # Timer controls
        controls_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, 0.15))
        
        self.play_pause_btn = Button(
            text='Start',
            size_hint=(1, 1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.play_pause_btn.bind(on_press=self.toggle_timer)
        controls_layout.add_widget(self.play_pause_btn)
        
        layout.add_widget(controls_layout)
        
        # Navigation buttons
        nav_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, 0.15))
        
        calendar_btn = Button(
            text='Calendar View',
            size_hint=(0.5, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        calendar_btn.bind(on_press=self.go_to_calendar)
        
        delete_btn = Button(
            text='Delete Challenge',
            size_hint=(0.5, 1),
            background_color=(0.9, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_press=self.confirm_delete)
        
        nav_layout.add_widget(calendar_btn)
        nav_layout.add_widget(delete_btn)
        layout.add_widget(nav_layout)
        
        # Back button
        back_btn = Button(
            text='Back to Challenges',
            size_hint=(1, 0.1),
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        
        # Start the timer update
        Clock.schedule_interval(self.update_timer, 1)
    
    def load_challenge(self, challenge_id):
        self.challenge_id = challenge_id
        store = JsonStore('challenges.json')
        challenge = store.get(challenge_id)
        
        self.challenge_name = challenge['name']
        self.name_label.text = self.challenge_name
        
        self.total_seconds = challenge['total_seconds']
        self.update_timer_display()
        
        self.is_running = challenge.get('is_running', False)
        if self.is_running:
            last_start = challenge.get('last_start_time')
            if last_start:
                # Calculate elapsed time since last start
                elapsed = int(time.time()) - int(last_start)
                self.total_seconds += elapsed
                # Update the last start time to now
                self.last_start_time = int(time.time())
                self.save_challenge_data()
            self.play_pause_btn.text = 'Pause'
            self.play_pause_btn.background_color = (0.9, 0.5, 0.1, 1)
        else:
            self.play_pause_btn.text = 'Start'
            self.play_pause_btn.background_color = (0.2, 0.8, 0.2, 1)
            self.last_start_time = 0
    
    def update_timer_display(self):
        hours = int(self.total_seconds / 3600)
        minutes = int((self.total_seconds % 3600) / 60)
        seconds = int(self.total_seconds % 60)
        
        self.timer_text = f"{hours}:{minutes:02d}:{seconds:02d}"
        self.timer_label.text = self.timer_text
        
        # Update progress
        progress_percent = min(100, (self.total_seconds / 3600) / 10)
        self.progress_label.text = f"Progress: {self.total_seconds / 3600:.1f} / 1000 hours ({progress_percent:.1f}%)"
    
    def update_timer(self, dt):
        if self.is_running:
            self.total_seconds += 1
            self.update_timer_display()
    
    def toggle_timer(self, instance):
        self.is_running = not self.is_running
        
        if self.is_running:
            self.play_pause_btn.text = 'Pause'
            self.play_pause_btn.background_color = (0.9, 0.5, 0.1, 1)
            self.last_start_time = int(time.time())
        else:
            self.play_pause_btn.text = 'Start'
            self.play_pause_btn.background_color = (0.2, 0.8, 0.2, 1)
            self.last_start_time = 0
            
            # Log today's progress
            self.log_daily_progress()
        
        self.save_challenge_data()
    
    def log_daily_progress(self):
        store = JsonStore('challenges.json')
        challenge = store.get(self.challenge_id)
        
        today = datetime.now().strftime('%Y-%m-%d')
        daily_logs = challenge.get('daily_logs', {})
        
        # Add today's time to the log
        if today in daily_logs:
            daily_logs[today] += self.total_seconds - challenge['total_seconds']
        else:
            daily_logs[today] = self.total_seconds - challenge['total_seconds']
        
        challenge['daily_logs'] = daily_logs
        store.put(self.challenge_id, **challenge)
    
    def save_challenge_data(self):
        store = JsonStore('challenges.json')
        challenge = store.get(self.challenge_id)
        
        challenge['total_seconds'] = self.total_seconds
        challenge['is_running'] = self.is_running
        challenge['last_start_time'] = self.last_start_time if self.is_running else None
        
        store.put(self.challenge_id, **challenge)
    
    def go_to_calendar(self, instance):
        calendar_screen = self.manager.get_screen('calendar')
        calendar_screen.load_challenge_data(self.challenge_id)
        self.manager.current = 'calendar'
    
    def confirm_delete(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=f"Are you sure you want to delete '{self.challenge_name}'?"))
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(1, 0.4))
        
        cancel_btn = Button(text='Cancel', size_hint=(0.5, 1))
        confirm_btn = Button(text='Delete', size_hint=(0.5, 1), background_color=(0.9, 0.2, 0.2, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.4))
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.delete_challenge(popup))
        
        popup.open()
    
    def delete_challenge(self, popup):
        popup.dismiss()
        
        store = JsonStore('challenges.json')
        store.delete(self.challenge_id)
        
        self.go_back(None)
    
    def go_back(self, instance):
        # Make sure to save the current state before leaving
        if self.is_running:
            self.toggle_timer(None)
        else:
            self.save_challenge_data()
        
        self.manager.current = 'load_challenge'
        load_screen = self.manager.get_screen('load_challenge')
        load_screen.load_challenges()

class CalendarScreen(Screen):
    challenge_id = StringProperty('')
    challenge_name = StringProperty('')
    current_month = NumericProperty(0)
    current_year = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(CalendarScreen, self).__init__(**kwargs)
        
        self.layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Title and month navigation
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        self.prev_month_btn = Button(
            text='<',
            size_hint=(0.15, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.prev_month_btn.bind(on_press=self.previous_month)
        
        self.month_label = Label(
            text='Month Year',
            font_size=dp(20),
            size_hint=(0.7, 1),
            halign='center'
        )
        
        self.next_month_btn = Button(
            text='>',
            size_hint=(0.15, 1),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.next_month_btn.bind(on_press=self.next_month)
        
        header_layout.add_widget(self.prev_month_btn)
        header_layout.add_widget(self.month_label)
        header_layout.add_widget(self.next_month_btn)
        
        self.layout.add_widget(header_layout)
        
        # Challenge name
        self.name_label = Label(
            text='Challenge Name',
            font_size=dp(18),
            size_hint=(1, 0.05),
            halign='center'
        )
        self.layout.add_widget(self.name_label)
        
        # Calendar grid
        self.calendar_layout = GridLayout(cols=7, spacing=dp(2), size_hint=(1, 0.6))
        
        # Add day headers
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.calendar_layout.add_widget(Label(text=day, size_hint_y=None, height=dp(30)))
        
        self.layout.add_widget(self.calendar_layout)
        
        # Stats section
        stats_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=dp(5))
        
        self.monthly_total_label = Label(
            text='Monthly Total: 0 hours',
            font_size=dp(16),
            halign='center'
        )
        
        self.monthly_avg_label = Label(
            text='Daily Average: 0 hours',
            font_size=dp(16),
            halign='center'
        )
        
        stats_layout.add_widget(self.monthly_total_label)
        stats_layout.add_widget(self.monthly_avg_label)
        
        self.layout.add_widget(stats_layout)
        
        # Back button
        back_btn = Button(
            text='Back to Challenge',
            size_hint=(1, 0.1),
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)
        
        # Initialize current month and year
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year
    
    def load_challenge_data(self, challenge_id):
        self.challenge_id = challenge_id
        store = JsonStore('challenges.json')
        challenge = store.get(challenge_id)
        
        self.challenge_name = challenge['name']
        self.name_label.text = self.challenge_name
        
        self.daily_logs = challenge.get('daily_logs', {})
        
        # Reset to current month
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year
        
        self.update_calendar()
    
    def update_calendar(self):
        # Clear existing calendar cells
        self.calendar_layout.clear_widgets()
        
        # Add day headers
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.calendar_layout.add_widget(Label(text=day, size_hint_y=None, height=dp(30)))
        
        # Update month label
        month_name = calendar.month_name[self.current_month]
        self.month_label.text = f"{month_name} {self.current_year}"
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Track monthly stats
        monthly_total_seconds = 0
        days_with_activity = 0
        
        # Fill calendar with day cells
        for week in cal:
            for day in week:
                if day == 0:
                    # Empty cell for days not in this month
                    self.calendar_layout.add_widget(Label(text='', size_hint_y=None, height=dp(50)))
                else:
                    # Format the date string to match our log format
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    
                    # Get hours for this day if any
                    day_seconds = 0
                    if date_str in self.daily_logs:
                        day_seconds = self.daily_logs[date_str]
                        monthly_total_seconds += day_seconds
                        days_with_activity += 1
                    
                    day_hours = day_seconds / 3600
                    
                    # Create day cell with hours if any
                    if day_seconds > 0:
                        cell = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50))
                        day_label = Label(text=str(day), size_hint=(1, 0.4))
                        hours_label = Label(
                            text=f"{day_hours:.1f}h",
                            size_hint=(1, 0.6),
                            color=(0.2, 0.8, 0.2, 1) if day_hours > 0 else (1, 1, 1, 1)
                        )
                        cell.add_widget(day_label)
                        cell.add_widget(hours_label)
                        self.calendar_layout.add_widget(cell)
                    else:
                        self.calendar_layout.add_widget(Label(text=str(day), size_hint_y=None, height=dp(50)))
        
        # Update stats
        monthly_total_hours = monthly_total_seconds / 3600
        self.monthly_total_label.text = f"Monthly Total: {monthly_total_hours:.1f} hours"
        
        if days_with_activity > 0:
            daily_avg = monthly_total_hours / days_with_activity
            self.monthly_avg_label.text = f"Daily Average: {daily_avg:.1f} hours"
        else:
            self.monthly_avg_label.text = "Daily Average: 0 hours"
    
    def previous_month(self, instance):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()
    
    def next_month(self, instance):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()
    
    def go_back(self, instance):
        self.manager.current = 'challenge'

class ThousandHourApp(App):
    def build(self):
        # Set up screen manager
        sm = ScreenManager()
        
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CreateChallengeScreen(name='create_challenge'))
        sm.add_widget(LoadChallengeScreen(name='load_challenge'))
        sm.add_widget(ChallengeScreen(name='challenge'))
        sm.add_widget(CalendarScreen(name='calendar'))
        
        # Ensure the data directory exists
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
        
        return sm

if __name__ == '__main__':
    ThousandHourApp().run()

