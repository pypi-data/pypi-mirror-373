<h1 align="center">
  Fused Public Python package
</h1>
<h3 align="center">
  🌎 Code to Map. Instantly.
</h3>
<br><br>

**Fused** is a Python library to code, scale, and ship geospatial workflows of any size. Express workflows as shareable UDFs (user defined functions) without thinking about the underlying compute. The Fused Python library is maintained by [Fused.io](https://fused.io).

## Prerequisites

Python >= 3.10

## Install

```
pip install fused
```

## Quickstart

```python3
import fused

# Declare UDF
@fused.udf()
def my_udf():
    import pandas as pd
    return pd.DataFrame({'hello': ['world']})

df = fused.run(my_udf)
print(df)

dc_file_udf = fused.load('https://github.com/fusedio/udfs/tree/main/public/DC_File_Example')

df2 = fused.run(dc_file_udf)
print(df2)
```

## Resources

- [Open source UDF catalog](https://github.com/fusedio/udfs/tree/main)
- [Fused Discord community](https://discord.com/invite/BxS5wMzdRk)
- [LinkedIn](https://www.linkedin.com/company/fusedio)

## Changelog
See the [changelog](https://docs.fused.io/python-sdk/changelog/) for the latest changes.
