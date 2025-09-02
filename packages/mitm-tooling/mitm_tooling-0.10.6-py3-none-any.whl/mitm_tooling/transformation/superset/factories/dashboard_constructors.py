from collections.abc import Callable, Iterable

from mitm_tooling.transformation.superset.definitions import DashboardComponent, DashboardPositionData, SupersetChartDef

DashElementCallable = Callable[[], tuple[list[DashboardComponent], list[DashboardComponent]]]
DashCallable = Callable[[], DashboardPositionData]


# noinspection PyPep8Naming
def GRID(grid: Iterable[Iterable[DashElementCallable]]) -> DashElementCallable:
    from .dashboard import put_in_rows

    def f():
        out_grid, acc = [], []
        for row in grid:
            out_row = []
            for func in row:
                a, b = func()
                out_row.extend(a)
                acc.extend(b)
            out_grid.append(out_row)
        out_rows, inner_acc = put_in_rows(out_grid)
        acc.extend(inner_acc)
        return out_rows, acc

    return f


# noinspection PyPep8Naming
def ROW(*args: DashElementCallable) -> DashElementCallable:
    return GRID([args])


# noinspection PyPep8Naming
def COL_GROUP(*args: tuple[int, Iterable[DashElementCallable]]) -> DashElementCallable:
    return ROW(COLS(*args))


# noinspection PyPep8Naming
def COLS(*args: tuple[int, Iterable[DashElementCallable]]) -> DashElementCallable:
    from .dashboard import put_in_columns

    def f():
        acc, out_cols = [], []
        for w, funcs in args:
            out_row = []
            for func in funcs:
                a, b = func()
                acc.extend(b)
                out_row.extend(a)
            out_cols.append((w, out_row))
        cols, inner_acc = put_in_columns(out_cols)
        acc.extend(inner_acc)
        return cols, acc

    return f


# noinspection PyPep8Naming
def TABS(tabs: dict[str, list[DashElementCallable]]) -> DashElementCallable:
    from .dashboard import put_in_tabs

    def f():
        acc, out_cols = [], []  # noqa: F841
        out_tabs = {}
        for k, funcs in tabs.items():
            out_tab_contents = []
            for func in funcs:
                a, b = func()
                acc.extend(b)
                out_tab_contents.extend(a)
            out_tabs[k] = out_tab_contents
        tabs_, inner_acc = put_in_tabs(out_tabs)
        acc.extend(inner_acc)
        return [tabs_], acc

    return f


# noinspection PyPep8Naming
def WRAP(c: DashboardComponent) -> DashElementCallable:
    return lambda: ([c], [])


# noinspection PyPep8Naming
def CHART(chart: SupersetChartDef, w: int = 3, h: int = 50) -> DashElementCallable:
    from .dashboard import chart_to_def

    return WRAP(chart_to_def(chart, width=w, height=h))


# noinspection PyPep8Naming
def HEADER(title: str) -> DashElementCallable:
    from .dashboard import mk_dashboard_header

    return WRAP(mk_dashboard_header(title))


# noinspection PyPep8Naming
def MARKDOWN(text: str, w: int = 3, h: int = 50) -> DashElementCallable:
    from .dashboard import mk_dashboard_markdown

    return WRAP(mk_dashboard_markdown(text, width=w, height=h))


# noinspection PyPep8Naming
def DASH(title: str, *rows: DashElementCallable) -> DashCallable:
    from .dashboard import mk_dashboard_position_data

    def f():
        out_rows, acc = [], []
        for row in rows:
            a, b = row()
            acc.extend(b)
            out_rows.extend(a)
        return mk_dashboard_position_data(title, out_rows, acc)

    return f


def construct(f: DashCallable) -> DashboardPositionData:
    return f()
