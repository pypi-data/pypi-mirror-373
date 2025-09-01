import os
import seaborn as sns
import matplotlib as mpl
from datetime import date
from rendu.htmldeck import HtmlSlideDeck

# ----------------------------------------------- #
# Use pandas/seaborn to perform some data analysis
# ----------------------------------------------- #
os.makedirs('./tmp', exist_ok=True)
mpl.use('AGG')
penguins = sns.load_dataset('penguins')
fig = sns.displot(penguins, x='flipper_length_mm')
fig.savefig('./tmp/penguins_histogram.png')
flen_ave = penguins.flipper_length_mm.mean().round(2)
flen_med = penguins.flipper_length_mm.median().round(2)
flen_std = penguins.flipper_length_mm.std().round(2)
penguins.to_csv('./tmp/penguins.csv')

# ------------------------------------------------------ #
# Now use rendu to quickly assemble an HTML presentation
# ------------------------------------------------------ #

# Create HTML report
rep = HtmlSlideDeck(f'Analysis Of Penguin Population [{date.today()}]',
                    footer='University Of Penguinia, dept. of Marine Science')

# Add intro slide
s = rep.add_slide(0, "Penguin Study Report", "Intro")
s.main.add_h2('Data Sources')
s.main.add_ul(['Raw data available at seaborn-data repository',
               'https://github.com/mwaskom/seaborn-data'])
s.main.add_h2('Disclaimer')
s.main.add_p('NO PENGUINS WERE HARMED FOR THIS STUDY')
s.side.add_h2('Authors')
s.side.add_ul(['John Doe, PhD', 'Jane Doe, PhD'])

# Add slide with histogram with stats
s = rep.add_slide(1, "Flipper Length Distribution", "Flipper Length")

# Add figure to main layout
s.main.add_figure('./tmp/penguins_histogram.png')

# Add more info to side layout
s.side.add_h2('Main Stats')
s.side.add_ul([f'Average: {flen_ave}',
               f'Median: {flen_med}',
               f'Std: {flen_std}'])

# Add slide that embeds raw data
s = rep.add_raw_data_slide(2, "Raw Data", "Raw Data", './tmp/penguins.csv')

# Save report
rep.save('./tmp/penguin_report.html')

