# htmlstr

HTML structured (the "str" stands for "structured"). Balanced for interactivity and written content.

The parser will keep everything as concise as possible.

```python
from htmlstr import Parser

parser = Parser()
elements = parser.parse("<button>Hello!</button>")

print(elements)
```


```python
[
    Button(
        id=0, 
        inner=[
            Text(content='Hello!')
        ]
    )
]
```

***

(c) 2025 AWeirdDev
