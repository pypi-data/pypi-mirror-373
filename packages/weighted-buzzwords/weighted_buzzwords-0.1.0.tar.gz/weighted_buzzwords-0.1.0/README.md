# Plotting


# Weighted-buzzwords

## Buzzwords

``` python
buzzWords={ f"buzzword with weight {i}":i 
    for i in map(lambda x:x**2//3+x+5,range(15)) 
}

buzzWords
```

    {'buzzword with weight 5': 5,
     'buzzword with weight 6': 6,
     'buzzword with weight 8': 8,
     'buzzword with weight 11': 11,
     'buzzword with weight 14': 14,
     'buzzword with weight 18': 18,
     'buzzword with weight 23': 23,
     'buzzword with weight 28': 28,
     'buzzword with weight 34': 34,
     'buzzword with weight 41': 41,
     'buzzword with weight 48': 48,
     'buzzword with weight 56': 56,
     'buzzword with weight 65': 65,
     'buzzword with weight 74': 74,
     'buzzword with weight 84': 84}

``` python
from weighted_buzzwords.valuedbuzzwords import valued_buzzwords



valued_buzzwords(buzzWords)
```

![](README_files/figure-commonmark/cell-3-output-1.png)

``` python
valued_buzzwords(buzzWords,min_font=12,max_font=300)
```

![](README_files/figure-commonmark/cell-4-output-1.png)

``` python
valued_buzzwords(buzzWords,min_font=12,max_font=300, figsize=(25,4))
```

![](README_files/figure-commonmark/cell-5-output-1.png)

``` python
valued_buzzwords(buzzWords,min_font=12,max_font=300, figsize=(25,4),stretch=4)
```

![](README_files/figure-commonmark/cell-6-output-1.png)

``` python
valued_buzzwords(buzzWords,min_font=12,max_font=300, figsize=(25,4),stretch=4,cmap="jet")
```

![](README_files/figure-commonmark/cell-7-output-1.png)
