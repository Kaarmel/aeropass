"""Sprawdza, czy demo nie przedstawia danych scenariusza jako zgody na lot."""

from demo import START, alarm, mozna_latac


if __name__ == "__main__":
    a = alarm()
    p = mozna_latac(START)
    assert a["stan_cm"] > a["prog_alarmowy_cm"] and a["zweryfikowany"] is False
    assert p["przestrzen"] == "niezweryfikowana" and p["opad"] is None
    print("OK: scenariusz alarmu i pogody nie jest zgodą na lot")
