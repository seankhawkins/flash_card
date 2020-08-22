import pandas as pd
import numpy as np 
from datetime import datetime, timedelta

# Algorithm based on: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2

interval_dict = {}


# Calculates new easiness factor based on previous value and quality score (ease of identification)
def calc_new_ef(prev_ef, quality):
    return max(1.3, prev_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))


# Calculates next date to review based on interval value and easiness factor
def calc_new_target_range(ef, interval):
    if interval == 1:
        return 1
    elif interval == 2:
        return 6
    else:
        try:
            return interval_dict[interval - 1] * ef
        except:
            prev_value = calc_new_target_range(ef, interval - 1) 
            interval_dict[interval - 1] = prev_value
            return prev_value * ef


# Read in vocabulary from csv
vocab_df = pd.read_csv('vocab.csv')

# Set new words' target date to today (SHOULD IT BE PREVIOUS?)
vocab_df['Target Date'].fillna(datetime.now(), inplace=True)

# WANT TO GO UNTIL EVERYTHING REACHES 4 
# Go through vocabulary 
for index, row in vocab_df.iterrows():
    # If date has passed 
    if datetime.strptime(row['Target Date'], '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
        quality = 3

        # Quality determined by the speed of recall 
        try: 
            # Quality must be an integer between 0 and 5
            print(row['English'])
            input()
            print(row['Italian'] + ': ' + row['Pronunciation'])
            quality_string = input('Quality: ')
            if quality_string == 'quit':
                break
            quality = int(quality_string)
            if quality > 5 or quality < 0:
                continue
        except:
            continue 

        # If unable to identify, reset interval and target date (to now)
        if quality < 3:
            vocab_df.at[index, 'Interval'] = 1
            vocab_df.at[index, 'Target Date'] = datetime.now()
        # If remembered, update EF, target date, and interval 
        else: 
            # Update EF
            updated_ef = calc_new_ef(row['EF'], quality)
            vocab_df.at[index, 'EF'] = updated_ef

            # Update target date 
            updated_target_range = calc_new_target_range(updated_ef, vocab_df.at[index, 'Interval'])
            vocab_df.at[index, 'Target Date'] = datetime.now() + timedelta(hours=updated_target_range)

            # Update interval 
            vocab_df.at[index, 'Interval'] = row['Interval'] + 1

# Save results 
print("No (more) words to review!")
vocab_df.to_csv('vocab.csv', index=False)
