from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.recycleview import RecycleView
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

class TaskItem(BoxLayout):
    def __init__(self, task_text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 40

        self.checkbox = CheckBox(size_hint_x=0.1)
        self.add_widget(self.checkbox)

        self.label = Label(text=task_text, size_hint_x=0.9)
        self.add_widget(self.label)

class TaskList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
    
    def add_task(self, task_text):
        self.data.append({'text': task_text})
        self.refresh_from_data()

class PomodoroApp(App):
    def build(self):
        self.study_time = 40 * 60  # Default study time is 40 minutes in seconds
        self.rest_time = 10 * 60  # Default rest time is 10 minutes in seconds
        self.current_time = self.study_time
        self.is_study = True  # Boolean to track if it's study or rest time
        self.timer_running = False

        # Create UI layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Label for showing the timer
        self.timer_label = Label(text=self.format_time(self.current_time), font_size=40)
        layout.add_widget(self.timer_label)
        
        # Study and Rest input fields
        layout.add_widget(Label(text="Set Study Time (in minutes):"))
        self.study_input = TextInput(text="40", multiline=False)
        layout.add_widget(self.study_input)
        
        layout.add_widget(Label(text="Set Rest Time (in minutes):"))
        self.rest_input = TextInput(text="10", multiline=False)
        layout.add_widget(self.rest_input)
        
        # Start Button
        self.start_button = Button(text="Start Timer")
        self.start_button.bind(on_press=self.start_timer)
        layout.add_widget(self.start_button)
        
        # Stop Alarm Button
        self.stop_alarm_button = Button(text="Stop Alarm", disabled=True)
        self.stop_alarm_button.bind(on_press=self.stop_alarm)
        layout.add_widget(self.stop_alarm_button)

        # Task Input and Add Button
        layout.add_widget(Label(text="Task List:"))
        task_layout = BoxLayout(size_hint_y=None, height=40)
        self.task_input = TextInput(text="", multiline=False, size_hint_x=0.8)
        task_layout.add_widget(self.task_input)
        add_task_button = Button(text="Add Task", size_hint_x=0.2)
        add_task_button.bind(on_press=self.add_task)
        task_layout.add_widget(add_task_button)
        layout.add_widget(task_layout)

        # Task List (RecycleView to hold task items)
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        layout.add_widget(self.task_list)

        # Load alarm sound
        self.alarm_sound = SoundLoader.load('alarm.mp3')  # Make sure to have an alarm.mp3 file

        return layout

    def format_time(self, seconds):
        """Helper function to format time into mm:ss."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def start_timer(self, instance):
        """Start the countdown timer."""
        if not self.timer_running:
            self.timer_running = True
            self.start_button.text = "Pause Timer"
            # Update study and rest times based on user input
            self.study_time = int(self.study_input.text) * 60
            self.rest_time = int(self.rest_input.text) * 60
            self.current_time = self.study_time if self.is_study else self.rest_time
            self.timer_event = Clock.schedule_interval(self.update_time, 1)  # Update every second
        else:
            self.timer_running = False
            self.start_button.text = "Start Timer"
            Clock.unschedule(self.timer_event)

    def update_time(self, dt):
        """Update the countdown timer."""
        if self.current_time > 0:
            self.current_time -= 1
            self.timer_label.text = self.format_time(self.current_time)
        else:
            self.trigger_alarm()

    def trigger_alarm(self):
        """Trigger the alarm and stop the timer."""
        if self.alarm_sound:
            self.alarm_sound.play()
        self.timer_running = False
        self.start_button.disabled = True
        self.stop_alarm_button.disabled = False

    def stop_alarm(self, instance):
        """Stop the alarm and switch between study and rest periods."""
        if self.alarm_sound:
            self.alarm_sound.stop()

        # Switch to the other mode (study or rest)
        self.is_study = not self.is_study
        self.current_time = self.study_time if self.is_study else self.rest_time
        self.timer_label.text = self.format_time(self.current_time)

        # Enable/disable buttons accordingly
        self.start_button.disabled = False
        self.stop_alarm_button.disabled = True

    def add_task(self, instance):
        """Add a new task to the task list."""
        task_text = self.task_input.text.strip()
        if task_text:  # Only add non-empty tasks
            task_item = TaskItem(task_text=task_text)
            self.task_list.add_widget(task_item)
            self.task_input.text = ""  # Clear input field after adding task

# Run the app
if __name__ == '__main__':
    PomodoroApp().run()