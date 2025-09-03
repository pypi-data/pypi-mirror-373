from arduino_hid_emulator.arduino import ArduinoConnection
from arduino_hid_emulator.mouse import MouseController

def main():
    # Подключение к Arduino
    arduino = ArduinoConnection()
    mouse = MouseController(arduino)

    # Выполняем калибровку
    try:
        mouse.calibrate()
    except RuntimeError as e:
        print(f"Ошибка калибровки: {e}")
        return

    # Тестируем перемещение с новыми коэффициентами
    print("Тестовое перемещение с новыми коэффициентами.")
    mouse.move_direct(100, 100)

    # Плавное перемещение
    print("Начинается плавное перемещение курсора.")
    mouse.mouse_move(200, 200)

    # Закрываем соединение
    arduino.close()

if __name__ == "__main__":
    main()
