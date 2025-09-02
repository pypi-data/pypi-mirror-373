"""
# htmlmaster
Provides tools for making html.

## Usage
### Make an html table

```py
>>> from repo.htmlmaster import src as hm

>>> table = hm.HTMLTableMaker(index=[1, 2], columns=["foo", "bar"])
>>> table[0, 0] = "this"
>>> table[0, 1] = "is"
>>> table[1, 0] = "a"
>>> table[1, 1] = "table"

>>> table.make()
'<table
class="main">
<thead>
<tr>
<th>foo</th>
<th>bar</th>
</tr>
</thead>
<tbody>
<tr>
<td>this</td>
<td>is</td>
</tr>
<tr>
<td>a</td>
<td>table</td>
</tr>
</tbody>
</table>'
```

If you are using a jupyter notebook, you can run a cell like this:

```py
>>> table.show()
```
<table class="main">
<thead>
<tr>
<th>foo</th>
<th>bar</th>
</tr>
</thead>
<tbody>
<tr>
<td>this</td>
<td>is</td>
</tr>
<tr>
<td>a</td>
<td>table</td>
</tr>
</tbody>
</table>


### Make an html tree

```py
>>> tree = hm.HTMLTreeMaker("this")
>>> tree.add("is")
>>> tree.add("a")
>>> tree.get(-1).add("tree")

>>> tree.make()
'<ul class="main">
<li class="m"><details open><summary>this</summary>
<ul
class="m">
<li class="m"><span>is</span></li>
<li class="m"><details
open><summary>a</summary>
<ul class="m">
<li
class="m"><span>tree</span></li>
</ul>
</details></li>
</ul>
</details></li>
</ul>'
```

If you are using a jupyter notebook, you can run a cell like this:

```py
>>> tree.show()
```
<ul class="main">
<li class="m"><details open><summary>this</summary>
<ul class="m">
<li class="m"><span>is</span></li>
<li class="m"><details open><summary>a</summary>
<ul class="m">
<li class="m"><span>tree</span></li>
</ul>
</details></li>
</ul>
</details></li>
</ul>

## See Also
### Github repository
* https://github.com/Chitaoji/htmlmaster/

### PyPI project
* https://pypi.org/project/htmlmaster/

## License
This project falls under the BSD 3-Clause License.

"""

from . import core
from ._version import __version__
from .core import *

__all__: list[str] = []
__all__.extend(core.__all__)
