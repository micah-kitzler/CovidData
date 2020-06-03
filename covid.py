import requests
import json
import pandas
import matplotlib


url = "https://covidtracking.com/api/states/daily"
data = pandas.json_normalize(requests.get(url = url, params = {}).json())

data['date'] = pandas.to_datetime(data['date'], format='%Y%m%d')
data = data[data['date'] >= pandas.Timestamp('2020-03-04')]
#data = data.set_index(['date','state'])

Georgia = data[data['state']=='GA']
Georgia = Georgia.set_index('date')
Georgia = Georgia.groupby('date').sum()

NewYork = data[data['state']=='NY']
NewYork = NewYork.set_index('date')
NewYork = NewYork.groupby('date').sum()

##Florida = data[data['state']=='PA']
##Florida = Florida.set_index('date')
##Florida = Florida.groupby('date').sum()
##
##Washington = data[data['state']=='WV']
##Washington = Washington.set_index('date')
##Washington = Washington.groupby('date').sum()

National = data.groupby('date').sum()

NotNY = National-NewYork

Georgia['positive'].plot(legend=True)
Georgia['total'].plot(legend=True)
matplotlib.pyplot.title('Georgia Testing')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()

NewYork['positive'].plot(legend=True)
NewYork['total'].plot(legend=True)
matplotlib.pyplot.title('New York Testing')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()


National['positive'].plot(legend=True)
National['total'].plot(legend=True)
matplotlib.pyplot.title('National Testing')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()

change = National.diff(axis=0)
GaChange = Georgia.diff(axis=0)
change['positive'].rolling(3).mean().plot(legend=True)
change['total'].rolling(3).mean().plot(legend=True)
GaChange['positive'].rolling(3).mean().plot(legend=True, secondary_y = True)
GaChange['total'].rolling(3).mean().plot(legend=True, secondary_y = True)
matplotlib.pyplot.title('National and Georgia Positive and Total Testing')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()

NYChange = NewYork.diff(axis=0)
change['positive'].rolling(3).mean().plot(legend=True)
change['total'].rolling(3).mean().plot(legend=True)
NYChange['positive'].rolling(3).mean().plot(legend=True, secondary_y = True)
NYChange['total'].rolling(3).mean().plot(legend=True, secondary_y = True)
matplotlib.pyplot.title('National and New York Positive and Total Testing')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()

##NotNYChange = NotNY.diff(axis=0)
##NotNYChange['positive'].plot(legend=True)
##NotNYChange['total'].plot(legend=True)
##NYChange['positive'].plot(legend=True, secondary_y = True)
##NYChange['total'].plot(legend=True, secondary_y = True)
##matplotlib.pyplot.title('New York and Rest Positive and Total Testing')
##matplotlib.pyplot.grid(b=True)
##matplotlib.pyplot.show()

change['national_pct_positive'] = change['positive']/change['total']
GaChange['GA_pct_positive'] = GaChange['positive']/GaChange['total']
NYChange['NY_pct_positive'] = NYChange['positive']/NYChange['total']
change['national_pct_positive'].rolling(3).mean().plot(legend=True)
GaChange['GA_pct_positive'].rolling(3).mean().plot(legend=True)
NYChange['NY_pct_positive'].rolling(3).mean().plot(legend=True)
matplotlib.pyplot.title('Percent Positive Tests Nationaly and in Georgia')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()

National['positive'].diff().rolling(28, min_periods=1).sum().plot(legend=True, label='National')
Georgia['positive'].diff().rolling(28, min_periods=1).sum().plot(legend=True, label='GA')
NewYork['positive'].diff().rolling(28, min_periods=1).sum().plot(legend=True, label='NY')
NotNY['positive'].diff().rolling(28, min_periods=1).sum().plot(legend=True, label='Not NY')
matplotlib.pyplot.title('Total Active Cases')
matplotlib.pyplot.grid(b=True)
matplotlib.pyplot.show()

##change = National.pct_change(axis=0)
##GaChange = Georgia.pct_change(axis=0)
##change['positive'].plot(legend=True)
###change['total'].plot(legend=True)
##GaChange['positive'].plot(legend=True)
###GaChange['total'].plot(legend=True, secondary_y = True)
##matplotlib.pyplot.legend(['National','GA'])
##matplotlib.pyplot.ylim(top=1.0, bottom=0.0)
##matplotlib.pyplot.title('Percent Change Nationaly and in Georgia')
##matplotlib.pyplot.grid(b=True)
##matplotlib.pyplot.show()
##
##change = National.pct_change(axis=0)
##NYChange = NewYork.pct_change(axis=0)
##change['positive'].plot(legend=True)
##NYChange['positive'].plot(legend=True)
##matplotlib.pyplot.legend(['National','NY'])
##matplotlib.pyplot.ylim(top=1.0, bottom=0.0)
##matplotlib.pyplot.title('Percent Change Nationaly and in New York')
##matplotlib.pyplot.grid(b=True)
##matplotlib.pyplot.show()
##
##NotNYChange = NotNY.pct_change(axis=0)
##NotNYChange['positive'].plot(legend=True)
##NYChange['positive'].plot(legend=True)
##matplotlib.pyplot.legend(['National','NY'])
##matplotlib.pyplot.ylim(top=1.0, bottom=0.0)
##matplotlib.pyplot.title('Percent Change in New York and elsewhere')
##matplotlib.pyplot.grid(b=True)
##matplotlib.pyplot.show()
##
###FLChange = Florida.pct_change(axis=0)
###WAChange = Washington.pct_change(axis=0)
###FLChange['positive'].plot(legend=True)
###WAChange['positive'].plot(legend=True)
###matplotlib.pyplot.legend(['FL','WA'])
###matplotlib.pyplot.ylim(top=1.0, bottom=0.0)
###matplotlib.pyplot.title('Percent Change in Florida and in Washington')
###matplotlib.pyplot.grid(b=True)
###matplotlib.pyplot.show()
##
##USavg = change['positive'].rolling(7).mean()
##USstd = change['positive'].rolling(7).std()
##USavg.plot()
##matplotlib.pyplot.fill_between(USstd.index, USavg-2*USstd, USavg+2*USstd, alpha = 0.2)
##matplotlib.pyplot.title('National Percent Change with Error Margin (7 Day Rolling Avg)')
##matplotlib.pyplot.grid(b=True)
##matplotlib.pyplot.show()

