import pandas as pd
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description='Process a CSV file and remove duplicates.')
parser.add_argument('--filename', type=str, default='books_list.csv', help='CSV file to process')
args = parser.parse_args()

# Read the CSV file based on the argument
df = pd.read_csv(args.filename)

# Remove duplicates
df_cleaned = df.drop_duplicates(subset='link', keep='first')

# Save the cleaned data to the same file
df_cleaned.to_csv(args.filename, index=False)
