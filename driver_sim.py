import asyncio
import random
import names

import aiokafka
from aiokafka.helpers import create_ssl_context
from pydantic import BaseModel

context = create_ssl_context(
    cafile="demo_keys/ca.pem",
    certfile="demo_keys/service.cert",
    keyfile="demo_keys/service.key",
)

TOPIC_NAME = "raw-agent-data"

lat_max = 51.526475
lat_min = 51.511146
lon_max = -0.084629
lon_min = -0.135269

bounding_box1 = {"lat": 51.511146, "lon": -0.135269}
bounding_box2 = {"lat": 51.526475, "lon": -0.084629}


class Agent(BaseModel):
    agent_id: str
    free = bool
    lat = float
    lon = float
    capacity = int


num_of_agents = 250


def move_agent(agent: Agent) -> Agent:
    move_vector_lat = random.uniform(-0.0001, 0.0001)
    move_vector_lon = random.uniform(-0.0001, 0.0001)
    if bounding_box1["lat"] < agent.lat < bounding_box2["lat"]:
        if bounding_box1["lon"] < agent.lon < bounding_box2["lon"]:
            agent.lat += move_vector_lat
            agent.lon += move_vector_lon
    return agent


def make_agents(number_of_agents) -> list[Agent]:
    agents = []
    for i in range(number_of_agents):
        agent = Agent(agent_id=(names.get_first_name() + '_' + names.get_last_name()),
                      free=True, lat=(random.uniform(lat_max, lat_min)),
                      lon=(random.uniform(lon_max, lon_min)), capacity=random.randint(5, 10))
        agents.append(agent)
    return agents


def my_loop(my_producer):
    my_agents = make_agents(num_of_agents)

    for _ in range(10000):
        for agent in my_agents:
            agent = move_agent(agent)

        message = agent.json()
        my_producer.send(TOPIC_NAME, message.encode('utf-8'))
        asyncio.sleep(1)


async def main():
    global producer
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=f"streaming-econ-demo-devrel-ben.aivencloud.com:15545",
        security_protocol="SSL",
        ssl_context=context,
        # broker_credentials=context,
    )

    await producer.start()
    await my_loop(producer)
    await producer.stop()


asyncio.run(main())
