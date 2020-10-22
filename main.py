from Soil import Soil
from Time import ArtificialTime
import ElementaryRLAgent
import numpy
import copy


def interaction():
    t = ArtificialTime()
    soil = Soil(t)
    policy = ElementaryRLAgent.Policy(0.1, 0.05, [0, 20])
    agent = ElementaryRLAgent.Agent(soil, t, policy, 0.1, 0.2, [0, 1, 2])
    last_raw_command = ""
    while t.month < 2:
        raw_command = input()
        if raw_command == "*":
            raw_command = last_raw_command
        command = raw_command.split()
        if command[0] == "state":
            m = float(command[1])
            for s in policy.state_action_values.keys():
                if s.moisture == m:
                    print(str(s)+" :")
                    for action, value in policy.state_action_values[s].items():
                        print("\tintensity " + str(action) + " :" + str(value))
        elif command[0] == "proceed":
            counter = 0
            if len(command) == 3:
                while counter < int(command[2]):
                    if command[1] == "verbose":
                        print("state: "+str(agent.state))
                    agent.Q_learning_iteration()
                    if command[1] == "verbose":
                        print("action: "+str(agent.action_to_take)+" , reward: "+str(agent.reward))
                        print()
                    t.increase_time()
                    counter += 1
                    if t.month >= 2:
                        break
            else:
                print("Invalid command!")
        elif command[0] == "soil":
            print(soil)
        elif command[0] == "epsilon":
            print(policy.epsilon)
        elif command[0] == "iteration":
            if command[1] == "explore":
                print(policy.exploration_iteration)
            if command[1] == "learn":
                print(agent.learning_iteration)
        elif command[0] == "history":
            if command[1] == "explore":
                print(policy.explore_delta_reward_EMA)
            elif command[1] == "exploit":
                print(policy.exploit_delta_reward_EMA)
            elif command[1] == "reward":
                print(policy.reward_EMA)
            else:
                print("Invalid command!")
        elif command[0] == "visualize":
            if len(command) > 1:
                soil.visualizer(command[1])
            else:
                print("Invalid command!")
        elif command[0] == "loss":
            print(soil.LAYERS_WATER_LOSS)
        elif command[0] == "input":
            print(soil.input_water)
        else:
            print("Invalid Command!")
        last_raw_command = raw_command
    soil.visualizer('day')


def with_agent():
    t = ArtificialTime()
    soil = Soil(t)
    policy = ElementaryRLAgent.Policy(0.1, 0.01, [0, 10, 20])
    agent = ElementaryRLAgent.Agent(soil, t, policy, 0.7, 0.8, [0, 1, 2])
    while t.month < 2:
        agent.Q_learning_iteration()
        '''
        if agent.learning_iteration % 100 == 0:
            print(soil)
            print(policy)
            print(policy.epsilon)
            input()
        '''
        t.increase_time()
    soil.visualizer('day')


with_agent()
