"""
Contains css styles.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

__all__ = []

TREE_CSS_STYLE = """<style type="text/css">
.{0} li.m {{
    display: block;
    position: relative;
    padding-left: 2.5rem;
}}
.{0} li.t,
.{0} li.i {{
    display: block;
    position: relative;
    padding-left: 0;
}}
.{0} li.i>span {{
    border: solid .1em #666;
    border-radius: .2em;
    display: inline-block;
    margin-top: .5em;
    padding: .2em .5em;
    position: relative;
}}
.{0} li>details>summary>span.open,
.{0} li>details[open]>summary>span.closed {{
    display: none;
}}
.{0} li>details[open]>summary>span.open {{
    display: inline;
}}
.{0} li>details>summary {{
    display: block;
    cursor: pointer;
}}
.{0} ul {{
    display: table;
    padding-left: 0;
    margin-left: 0;
}}
</style>
"""
