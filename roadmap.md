# Objective
The objective of this library is to make getting and visualizing census data an easy process for the user. If the user wants something more advanced, they will probably need to dowrite some of their own mapping / coloring methods.

We want for this library to "just work" and be a *really good* starting place for working with census data.

## Noah's ideal workflow

This is Noah's idea of an ideal workflow.

First, you'd want to explore the data available to you. For this, you'd need to specify the geography that you are interested in and how you would want the data broken down. 

```python
>>> import bbd
>>>
>>> vars = bbd.explore_acs(state="CO", view_by=bbd.COUNTY)
found 1560 variables for the state of Colorado, broken down by county

Variable Name		Variable Label		Variable Description
---------------------------------------------------------------------
D06_001			Med. Household Income	Median Household Income
...			...			...
...			...			...
```

Ideally, it'd be nice to not specify how you want it broken down and instead have the table spit out ALL info available, with another column describing which level the data is available at.

This is likely going to be a lot of information (a lot of rows in the table). Seems like you would get a lot of utility out of adding some kind of "search" or "lookup" function.

```python
>>> # The following will only display rows with a label that
>>> # contains "income"
>>> vars.search("income")
found 5/1560 variables matching "income" for the state of Colorado, 
broken down by county

Variable Name		Variable Label		Variable Description
---------------------------------------------------------------------
D06_001			Med. Household Income	Median Household Income
...			...			...
...			...			...
```


You would use this search function to find the relevant variable that you want, and be confident that there is data for it at the level and geography you are interested in.

Now that we know which variable (or variables) we are interested in, you have a few options. For example, you might want to simply tabulate that census variable.

```python
>>> from pprint import pprint
>>>
>>> table = bbd.get_acs(state="CO", variable="D06_001", view_by=bbd.COUNTY)
>>> pprint(table)
{
    "GEOID": [...]
    "NAME": [...]
    "D06_001E": [...]
    "D06_001M": [...]
}
```

Worth noting that whenever calls are made to big tables they (can be | are by default) cached into some set working directory (perhaps defaults to home). Same goes for the shapefiles that get pulled and unzipped from the census ftp.

Once the user has this data cached, they've taken a look at the table and know it's good stuff, they should be able to make a map using the same inputs.

```python
>>> table = bbd.make_acs_map(state="CO", variable="D06_001", view_by=bbd.COUNTY, save_to="map.html")
>>> # This method should grab the same data as 'get_acs', and also pull
>>> # the relevant shapefiles from the census ftp. (There is already a method
>>> # to grab and unzip shapefiles from that site.) Then it'll simply join
>>> # the data table with the shapefile on the GEOID and generate a leaflet
>>> # map with 'make_map'
```

Of course, if the user wanted to they could also call `make_map` on their own if they had specific processing they wanted to first do with either the shapefiles or the data

```python
>>> table = bbd.get_acs(...)
>>> # process table
>>>
>>> shapefile_path = bbd.get_shapefiles(...)
>>> # process shapefiles
>>>
>>> bbd.make_map(table, shapefile_path, "map.html")
```

