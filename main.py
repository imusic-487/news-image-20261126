#!/usr/bin/env python3
"""Sum up Thursday 26 November 2026 world news in one 1024x1024 image.

Pure Python 3.13 standard library only (struct, zlib, os). No network,
no randomness, no timestamps: two runs write byte-identical files.
Draws a dense broadsheet: masthead, UTC timeline, schematic world map
with numbered locations, four information graphics, 16 lead stories and
a 34-item compact list (50 stories total), plus a DATE CHECK box that
separates genuine 26 Nov events from 25 Nov events reported on 26 Nov
and from earlier-date traps. Grades: CONFIRMED (2+ sources or official)
vs CLAIM (single source or announcement); "*" marks a 25 Nov event.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette (warm newsprint) ----
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (179, 38, 30)
BLUE = (31, 78, 121)
OCEAN = (198, 222, 235)
LAND = (232, 222, 188)
LAND_LINE = (160, 148, 110)
GREEN = (30, 122, 52)
AMBER = (154, 106, 0)
GREY = (110, 105, 92)
LIGHT = (255, 255, 255)
PANEL = (255, 255, 255)
BAR = (31, 78, 121)
BAR2 = (179, 38, 30)

# ---- 5x7 bitmap font ("#" = on). All text is upper-case on purpose. ----
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


def text_w(s, scale):
    return len(s) * 6 * scale


class Img:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def hline(self, x0, x1, y, c):
        if x0 > x1:
            x0, x1 = x1, x0
        self.fill_rect(x0, y, x1 - x0 + 1, 1, c)

    def vline(self, x, y0, y1, c):
        if y0 > y1:
            y0, y1 = y1, y0
        self.fill_rect(x, y0, 1, y1 - y0 + 1, c)

    def rect(self, x, y, w, h, c):
        self.hline(x, x + w - 1, y, c)
        self.hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c)
        self.vline(x + w - 1, y, y + h - 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set_px(xx, yy, c)

    def fill_poly(self, pts, c):
        if len(pts) < 3:
            return
        ymin = min(p[1] for p in pts)
        ymax = max(p[1] for p in pts)
        n = len(pts)
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "1":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centred(self, cx, y, s, scale, c):
        return self.text(cx - text_w(s, scale) // 2, y, s, scale, c)


def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def save_png(path, img):
    raw = bytearray()
    for y in range(img.h):
        raw.append(0)
        raw += img.buf[y * img.w * 3:(y + 1) * img.w * 3]
    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- content: 50 stories of 26 November 2026 ----
# grade: "C" = CONFIRMED (2+ sources or official), "L" = CLAIM (single
# source or announcement). star=True means reported 26 Nov, happened 25 Nov.
LEAD = [
    ("C", False, "THANKSGIVING STORM PEAKS: RAIN, 50-60MPH GUSTS, FLOODS - REUTERS"),
    ("C", False, "MACY'S 100TH PARADE: DRY 8:30AM START, RAIN LATER - REUTERS"),
    ("C", False, "RECORD TRAVEL: 417,000+ FLIGHTS, 81.5M TRIPS - FAA, AAA"),
    ("C", False, "INDIA CONSTITUTION DAY: IITS ADD 6,000 TECH SEATS - GOVT"),
    ("C", False, "CHESS GAME 3 TODAY: SINDAROV-GUKESH, LEVEL 1-1 - FIDE"),
    ("C", False, "HONG KONG: 1 YEAR SINCE WANG FUK COURT FIRE, 168 DEAD - HK"),
    ("L", False, "CANADA: CARNEY TO ANNOUNCE STEEL, LUMBER AID - CBC"),
    ("C", True, "US TARIFFS (25 NOV): +20% CHINA, 15% CAP ALLIES - AP"),
    ("C", True, "SHENZHOU-24 DOCKS; FIRST PAKISTANI IN ORBIT - REUTERS"),
    ("C", True, "BANGLADESH GARMENT WAGE +36% TO 17,000 TAKA - REUTERS"),
    ("C", True, "CARTAGENA SIEGE ENDS: 20 HOSTAGES FREED - REUTERS"),
    ("C", True, "N KOREA ORDERS SWISS OFFICE SHUT IN 48H - KCNA"),
    ("L", False, "INDIA-NEPAL RS 15,000-CR PACKAGE AFTER MODI TALKS - MEDIA"),
    ("L", False, "HASINA ASKS TO RETURN TO BANGLADESH DEC 16 - REPORTS"),
    ("C", True, "SOORYAVANSHI, 17, HITS 204 OFF 53 BALLS VS UAE - MEDIA"),
    ("C", True, "CHAMPIONS LEAGUE: REAL BEAT PSV; ARSENAL HELD - UEFA"),
]

COMPACT = [
    ("L", False, "XI GRAFT PROBE OF SHANGHAI RISING STAR SHAKES CHINA - BBC"),
    ("L", False, "RUSSIA'S OWN FIGURES: NEARLY 500,000 WAR DEAD IN UKRAINE - DATA"),
    ("L", False, "US ATTORNEY GENERAL DODGES NVIDIA PROBE QUESTIONS - REPORTS"),
    ("L", False, "ASTEROID CLOSE-UPS TO BE REVEALED AFTER DART, HERA - ESA/NASA"),
    ("L", False, "MELANIA TRUMP REUNITES 7TH GROUP OF CHILDREN - US MEDIA"),
    ("L", False, "KILMAR ABREGO GARCIA LEAVING US FOR SPAIN - REPORTS"),
    ("C", False, "BRAZIL WOLBACHIA TRIAL CUTS VIRAL INFECTIONS 68% - STUDY"),
    ("C", False, "IPL 2027 AUCTION DRAWS 1,220 PLAYER REGISTRATIONS - IPL"),
    ("L", False, "FLIPKART CEO KALYAN KRISHNAMURTHY TO STEP DOWN IN DEC - REPORTS"),
    ("C", False, "SENSEX DROPS 1,484 PTS; NIFTY BELOW 25,400 - BSE"),
    ("C", True, "NZ HOLD INDIA TO DRAW IN FIRST TEST - REPORTS"),
    ("C", False, "MODI, GERMAN CHANCELLOR MERZ HOLD STRATEGIC TALKS - PMO"),
    ("C", False, "INDIA SPACE ECONOMY TO HIT $40-45BN IN A DECADE - MINISTER"),
    ("L", False, "HOUTHIS REPORT DEATHS AFTER SAUDI STRIKES IN YEMEN - MEDIA"),
    ("C", False, "ROAD CRASH IN UAE'S RAS AL KHAIMAH KILLS 11 - UAE MEDIA"),
    ("C", False, "5.6-MAGNITUDE QUAKE HITS NEPAL'S KOSHI PROVINCE - REPORTS"),
    ("C", False, "COLOMBIA MARKS 10 YEARS SINCE HISTORIC PEACE DEAL - UN"),
    ("C", False, "US CONSUMER CONFIDENCE NEAR TWO-YEAR HIGH - SURVEY"),
    ("C", False, "CANADA REAFFIRMS INFLATION STRATEGY - BANK OF CANADA"),
    ("C", False, "EL SALVADOR ALLOCATES $860M DEBT FINANCING - GOVT"),
    ("C", False, "BARBADOS SETS FEB DEADLINE FOR CARIBBEAN AI RULES - GOVT"),
    ("C", False, "PETROBRAS UNVEILS $122BN INVESTMENT STRATEGY - PETROBRAS"),
    ("C", False, "VENEZUELA REVEALS $237.5BN PUBLIC DEBT - GOVT"),
    ("C", False, "AUSTRALIA, SOLOMON ISLANDS SIGN SECURITY PACT - GOVTS"),
    ("C", False, "EGYPT: SUEZ CANAL REVENUES GRADUALLY RECOVERING - SCA"),
    ("C", False, "FRANCE SEEKS INDEPENDENCE IN CRITICAL MINERALS - GOVT"),
    ("L", False, "BRITAIN PROBES LEGACY OF NUCLEAR WEAPONS TESTS - REPORTS"),
    ("L", False, "POLAND FLAGS SECURITY AFTER AIRSPACE VIOLATIONS - GOVT"),
    ("L", False, "RUSSIA RAISES DEFENCE ALLOCATIONS - BUDGET"),
    ("C", False, "UKRAINE, HUNGARY PURSUE RENEWED ECONOMIC TIES - GOVTS"),
    ("L", False, "JAPAN-EUROPE MISSION REACHES MERCURY AFTER 8 YEARS - JAXA/ESA"),
    ("C", False, "INDIA: HUMAN CONTROL MUST STAY OVER AI IN WAR - MEA"),
    ("L", False, "ISRAELI MINISTER: IRAN DEVELOPING CHEMICAL WEAPONS - ISRAEL DM"),
    ("L", False, "US SHELVES PLAN TO USE RUSSIA BUSINESS DEALS FOR PEACE - FT"),
]

# UTC timeline of 26 Nov 2026: (hour, label, above_bar)
TIMELINE = [
    (2.0, "HK ANNIV.", True),
    (4.5, "DELHI", False),
    (6.0, "NEPAL", True),
    (13.5, "PARADE", False),
    (14.0, "CHESS G3", True),
    (15.0, "CANADA AID", False),
    (18.0, "STORM PEAK", True),
]

# schematic world map: rough continent outlines in (lon, lat)
NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                 (-85, 73), (-75, 72), (-65, 60), (-55, 52), (-60, 46),
                 (-70, 42), (-75, 35), (-80, 32), (-85, 30), (-90, 21),
                 (-95, 18), (-100, 16), (-105, 20), (-110, 23), (-115, 28),
                 (-120, 34), (-125, 40), (-125, 48), (-135, 58), (-150, 60),
                 (-165, 60)]
SOUTH_AMERICA = [(-80, 10), (-75, 7), (-70, 12), (-60, 8), (-52, 5),
                 (-50, 0), (-40, -5), (-35, -8), (-40, -20), (-48, -28),
                 (-55, -35), (-65, -40), (-70, -52), (-73, -40), (-72, -20),
                 (-80, -5), (-81, 0)]
AFRICA = [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
          (51, 11), (48, 0), (40, -10), (35, -20), (32, -28), (20, -35),
          (12, -18), (9, -1), (9, 4), (-8, 5), (-15, 12), (-17, 20),
          (-16, 28)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
          (10, 59), (18, 56), (21, 55), (28, 59), (30, 60), (25, 65),
          (20, 70), (30, 70), (40, 68), (45, 60), (40, 55), (35, 50),
          (30, 46), (28, 41), (23, 40), (20, 38), (15, 38), (12, 44),
          (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36)]
ASIA = [(40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75),
        (100, 77), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
        (160, 66), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
        (150, 59), (142, 55), (140, 45), (135, 43), (130, 42), (127, 40),
        (122, 38), (120, 35), (118, 30), (112, 22), (108, 18), (105, 10),
        (103, 2), (100, 6), (98, 10), (95, 15), (92, 21), (89, 22),
        (86, 20), (80, 15), (77, 8), (75, 12), (72, 20), (68, 23),
        (62, 25), (58, 26), (55, 26), (52, 28), (50, 30), (48, 30),
        (45, 32), (42, 35), (40, 38), (38, 42), (35, 45), (30, 46)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
             (132, -32), (135, -35), (138, -35), (140, -38), (145, -38),
             (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
             (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
             (130, -13), (126, -14), (122, -17), (118, -20)]

# numbered map locations: (number, lon, lat, label dx, label dy)
MAP_POINTS = [(1, -74, 41, -14, -10), (2, 6, 46, -4, 10),
              (3, 77, 29, 8, -12), (4, 90, 24, 8, 12),
              (5, 116, 40, 8, -12), (6, 114, 22, 8, 10),
              (7, -75, 10, -4, 10), (8, 126, 39, 8, -6),
              (9, 85, 28, -18, 2), (10, -48, -16, 8, -4),
              (11, 0, 51, -14, -10), (12, 37, 56, 8, -10)]

DATE_CHECK = [
    "26 NOV (TODAY): THANKSGIVING + STORM, MACY'S 100TH PARADE, CHESS GAME 3, INDIA CONSTITUTION DAY,",
    "HONG KONG FIRE 1-YEAR ANNIVERSARY, CANADA AID PLAN, NEPAL PACKAGE, HASINA REQUEST.",
    "* = REPORTED 26 NOV BUT HAPPENED 25 NOV: US TARIFFS, SHENZHOU-24, BANGLADESH WAGE,",
    "CARTAGENA RESCUE, N KOREA-SWISS ROW, SOORYAVANSHI 204, CHAMPIONS LEAGUE RESULTS.",
    "NOT TODAY - DO NOT COUNT: ICJ MYANMAR RULING 19 NOV; COP31 COLLAPSE 22 NOV; EU SANCTIONS 23 NOV;",
    "SHENZHEN SUMMIT 19 NOV; UKRAINE WARSHIP CLAIM 23 NOV.",
    "GRADES: CONFIRMED = 2+ SOURCES OR OFFICIAL. CLAIM = ONE SOURCE OR ANNOUNCEMENT ONLY.",
]


# ---- layout ----
MX = 16                      # left margin
RX = W - MX                  # right edge (1008)
MAP = (MX, 118, 600, 232)    # map box x0,y0,x1,y1
GFX = (612, 118, RX, 260)    # graphics area x0,y0,x1,y1


def grade_color(grade):
    return GREEN if grade == "C" else AMBER


def grade_word(grade):
    return "CONFIRMED" if grade == "C" else "CLAIM"


def section_head(img, y, title, note=""):
    img.fill_rect(MX, y, RX - MX, 2, RED)
    img.text(MX, y + 5, title, 2, RED)
    if note:
        img.text(RX - text_w(note, 1), y + 8, note, 1, GREY)
    return y + 22


def draw_masthead(img):
    img.text_centred(W // 2, 6, "THE WORLD IN ONE DAY", 4, INK)
    img.text_centred(W // 2, 40, "THURSDAY 26 NOVEMBER 2026  -  50 STORIES FROM EVERY CONTINENT", 2, RED)
    img.fill_rect(MX, 62, RX - MX, 3, INK)


def draw_timeline(img):
    y0, y1 = 68, 106
    bx0, bx1, by = MX, RX, 88
    img.fill_rect(bx0, by, bx1 - bx0, 3, INK)
    for h in range(0, 25, 2):
        x = bx0 + int(h / 24 * (bx1 - bx0))
        img.vline(x, by - 3, by + 6, INK)
    img.text(bx0 - 2, by + 9, "00", 1, GREY)
    img.text(bx1 - 12, by + 9, "24", 1, GREY)
    img.text(RX - text_w("26 NOV IN UTC", 1), by - 13, "26 NOV IN UTC", 1, GREY)
    for hour, label, above in TIMELINE:
        x = bx0 + int(hour / 24 * (bx1 - bx0))
        img.circle(x, by + 1, 4, RED)
        img.circle(x, by + 1, 2, LIGHT)
        lx = min(max(x - text_w(label, 1) // 2, MX), RX - text_w(label, 1))
        if above:
            img.text(lx, by - 13, label, 1, RED)
        else:
            img.text(lx, by + 9, label, 1, INK)
    img.hline(MX, RX, y1 + 2, INK)


def proj(lon, lat):
    x0, y0, x1, y1 = MAP
    x = x0 + (lon + 170) / 360.0 * (x1 - x0)
    y = y0 + (72 - lat) / 117.0 * (y1 - y0)
    return int(x), int(y)


def draw_map(img):
    x0, y0, x1, y1 = MAP
    img.fill_rect(x0, y0, x1 - x0, y1 - y0, OCEAN)
    img.rect(x0, y0, x1 - x0, y1 - y0, INK)
    for lat in (60, 30, 0, -30):
        _, yy = proj(0, lat)
        for xx in range(x0, x1, 4):
            img.set_px(xx, yy, (255, 255, 255))
    for cont in (NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EUROPE, ASIA, AUSTRALIA):
        pts = [proj(lon, lat) for lon, lat in cont]
        img.fill_poly(pts, LAND)
        for i in range(len(pts)):
            img.line(pts[i][0], pts[i][1], pts[(i + 1) % len(pts)][0],
                     pts[(i + 1) % len(pts)][1], LAND_LINE)
    img.text(x0 + 4, y0 + 3, "WHERE IT HAPPENED", 1, BLUE)
    for num, lon, lat, dx, dy in MAP_POINTS:
        px, py = proj(lon, lat)
        img.circle(px, py, 4, LIGHT)
        img.circle(px, py, 3, RED)
        lx, ly = px + dx, py + dy
        img.line(px, py, lx + 3, ly + 3, RED)
        lab = str(num)
        img.fill_rect(lx - 1, ly - 1, text_w(lab, 1) + 2, 9, LIGHT)
        img.text(lx, ly, lab, 1, RED)
    img.text(x0, y1 + 4, "MAP: 1 NYC  2 GENEVA  3 DELHI  4 DHAKA  5 BEIJING  6 HONG KONG", 1, INK)
    img.text(x0, y1 + 14, "7 CARTAGENA  8 PYONGYANG  9 KATHMANDU  10 BRASILIA  11 LONDON  12 MOSCOW", 1, INK)


def draw_panel(img, x, y, w, h, title):
    img.fill_rect(x, y, w, h, PANEL)
    img.rect(x, y, w, h, INK)
    img.fill_rect(x, y, w, 13, BLUE)
    img.text(x + 4, y + 3, title, 1, LIGHT)
    return y + 16


def draw_graphics(img):
    gx0, gy0, gx1, gy1 = GFX
    pw = (gx1 - gx0 - 8) // 2
    ph = (gy1 - gy0 - 8) // 2
    # G1: tariffs bar chart (top-left)
    y = draw_panel(img, gx0, gy0, pw, ph, "US TARIFFS - 25 NOV")
    bars = [("CHINA +20%", 45, BAR2), ("ALLIES 15% CAP", 15, BAR),
            ("BRAZIL 10%", 10, BAR)]
    bx = gx0 + 4
    for label, val, col in bars:
        img.text(bx, y + 1, label, 1, INK)
        bw = int(val / 50.0 * (pw - 8))
        img.fill_rect(bx, y + 10, bw, 7, col)
        img.text(bx + bw + 3, y + 10, str(val) + "%", 1, col)
        y += 19
    # G2: chess scoreboard (top-right)
    x2 = gx0 + pw + 8
    y = draw_panel(img, x2, gy0, pw, ph, "CHESS - WORLD TITLE")
    img.text(x2 + 4, y + 1, "GUKESH 1 - 1", 2, INK)
    img.text(x2 + 4, y + 17, "SINDAROV", 2, INK)
    img.text(x2 + 4, y + 33, "GAME 3 TODAY - GENEVA", 1, INK)
    img.text(x2 + 4, y + 43, "15:00 CET - $2.5M FUND", 1, GREY)
    # G3: Thanksgiving travel (bottom-left)
    y = draw_panel(img, gx0, gy0 + ph + 8, pw, ph, "THANKSGIVING TRAVEL")
    img.text(gx0 + 4, y + 1, "81.5M", 2, RED)
    img.text(gx0 + 4, y + 17, "TRAVELLERS (AAA)", 1, INK)
    img.text(gx0 + 4, y + 27, "417,000+ FLIGHTS IN 9 DAYS", 1, INK)
    img.text(gx0 + 4, y + 37, "FAA: BUSIEST IN 16 YEARS", 1, GREY)
    # G4: garment wage (bottom-right)
    y = draw_panel(img, x2, gy0 + ph + 8, pw, ph, "GARMENT WAGE - BANGLADESH")
    img.text(x2 + 4, y + 1, "17,000 TAKA", 2, RED)
    img.text(x2 + 4, y + 17, "UP FROM 12,500  +36%", 1, INK)
    img.text(x2 + 4, y + 27, "FROM DEC 1 - WORKERS", 1, INK)
    img.text(x2 + 4, y + 37, "WANTED 30,000 TAKA", 1, GREY)


def draw_lead(img, y):
    y = section_head(img, y, "THE DAY'S TOP STORIES",
                     "GREEN = CONFIRMED   AMBER = CLAIM   * = 25 NOV EVENT")
    for i, (grade, star, text) in enumerate(LEAD, 1):
        col = grade_color(grade)
        num = "%02d" % i
        img.text(MX, y, num, 2, col)
        x = MX + text_w(num + " ", 2)
        if star:
            x = img.text(x, y, "*", 2, RED)
            x += 6
        x = img.text(x, y, text, 2, INK)
        tag = grade_word(grade)
        img.text(RX - text_w(tag, 1), y + 3, tag, 1, col)
        y += 21
    return y


def draw_compact(img, y):
    y = section_head(img, y, "MORE FROM 26 NOVEMBER - STORIES 17 TO 50",
                     "NUMBER COLOUR = GRADE (SEE ABOVE)")
    col_w = (RX - MX - 16) // 2
    for k, (grade, star, text) in enumerate(COMPACT, 17):
        col_i = 0 if k - 17 < 17 else 1
        row = (k - 17) % 17
        x = MX + col_i * (col_w + 16)
        yy = y + row * 12
        num = "%d " % k
        xx = img.text(x, yy, num, 1, grade_color(grade))
        if star:
            xx = img.text(xx, yy, "* ", 1, RED)
        img.text(xx, yy, text, 1, INK)
    return y + 17 * 12 + 4


def draw_date_check(img, y):
    img.fill_rect(MX, y, RX - MX, 2, RED)
    img.text(MX, y + 5, "DATE CHECK - WHAT COUNTS AS 26 NOVEMBER 2026", 2, RED)
    yy = y + 26
    for line in DATE_CHECK:
        img.text(MX, yy, line, 1, INK)
        yy += 11
    return yy + 4


def draw_footer(img):
    img.fill_rect(MX, 1000, RX - MX, 2, INK)
    img.text(MX, 1006, "SOURCES: REUTERS AP CNN BBC FT FIDE CBC KCNA UEFA IPL BSE - FULL LIST IN REPO README", 1, GREY)
    img.text(MX, 1016, "DRAWN FROM REPORTS OF 26 NOV 2026 - ALL TIMES UTC UNLESS NOTED - 50 STORIES", 1, GREY)


def build():
    img = Img(W, H, PAPER)
    draw_masthead(img)
    draw_timeline(img)
    draw_map(img)
    draw_graphics(img)
    y = draw_lead(img, 266)
    y = draw_compact(img, y + 2)
    y = draw_date_check(img, y + 2)
    draw_footer(img)
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    img = build()
    size = save_png(path, img)
    print("wrote %s %dx%d %d bytes" % (path, W, H, size))
    # overflow self-check: every lead line must fit the page width
    for i, (grade, star, text) in enumerate(LEAD, 1):
        w = text_w("%02d " % i, 2) + (18 if star else 0) + text_w(text, 2)
        w += text_w(grade_word(grade), 1) + 12
        if w > RX - MX:
            print("WARN lead %d too wide: %d px" % (i, w))
    for k, (grade, star, text) in enumerate(COMPACT, 17):
        w = text_w("%d " % k, 1) + (12 if star else 0) + text_w(text, 1)
        if w > (RX - MX - 16) // 2:
            print("WARN compact %d too wide: %d px" % (k, w))
    print("stories: %d lead + %d compact = %d"
          % (len(LEAD), len(COMPACT), len(LEAD) + len(COMPACT)))


if __name__ == "__main__":
    main()
