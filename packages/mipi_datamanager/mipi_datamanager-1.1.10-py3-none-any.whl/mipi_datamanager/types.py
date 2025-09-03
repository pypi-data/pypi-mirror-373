from typing import Literal, LiteralString
import pandas as pd

type JoinLiterals = Literal["left", "right", "inner", "outer", "cross"]
type BuildLiterals = LiteralString["Config", "Jinja", "SQL", "Format SQL", "Data Frame", "Excel"]
type Mask = pd.Series[bool]
