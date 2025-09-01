import random
from datetime import datetime

# ----------------------------------------------------------
# External helpers
# ----------------------------------------------------------

from faker import Faker
from faker.providers import DynamicProvider

fake = Faker()

# ----------------------------------------------------------
# monotonic counter
# ----------------------------------------------------------
global_counter = 0


def next_monotonic_uid():
    """Provides a global monotonic counter, normally used as
    unique-integer identifier
    """

    global global_counter
    global_counter += 1
    return global_counter


# ----------------------------------------------------------
# Fake year provider
# ----------------------------------------------------------

year_provider = DynamicProvider(
    provider_name="year",
    elements=list(range(2018, datetime.now().year + 1)),
)

fake.add_provider(year_provider)


def item_name(sep="-", lower=True):
    sentence = fake.sentence().split()
    random.shuffle(sentence)
    N = len(sentence)
    sentence = sep.join(sentence[-random.randint(1, N) :])
    if lower:
        sentence = sentence.lower()

    return sentence


fake.item_name = item_name
