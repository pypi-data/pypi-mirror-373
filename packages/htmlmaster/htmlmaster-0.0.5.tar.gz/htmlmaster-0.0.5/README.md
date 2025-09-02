# htmlmaster
Provides tools for making html.

## Installation
```sh
$ pip install htmlmaster
```


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
'<table class="main">\n<thead>\n<tr>\n<th>foo</th>\n<th>bar</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>this</td>\n<td>is</td>\n</tr>\n<tr>\n<td>a</td>\n<td>table</td>\n</tr>\n</tbody>\n</table>'
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
'<ul class="main">\n<li class="m"><details open><summary>this</summary>\n<ul class="m">\n<li class="m"><span>is</span></li>\n<li class="m"><details open><summary>a</summary>\n<ul class="m">\n<li class="m"><span>tree</span></li>\n</ul>\n</details></li>\n</ul>\n</details></li>\n</ul>'
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

## History
### v0.0.5
* Bugfix for the argument parsing of `HTMLTreeMaker.addspan()`.

### v0.0.4
* Fixed a bug occured when specifying `value=None` for `HTMLTreeMaker()`.

### v0.0.3
* New method for `HTMLTreeMaker`: `*.addspan()`, `*.addval()`.
* Removed methods from `HTMLTreeMaker`: `*.setstyle()`, `*.getstyle()`


### v0.0.2
* New methods for `HTMLMaker`: `*.setrootstyle()`, `*.getrootstyle()`, `*.setrootcls()`, `*.getrootcls()`.
* Removed methods from `HTMLMaker`: `*.set_maincls()`, `*.get_maincls()`.

### v0.0.1
* Initial release.