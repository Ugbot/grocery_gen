import json
import random
from pprint import pprint

from pydantic import BaseModel

from celebrationData import make_my_event_scores
from citydata import make_my_cities
from groceryLists import GroceryList
from product_values import calculate_day_score

import numpy as np
from noise import snoise2


def generate_simplex_noise(period, num_values, amplitude=1, seed=0, octaves=1, persistence=0.5):
    noise_values = np.zeros(num_values)
    frequency = 1 / period

    for i in range(num_values):
        noise_value = 0
        amplitude_i = amplitude

        for _ in range(octaves):
            noise_value += amplitude_i * snoise2(seed + i * frequency, seed)
            frequency *= 2
            amplitude_i *= persistence

        noise_values[i] = noise_value

    return noise_values


class Purchase(BaseModel):
    city: str
    day: int
    item: str
    price: float


def get_random_item_from_dict(my_dict):
    return random.choice(list(my_dict.items()))


def seeded_random(seed):
    random.seed(seed)
    while True:
        yield random.random()


random_gen = seeded_random(42)
period = 365
num_values = 365
amplitude = 1
seed = 42
octaves = 3
persistence = 0.5

simplex_noise_values = generate_simplex_noise(period, num_values, amplitude, seed, octaves, persistence)

my_cities = make_my_cities()

my_events = make_my_event_scores()

my_groceries = GroceryList()

purchases_per_day = 1000
newyear_purchases = 0
easter_purchases = 0
thanksgiving_purchases = 0
xmas_purchases = 0
hallween_purchases = 0

total_purchases = 0
for city in my_cities.values():
    for day in range(365):

        my_score = calculate_day_score(day, city, my_events)
        weighted_purchases = my_score.spend_weight * (simplex_noise_values[day] + 1) * purchases_per_day
        daily_purchases = []
        if my_score.valentines_weight > 0.3:
            print(f"Valentines day in {city.name} on day {day}")
            pass

        while weighted_purchases > 0:
            weighted_purchases -= 1
            purchase = Purchase(city="city", day=1, item="item", price=10)
            purchase.city = city.name
            purchase.day = day
            purchase.item, purchase.price = get_random_item_from_dict(my_groceries.general)

            daily_purchases.append(purchase.json())
            my_rand = random_gen.__next__()
            if random_gen.__next__() < my_score.xmas_weight:
                next_item, next_price = get_random_item_from_dict(my_groceries.xmas)
                xmas_purchase = Purchase(city = city.name, day = day, item = next_item, price = next_price)
                daily_purchases.append(xmas_purchase.json())
                weighted_purchases -= 1
                xmas_purchases += 1

            if random_gen.__next__() < my_score.thanksgiving_weight:
                next_item, next_price = get_random_item_from_dict(my_groceries.thanksgiving)
                thanksgiving_purchase = Purchase(city = city.name, day = day, item = next_item, price = next_price)
                daily_purchases.append(thanksgiving_purchase.json())
                weighted_purchases -= 1
                thanksgiving_purchases += 1

            if random_gen.__next__() < my_score.easter_weight:
                next_item, next_price = get_random_item_from_dict(my_groceries.easter)
                easter_purchase =Purchase(city = city.name, day = day, item = next_item, price = next_price)
                daily_purchases.append(easter_purchase.json())
                weighted_purchases -= 1
                easter_purchases += 1

            if my_score.valentines_weight > 0.3:
                print(f"Valentines day in {city.name} on day {day}")
                print(f"Valentines weight is {my_score.valentines_weight}, random is {random_gen.__next__()}"                )

            if random_gen.__next__() < my_score.valentines_weight:
                next_item, next_price = get_random_item_from_dict(my_groceries.valentines)
                valentines_purchase = Purchase(city = city.name, day = day, item = next_item, price = next_price)

                daily_purchases.append(valentines_purchase.json())
                weighted_purchases -= 1

            if random_gen.__next__() < my_score.new_year_weight:
                next_item, next_price = get_random_item_from_dict(my_groceries.new_year)
                new_year_purchase = Purchase(city = city.name, day = day, item = next_item, price = next_price)
                daily_purchases.append(new_year_purchase.json())
                weighted_purchases -= 1
                newyear_purchases += 1

        # print(daily_purchases)
        total_purchases += len(daily_purchases)
        json_purchases = json.dumps(daily_purchases)
        # pprint(json_purchases)

pprint(f"total purchases simulated is {total_purchases}, {newyear_purchases} new year, {easter_purchases} easter, {thanksgiving_purchases} thanksgiving, {xmas_purchases} xmas")