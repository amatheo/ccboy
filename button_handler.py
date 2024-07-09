from config import ACTION_MAP


class ButtonHandler:
    @staticmethod
    def handle_command(command, emulator):
        if not command:
            return
        command = command.lower()
        if command in ACTION_MAP:
            action = ACTION_MAP[command]
            emulator.press_button(action)
