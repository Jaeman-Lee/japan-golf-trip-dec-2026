"""Print reproducible trip subtotals for both adults, in KRW."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import json

p = json.loads((Path(__file__).resolve().parent / 'prices.json').read_text())
fx = Decimal(p['krw_per_jpy'])

def won(amount):
    return int(amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

for rounds in (3, 2):
    shared = sum(p[key] for key in (
        'hotel_with_breakfast_jpy', 'club_rental_delivered_jpy', 'airport_taxi_return_jpy',
        'airport_booking_allowance_jpy', 'onsen_entry_party_jpy', 'onsen_train_return_party_jpy',
        'harbour_train_return_party_jpy'))
    local = shared + sum(p['green_fees_party_by_day_jpy'][:rounds]) + 2 * rounds * p['golf_taxi_per_leg_jpy']
    subtotal = Decimal(p['air_quote_krw']) + fx * local
    baggage = Decimal(p['example_checked_bag_out_krw']) + fx * p['example_checked_bag_return_jpy']
    for label, total in [('base', subtotal), ('25kg example', subtotal + baggage)]:
        print(f'{rounds * 18}H {label}: party {won(total):,} KRW, per person {won(total / p["party"]):,} KRW, remaining {won(p["budget_krw"] - total):,} KRW')
