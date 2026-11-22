"""Print reproducible trip subtotals for both adults, in KRW."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import json

p = json.loads((Path(__file__).resolve().parent / 'prices.json').read_text())
fx = Decimal(p['krw_per_jpy'])

def won(amount):
    return int(amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

shared = sum(p[key] for key in (
    'hotel_with_breakfast_jpy', 'club_rental_delivered_jpy', 'airport_taxi_return_jpy',
    'airport_booking_allowance_jpy', 'onsen_entry_party_jpy', 'onsen_train_return_party_jpy',
    'harbour_train_return_party_jpy'))

for rounds in (3, 2):
    local = shared + sum(p['green_fees_party_by_day_jpy'][:rounds]) + 2 * rounds * p['golf_taxi_per_leg_jpy']
    subtotal = Decimal(p['air_quote_krw']) + fx * local
    baggage = Decimal(p['example_checked_bag_out_krw']) + fx * p['example_checked_bag_return_jpy']
    for label, total in [('base', subtotal), ('25kg example', subtotal + baggage)]:
        print(f'{rounds * 18}H {label}: party {won(total):,} KRW, per person {won(total / p["party"]):,} KRW, remaining {won(p["budget_krw"] - total):,} KRW')

# Compare a supplier's three-round quote with package subtotals.
non_golf_54 = Decimal(p['air_quote_krw']) + fx * (shared + 6 * p['golf_taxi_per_leg_jpy'])
print(f'54H before green fees: {won(non_golf_54):,} KRW')
for cap in (2040000, 2100000, 2150000):
    print(f'At {cap:,} KRW: golf fees for both = {(Decimal(cap)-non_golf_54)/fx:.1f} JPY')

# Public package prices. Green fees, breakfast and shared transfers are included
# in these subtotals. Unpriced meals, golf bags and equipment are excluded.
budget = p["budget_krw"]
def package_subtotal(label, base_pp, transfer_pp=0, two_ball_pp=0, team_fee=0):
    total = p["party"] * (base_pp + transfer_pp + two_ball_pp) + team_fee
    print(f'{label}: party {total:,} KRW, per person {won(Decimal(total) / p["party"]):,} KRW, remaining {budget - total:,} KRW')
    return total

for unit, per_player, per_group in [("team", 0, 20_000), ("person", 20_000, 0)]:
    total = package_subtotal(f"Takamatsu 54H, fee per {unit}", 990_000,
                             two_ball_pp=3 * per_player, team_fee=3 * per_group)
    for club, final_rental in [("Gold", 2_750), ("Royal", 3_300)]:
        rental_yen = 2 * 2_200 + final_rental
        with_one_set = total + won(fx * rental_yen)
        print(f'  {club}: rental {rental_yen:,} JPY, party {with_one_set:,} KRW, remaining {budget - with_one_set:,} KRW')

package_subtotal("Prime Beppu 54H", 1_080_000, transfer_pp=60_000, two_ball_pp=3 * 20_000)
package_subtotal("Hana Beppu 54H, standard", 1_235_900, transfer_pp=60_000, two_ball_pp=3 * 40_000)
package_subtotal("Hana Beppu 54H, member", 1_205_900, transfer_pp=60_000, two_ball_pp=3 * 40_000)
package_subtotal("Smile Kagoshima 54H", 1_240_000, two_ball_pp=120_000)
package_subtotal("Hana Kagoshima 54H, standard", 1_325_900, transfer_pp=30_000, two_ball_pp=3 * 30_000)

kanmon_local_pp = won(fx * 8_000)
package_subtotal("Kanmon 54H, before equipment", 999_000 + kanmon_local_pp, two_ball_pp=50_000)
package_subtotal("Gran Cerezo Kagoshima 54H", 1_290_000, two_ball_pp=150_000)

# Three-night alternatives. Unknown fees and meals are outside these subtotals.
for yen_per_party in (8_000, 16_000):
    package_subtotal(f"Saga, transfer {yen_per_party:,} JPY for two, before Sunday fee",
                     1_040_000, two_ball_pp=2 * 20_000, team_fee=won(fx * yen_per_party))

package_subtotal("Yatsushiro, both bring clubs", 1_290_000)
package_subtotal("Yatsushiro, one set for three rounds", 1_290_000,
                 team_fee=won(fx * 3 * 4_400))
for fee_per_round in (10_000, 20_000):
    package_subtotal("Kumamoto city, land and displayed airfare", 830_000 + 335_341,
                     transfer_pp=60_000, two_ball_pp=3 * fee_per_round)
package_subtotal("Matsuyama, Dec 21, before two-player surcharge", 1_350_000)
package_subtotal("Matsuyama, Dec 20, before two-player surcharge", 1_500_000)
package_subtotal("Hana Fukuoka city", 1_726_900, transfer_pp=280_000, two_ball_pp=3 * 20_000)
package_subtotal("Hana Kumamoto station", 1_366_900, transfer_pp=340_000, two_ball_pp=3 * 22_000)

package_subtotal("Osaka Hinode, undated three-night starting price", 1_500_000)
package_subtotal("Kobe, 72H rather than 54H", 2_120_000)

# Matched Takamatsu routes (same golf dates, Gold on the last morning).
# All local prices below cover both travellers unless labelled per day.
takamatsu_golf = 2 * (9_680 + 10_010 + 7_350)
three_course_player = sum(p["three_course_gdo_jpy_per_player"].values())
three_course_party = p["party"] * three_course_player
print(f"GDO Royal/Sakaide/Gold 54H: {three_course_player:,} JPY per player, "
      f"{three_course_party:,} JPY per party, {takamatsu_golf - three_course_party:,} JPY lower golf fees")
takamatsu_rental_set = 2 * 2_200 + 2_750
taxi_one_way = [6_400, 6_800, 6_800, 6_800, 6_800, 8_500, 2_900]
taxi_distance_fare = sum(taxi_one_way)
for nights, flights, room, car in [(3, 773_600, 28_560, 28_710), (4, 838_800, 37_500, 37_125)]:
    routes = {"taxi": (taxi_distance_fare, taxi_distance_fare + 7 * 400)}
    for name, daily_cover in [("CDW", 1_430), ("CDW and NOC", 3_630)]:
        routes[name] = tuple(car + nights * daily_cover + fuel for fuel in (1_108, 1_375))
    base_with_own_clubs = [
        flights + won(fx * (room + takamatsu_golf + transport))
        for transport in routes["CDW and NOC"]
    ]
    for outbound_steps, return_steps in [(0, 0), (0, 1), (1, 1), (2, 2), (3, 3), (4, 4)]:
        bag_fee = 45_000 * outbound_steps + won(fx * 4_500 * return_steps)
        low, high = [amount + bag_fee for amount in base_with_own_clubs]
        print(f"Own clubs {nights}N, {30+5*outbound_steps}/{30+5*return_steps}kg: "
              f"party {low:,}–{high:,}, per person {won(Decimal(low)/2):,}–{won(Decimal(high)/2):,}, "
              f"remaining {budget-high:,}–{budget-low:,}, prepaid bags {bag_fee:,}")
    for name, transport in routes.items():
        for mobility in transport:
            yen = room + takamatsu_golf + takamatsu_rental_set + mobility
            total = flights + won(fx * yen)
            print(f"Takamatsu {nights}N {name}: party {total:,}, per person {won(Decimal(total) / 2):,}, remaining {budget - total:,}")
package_club = won(fx * takamatsu_rental_set)
for team in (60_000, 120_000):
    package_subtotal("Matched 3N package with Gold rental", 990_000, team_fee=team + package_club)
print(f"Second set, extra 5kg both ways: {45_000 + won(fx * 4_500):,} KRW")
print(f"Onsen and harbour, both: {won(fx * (2 * 700 + 4 * 410 + 4 * 230)):,} KRW")
