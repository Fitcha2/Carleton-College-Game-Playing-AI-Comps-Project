from simulation import *
from test_set_up import *
import random
import copy
from shutil import copyfile
from os import remove


class Trainer:


    def __init__(self, bot_count, bot_prefix='bot'):
        """
        Initializes all bot files

        bot_count: The number of robots to create (population size). MUST BE EVEN NUMBER
        mutation_percent: percentage as a number out of 100 of new bots generated via mutation (the rest are generated via crossover)
        bot_prefix: name to use to start the bot files
        """
        self.bot_prefix = bot_prefix
        self.bot_count = bot_count
        self.results = {}
        self.gen_count = 0
        self.bot_names = [self.bot_prefix + str(i) for i in range(1, self.bot_count + 1)]

        for bot in self.bot_names:
            initialize_new_bot(bot)

    def old_train(self, mutation_percent, generations, games_per_bot, fast_count, bots_per_sim=0, delete_files=True,
              operator_probability='50', carryover_portion=0.5):
        """
        Trains the bots for a set number of generations. Each generation half the bots are selected to move on to the next generation
        and the other half are thrown out. The thrown out bots are replaced by a combination of cross over and mutation on the selected
        bots dictated by the mutation percent parameter.
        mutation_percent: percentage of new bots generated via mutation (the rest are generated via crossover)
        generations: number of generations to train for
        games_per_bot: number of games each bot plays each generation
        fast_count: number of fast bots in each simulation (smart bots will be 3 - fast bots)
        bots_per_sim: Number of bots to include in each simulation, default is all bots in one simulation
        operator_probability = probability of making an operator on a mutation (string number from 0 - 100)
        carryover_portion: portion of bots to carry over (float from 0 to 1) TODO: make this actually work if it's not set to 0.5
        """

        for gen in range(generations):
            self.gen_count += 1

            # check to see if we are doing default number of games per simulation
            if bots_per_sim == 0:
                bots_per_sim = self.bot_count

            # set up list of simulations
            simulations = []
            simulation_count = self.bot_count // bots_per_sim
            for i in range(simulation_count):
                sim_name = self.bot_prefix + "_generation_" + str(self.gen_count) + '_' + str(i + 1)
                simulations.append(
                    Simulation(sim_name, self.bot_names[i * bots_per_sim: i * bots_per_sim + bots_per_sim],
                               games_per_bot, fast_count, delete_files))

            if self.bot_count % bots_per_sim != 0:
                bots_left_over = self.bot_count - (simulation_count * bots_per_sim)
                final_sim_name = self.bot_prefix + "_generation_" + str(self.gen_count) + '_' + str(
                    simulation_count + 1)
                simulations.append(
                    Simulation(final_sim_name, self.bot_names[-bots_left_over:], games_per_bot, fast_count,
                               delete_files))

            # run simulations, update results
            self.results[self.gen_count] = {}
            for simulation in simulations:
                simulation.simulate()
                res = simulation.get_evo_results()

                for key in res:
                    self.results[self.gen_count][key] = res[key]

            # Selects bots to move on and bots to be overwritten
            gen_results = [(k, self.results[self.gen_count][k]) for k in self.results[self.gen_count]]
            gen_results.sort(key=lambda x: x[1], reverse=True)
            selected_bots = gen_results[:(len(gen_results)*carryover_portion)]
            bad_bots = gen_results[(len(gen_results)*carryover_portion):]
            random.shuffle(selected_bots)
            random.shuffle(bad_bots)

            # calculate number of bots to mutate/cross over. cross over count must be even
            mutate_count = round(mutation_percent * len(selected_bots))
            cross_over_count = len(selected_bots) - mutate_count
            if cross_over_count % 2 != 0:
                if mutate_count == 0:
                    cross_over_count -= 1
                    mutate_count += 1
                else:
                    cross_over_count += 1
                    mutate_count -= 1

            # mutate bots
            for i in range(mutate_count):
                #if len(selected_bots) == 0:
                    #selected_bots = gen_results[:(len(gen_results)*carryover_portion)]
                    #random.shuffle(selected_bots)
                bot_to_mutate = selected_bots.pop()[0]
                bot_to_replace = bad_bots.pop()[0]
                mutate_bot(bot_to_mutate, bot_to_replace, operator_probability)

            # Cross over bots
            for i in range(cross_over_count // 2):
                #if len(selected_bots) == 0:
                    #selected_bots = gen_results[:(len(gen_results)*carryover_portion)]
                    #random.shuffle(selected_bots)
                bot1_to_cross_over = selected_bots.pop()[0]
                bot2_to_cross_over = selected_bots.pop()[0]
                bot1_to_replace = bad_bots.pop()[0]
                bot2_to_replace = bad_bots.pop()[0]
                cross_over(bot1_to_cross_over, bot2_to_cross_over, bot1_to_replace, bot2_to_replace)
                
                
                
    def train(self, mutation_percent, generations, games_per_bot, fast_count, bots_per_sim=0, delete_files=True, operator_probability='50'):
        """
        Trains the bots for a set number of generations. Each generation, the highest-performing bots are used to create the majority of the
        next generation, while the majority of the bots contribute only slightly. The new bots are generated by a combination of cross over
        and mutation, mainly on the selected bots, dictated by the mutation percent parameter.

        mutation_percent: percentage of new bots generated via mutation (the rest are generated via crossover)
        generations: number of generations to train for
        games_per_bot: number of games each bot plays each generation
        fast_count: number of fast bots in each simulation (smart bots will be 3 - fast bots)
        bots_per_sim: Number of bots to include in each simulation, default is all bots in one simulation
        operator_probability = probability of making an operator on a mutation (string number from 0 - 100)
        """

        for gen in range(generations):
            self.gen_count += 1

            # check to see if we are doing default number of games per simulation
            if bots_per_sim == 0:
                bots_per_sim = self.bot_count


            # set up list of simulations
            simulations = []
            simulation_count = self.bot_count // bots_per_sim
            for i in range(simulation_count):
                sim_name = self.bot_prefix + "_generation_" + str(self.gen_count) + '_' + str(i + 1)
                simulations.append(Simulation(sim_name, self.bot_names[i * bots_per_sim: i * bots_per_sim + bots_per_sim], games_per_bot, fast_count, delete_files))

            if self.bot_count % bots_per_sim != 0:
                bots_left_over = self.bot_count - (simulation_count * bots_per_sim)
                final_sim_name = self.bot_prefix + "_generation_" + str(self.gen_count) + '_' + str(simulation_count + 1)
                simulations.append(Simulation(final_sim_name, self.bot_names[-bots_left_over:], games_per_bot, fast_count, delete_files))


            # run simulations, update results
            self.results[self.gen_count] = {}
            for simulation in simulations:
                simulation.simulate()
                res = simulation.get_evo_results()

                for key in res:
                    self.results[self.gen_count][key] = res[key]


            # Splits bots into high performers and low performers
            gen_results = [(k, self.results[self.gen_count][k]) for k in self.results[self.gen_count]]
            total_fitness = sum(x[1] for x in gen_results)
            proportion_cutoff = 0.1
            fitness_cutoff = performance_cutoff * total_fitness
            gen_results.sort(key=lambda x: x[1], reverse=True) #sorting high to low
            fitness_accumulator = 0
            current_tree = 0
            while (fitness_accumulator <= fitness_cutoff)
                fitness_accumulator += gen_results[current_tree][1]
                current_tree+=1
            high_performers = gen_results[:current_tree]
            low_performers = gen_results[current_tree:]
            #selected_bots = gen_results[:len(gen_results) // 2]
            #bad_bots = gen_results[len(gen_results) // 2:]
            #random.shuffle(selected_bots)
            #random.shuffle(bad_bots)
            
            
            # normalize fitness, so random.choices has the right weights
            total_high_fitness = sum(x[1] for x in high_performers)
            total_low_fitness = sum(x[1] for x in low_performers)
            normalized_high_performers = [[i[0], i[1]/float(total_high_fitness)] for a in high_performers]
            normalized_low_performers = [[i[0], i[1]/float(total_low_fitness)] for a in low_performers]


            # calculate number of bots to mutate/cross over. cross over count must be even
            mutate_count = round(mutation_percent * len(gen_results))
            cross_over_count = len(gen_results) - mutate_count
            if cross_over_count % 2 != 0:
                if mutate_count == 0:
                    cross_over_count -= 1
                    mutate_count += 1
                else:
                    cross_over_count += 1
                    mutate_count -= 1
            
            
            # allow for storing new bots in previous gen_results
            # now includes copying files
            normalized_high_performers = copy.deepcopy(normalized_high_performers)
            normalized_low_performers = copy.deepcopy(normalized_low_performers)
            for tree in normalized_high_performers:
                file_name = tree[0]
                new_file_name = "COPY"+file_name
                copyfile(file_name, new_file_name)
                tree[0] = new_file_name
            for tree in normalized_low_performers:
                file_name = tree[0]
                new_file_name = "COPY"+file_name
                copyfile(file_name, new_file_name)
                tree[0] = new_file_name


            #set rate of selecting high performers
            high_performer_sample_rate = 0.8
            
            
            # mutate bots
            for i in range(mutate_count):
                #pick whether to take a high or low performer, then pick one of them, then strip lists
                bot_to_mutate = random.choices([random.choices(normalized_high_performers, 
                                                               weights = (a[1] for a in normalized_high_performers)),
                                                random.choices(normalized_low_performers, 
                                                               weights = (a[1] for a in normalized_low_performers))], 
                                               weights = [high_performer_sample_rate, 1-high_performer_sample_rate])[0][0][0]
                bot_to_replace = gen_results.pop()[0] #we shouldn't be looking at gen_results any more
                mutate_bot(bot_to_mutate, bot_to_replace, operator_probability)


            # Cross over bots
            for i in range(cross_over_count // 2):
                bot1_to_cross_over = random.choices([random.choices(normalized_high_performers, 
                                                               weights = (a[1] for a in normalized_high_performers)),
                                                random.choices(normalized_low_performers, 
                                                               weights = (a[1] for a in normalized_low_performers))], 
                                               weights = [high_performer_sample_rate, 1-high_performer_sample_rate])[0][0][0]
                bot2_to_cross_over = random.choices([random.choices(normalized_high_performers, 
                                                               weights = (a[1] for a in normalized_high_performers)),
                                                random.choices(normalized_low_performers, 
                                                               weights = (a[1] for a in normalized_low_performers))], 
                                               weights = [high_performer_sample_rate, 1-high_performer_sample_rate])[0][0][0]
                bot1_to_replace = gen_results.pop()[0]
                bot2_to_replace = gen_results.pop()[0]
                cross_over(bot1_to_cross_over, bot2_to_cross_over, bot1_to_replace, bot2_to_replace)
                
            
            #Get rid of orphaned files
            for tree in normalized_high_performers:
                file_name = tree[0]
                remove(file_name)
            for tree in normalized_low_performers:
                file_name = tree[0]
                remove(file_name)

# t = Trainer(8, 'new_bot')
# t.train(mutation_percent=.75, generations=3, games_per_bot=2, fast_count=3, bots_per_sim=4)
# print(t.results)





