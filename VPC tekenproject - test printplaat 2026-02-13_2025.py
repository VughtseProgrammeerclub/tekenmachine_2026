from machine import Pin, PWM, I2C
import time
import framebuf

# ================= OLED SETUP =================
# SSD1306 via I2C0 op GP8 (SDA) en GP9 (SCL)
# Lage I2C-frequentie omdat jouw display anders timeout-fouten gaf.
ADDR = 0x3C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=20000)


# ===== AANGEPASTE SSD1306 DRIVER =====
# Dit is een "slow/robust" variant.
# Belangrijk: bevat retries bij I2C-communicatie om OSError(110) te voorkomen.
class SSD1306_I2C_Slow:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = self.height // 8

        # Framebuffer bevat volledige beeldinhoud in RAM
        self.buffer = bytearray(self.pages * self.width)
        self.fb = framebuf.FrameBuffer(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB
        )

        self.init_display()

    # Essentieel: herhaal I2C write bij tijdelijke fouten
    def _writeto_retry(self, data, tries=8, delay_ms=5):
        for _ in range(tries):
            try:
                self.i2c.writeto(self.addr, data)
                return
            except OSError:
                time.sleep_ms(delay_ms)
        self.i2c.writeto(self.addr, data)

    # Stuurt een commando (control byte 0x00)
    def cmd(self, c):
        self._writeto_retry(bytes([0x00, c]))
        time.sleep_ms(2)

    # SSD1306 initialisatie-sequentie
    # Dit zet resolutie, scanrichting, charge pump enz.
    def init_display(self):
        for c in (
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
            0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
            0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF
        ):
            self.cmd(c)
        self.fill(0)
        self.show()

    def fill(self, col):
        self.fb.fill(col)

    def text(self, s, x, y):
        self.fb.text(s, x, y)

    def pixel(self, x, y, col=1):
        self.fb.pixel(x, y, col)

    # Belangrijk:
    # Eerst kolom + pagina-adres instellen,
    # daarna framebuffer in kleine blokken versturen.
    def show(self):
        self.cmd(0x21); self.cmd(0); self.cmd(self.width - 1)
        self.cmd(0x22); self.cmd(0); self.cmd(self.pages - 1)

        CHUNK = 32  # kleine blokken om I2C stabiel te houden
        for i in range(0, len(self.buffer), CHUNK):
            self._writeto_retry(b"\x40" + self.buffer[i:i+CHUNK])
            time.sleep_ms(1)


oled = SSD1306_I2C_Slow(128, 64, i2c, addr=ADDR)


# ================= OLED HELPER =================
# dot_state wordt gebruikt voor het knipperpuntje rechtsboven
dot_state = False

def oled_message(line1="", line2="", line3=""):
    oled.fill(0)

    if line1: oled.text(line1, 0, 0)
    if line2: oled.text(line2, 0, 16)
    if line3: oled.text(line3, 0, 32)

    # Speciaal: knipperend statuspuntje rechtsboven
    x0, y0 = 124, 0
    col = 1 if dot_state else 0
    for dx in range(3):
        for dy in range(3):
            oled.pixel(x0 + dx, y0 + dy, col)

    oled.show()


# ================= SERVO SETUP =================
pairs = [
    (13, 18),
    (14, 19),
    (15, 20),
]

led_onboard = Pin(25, Pin.OUT)
led_ext = Pin(16, Pin.OUT)

# Belangrijk:
# 50 Hz is standaard voor analoge servo's.
SERVO_FREQ = 50

# Deze waarden bepalen het PWM bereik (0° en 180°)
# Afhankelijk van servo kunnen deze iets verschillen.
MIN_DUTY = 1638
MAX_DUTY = 8192

def angle_to_duty(angle):
    return int(MIN_DUTY + (angle / 180) * (MAX_DUTY - MIN_DUTY))

def set_servo_angle(pwm, angle):
    pwm.duty_u16(angle_to_duty(angle))


# Servo's en knoppen initialiseren
buttons = {}
servos = {}

for btn_gpio, srv_gpio in pairs:
    buttons[btn_gpio] = Pin(btn_gpio, Pin.IN, Pin.PULL_DOWN)

    pwm = PWM(Pin(srv_gpio))
    pwm.freq(SERVO_FREQ)
    servos[btn_gpio] = pwm

    # Startpositie = 0 graden
    set_servo_angle(pwm, 0)


# ================= SOEPELE SERVO-BEWEGING =================
# Deze functie is blokkerend.
# Tijdens uitvoeren wordt geen andere knop verwerkt.
STEP_DELAY = 0.02   # bepaalt snelheid
STEP_SIZE  = 2      # bepaalt vloeiendheid

def move_once_slow(pwm):

    # Vooruit
    for angle in range(0, 181, STEP_SIZE):
        set_servo_angle(pwm, angle)
        time.sleep(STEP_DELAY)

    # Terug
    for angle in range(180, -1, -STEP_SIZE):
        set_servo_angle(pwm, angle)
        time.sleep(STEP_DELAY)


# ================= KNIPPER-TIMING =================
# Wordt gebruikt voor:
# - LED's
# - OLED statuspuntje
last_toggle = time.ticks_ms()
LED_INTERVAL = 300


# ================= MAIN LOOP =================
oled_message("VPC Tekenrobot", "Gereed", "Druk knop")

while True:
    now = time.ticks_ms()

    # LED + OLED puntje laten knipperen
    if time.ticks_diff(now, last_toggle) > LED_INTERVAL:
        led_onboard.toggle()
        led_ext.toggle()

        dot_state = not dot_state
        last_toggle = now

        oled_message("VPC Tekenrobot", "Gereed", "Druk knop")

    # Knoppen controleren
    # Let op: blokkerend door move_once_slow()
    for btn_gpio in (13, 14, 15):
        if buttons[btn_gpio].value() == 1:

            oled_message("Servo actief", f"GPIO {btn_gpio}", "")

            move_once_slow(servos[btn_gpio])

            oled_message("VPC Tekenrobot", "Gereed", "")

            # wachten tot knop losgelaten is
            while buttons[btn_gpio].value() == 1:
                time.sleep(0.01)

    time.sleep(0.005)
