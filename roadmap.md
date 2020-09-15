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
>>> table = get_acs(state="CO", variable="D06_001", view_by=bbd.COUNTY)
>>> pprint(table)
{
    "GEOID": [...]
    "NAME": [...]
    "D06_001E": [...]
    "D06_001M": [...]
}
```

Worth noting that whenever calls are made to big tables they (can be | are by default) cached into some set working directory (perhaps defaults to home).

TODO finish this up...

User could also make a map with those same inputs

User could make a map with the get_acs() table and their own shapefiles if they wanted.

